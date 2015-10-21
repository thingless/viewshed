import tornado.ioloop
import tornado.web
from tornado import gen
from PIL import Image
import math
import tornado

TILE_HOST = "http://127.0.0.1"

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
  R = 6378137
  MAX_LATITUDE = 85.0511287798
  @classmethod
  def latlng_to_pixel(cls, latlng):
    d = math.pi / 180.0,
    max = self.MAX_LATITUDE,
    lat = math.max(math.min(max, latlng[0]), -max),
    sin = math.sin(lat * d);
    return (self.R * latlng[1] * d, self.R * math.log((1.0 + sin) / (1.0 - sin)) / 2.0)
  @classmethod
  def latlng_to_tile(cls, latlng):
    r = cls.latlng_to_pixel(latlng)
    return (r[0]/256.0, r[1]/256.0)
  @classmethod
  def pixel_to_latlng(cls, point):
    d = 180.0 / math.pi
    return ((2.0 * math.atan(math.exp(point[1] / self.R)) - (math.pi / 2.0)) * d,
      point[0] * d / self.R))


class ElevationHandler(ApiHandler):
  @gen.coroutine
  def get(self, lat, lng):
    try:
      latlng = map(float, (lat, lat))
    except Exception:
      raise tornado.web.HTTPError(400)
    tile = CoordSystem.latlng_to_tile(latlng)
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(TILE_HOST+"/{z}/{x}/{y}.tif".format(z=12, x=tile[0], y=tile[1]))
    if response.code != 200:
      raise tornado.web.HTTPError(response.code)
    im = Image.open(response.buffer)
    pixel = [int(round(i))%255 for i in pixel = CoordSystem.latlng_to_pixel(latlng)]
    value = im[pixel[0], pixel[1]]
    im = None
    self.write_response({"value":im})

application = tornado.web.Application([
  (r"/(\d+\.?\d*)/(\d+\.?\d*)", ElevationHandler),
])

if __name__ == "__main__":
  application.listen(8888)
  tornado.ioloop.IOLoop.current().start()