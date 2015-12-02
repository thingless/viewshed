import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado import gen
import dict2xml
import math
import tornado
import gdal

TILE_HOST = "http://127.0.0.1:8080"
PORT = 8888
ZOOM = 12

class ApiHandler(tornado.web.RequestHandler):
    def get_format(self):
        format = self.get_argument('format', None)
        if not format:
            accept = self.request.headers.get('Accept')
            if accept:
                if 'javascript' in accept:
                    format = 'jsonp'
                elif 'json' in accept:
                    format = 'json'
                elif 'xml' in accept:
                    format = 'xml'
        return format or 'json'

    def write_response(self, obj, nofail=False):
        format = self.get_format()
        if format == 'json':
            self.set_header("Content-Type", "application/javascript")
            self.write(json.dumps(obj))
        elif format == 'jsonp':
            self.set_header("Content-Type", "application/javascript")
            callback = self.get_argument('callback', 'callback')
            self.write('%s(%s);'%(callback, json.dumps(obj)))
        elif format == 'xml':
            self.set_header("Content-Type", "application/xml")
            self.write('<response>%s</response>'%dict2xml.dict2xml(obj))
        elif nofail:
            self.write(json.dumps(obj))
        else:
            raise tornado.web.HTTPError(400, 'Unknown response format requested: %s'%format)

    def write_error(self, status_code, exc_info=None, **kwargs):
        errortext = 'Internal error'
        if exc_info:
            errortext = getattr(exc_info[1], 'log_message', errortext)

        self.write_response({'status' : 'error',
                             'code' : status_code,
                             'reason' : errortext},
                            nofail=True)

class CoordSystem(object):
    @classmethod
    def lnglat_to_pixel(cls, lnglat, zoom=ZOOM):
        lng, lat = lnglat
        lat *= math.pi / 180.0
        lng *= math.pi / 180.0
        x = 128.0 / math.pi * 2**zoom * (lng + math.pi)
        y = 128.0 / math.pi * 2**zoom * (math.pi - math.log(math.tan(math.pi / 4.0 + lat / 2.0)))
        #print lnglat, '->', (x,y), '->', (x//256,y//256)
        return round(x), round(y)

    @classmethod
    def lnglat_to_tile(cls, lnglat, zoom=ZOOM):
        r = cls.lnglat_to_pixel(lnglat, zoom)
        return (int(r[0]//256), 2**zoom - int(r[1]//256) - 1)

    @classmethod
    def pixel_to_lnglat(cls, point, zoom=ZOOM):
        x, y = point
        lat = (4.0 * math.atan(math.exp(math.pi - y * math.pi / (128.0 * 2**zoom))) - math.pi) / 2.0
        lng = x * math.pi / (128.0 * 2**zoom) - math.pi
        lat *= 180.0 / math.pi
        lng *= 180.0 / math.pi
        return lng, lat

def load_float32_image(buffer):
    try:
        gdal.FileFromMemBuffer('/vsimem/temp', buffer)
        ds = gdal.Open('/vsimem/temp')
        channel = ds.GetRasterBand(1).ReadAsArray()
        ds = None #cleanup
        gdal.Unlink('/vsimem/temp') #cleanup
        return channel
    except Exception, e:
        ds = None #cleanup
        gdal.Unlink('/vsimem/temp') #cleanup
        raise e

class ElevationHandler(ApiHandler):
    @gen.coroutine
    def get(self, lng, lat):
        print 'Getting elevation at lng, lat: %s, %s' % (lng, lat)
        try:
            lnglat = map(float, (lng, lat))
        except Exception:
            raise tornado.web.HTTPError(400)
        tile = CoordSystem.lnglat_to_tile(lnglat)
        http_client = AsyncHTTPClient()
        tile_url = TILE_HOST+"/{z}/{x}/{y}.tiff".format(z=ZOOM, x=tile[0], y=tile[1])
        response = yield http_client.fetch(tile_url)
        if response.code != 200:
            raise tornado.web.HTTPError(response.code)
        im = load_float32_image(response.body)
        pixel = [int(round(i)) % 256 for i in CoordSystem.lnglat_to_pixel(lnglat, ZOOM)]
        value = im[pixel[1], pixel[0]] #numpy is row,col
        self.write_response({
            "elevation": value,
            "pixel_coords": {"x": pixel[0], "y": pixel[1]},
            "tile": {"x": tile[0], "y": tile[1], "zoom": ZOOM, "url": tile_url},
            "geo_coords": {"latitude": lat, "longitude": lng},
        })

application = tornado.web.Application([
    (r"/elevation/(-?\d+\.?\d*)/(-?\d+\.?\d*)", ElevationHandler),
])

if __name__ == "__main__":
    application.listen(PORT)
    print 'listening on port %s' % PORT
    tornado.ioloop.IOLoop.current().start()
