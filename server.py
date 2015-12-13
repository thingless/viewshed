import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado import gen
import dict2xml
import math
import tornado
import gdal
from helpers import TileSampler, CoordSystem

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

class ElevationHandler(ApiHandler):
    @gen.coroutine
    def get(self, lng, lat):
        print 'Getting elevation at lng, lat: %s, %s' % (lng, lat)
        try:
            lnglat = map(float, (lng, lat))
        except Exception:
            raise tornado.web.HTTPError(400)
        sampler = TileSampler()
        pixel = CoordSystem.lnglat_to_pixel(lnglat)
        value = yield sampler.sample_pixel(pixel)
        lnglat = CoordSystem.pixel_to_lnglat(pixel)
        self.write_response({
            "elevation": value,
            "pixel_coords": {"x": pixel[0], "y": pixel[1]},
            "geo_coords": {"latitude": lnglat[1], "longitude": lnglat[0]},
        })

application = tornado.web.Application([
    (r"/elevation/(-?\d+\.?\d*)/(-?\d+\.?\d*)", ElevationHandler),
])

if __name__ == "__main__":
    application.listen(PORT)
    print 'listening on port %s' % PORT
    tornado.ioloop.IOLoop.current().start()
