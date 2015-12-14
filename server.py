import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado import gen
import math
import tornado
import gdal
from helpers import TileSampler, CoordSystem
import json
from geojson import Feature, Point
import geojson
from algo import generate_line_segments, generate_visible, iter_to_runs

PORT = 8888
ZOOM = 12

class ApiHandler(tornado.web.RequestHandler):

    def write_geojson(self, obj):
        self.set_header("Content-Type", "application/vnd.geo+json")
        self.write(geojson.dumps(obj))

    def write_json(self, obj):
        self.set_header("Content-Type", "application/javascript")
        self.write(json.dumps(obj))

    def write_error(self, status_code, exc_info=None, **kwargs):
        errortext = 'Internal error'
        if exc_info:
            errortext = getattr(exc_info[1], 'log_message', errortext)
        self.write_json({'status' : 'error',
                             'code' : status_code,
                             'reason' : errortext})

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
        self.write_geojson(Feature(geometry=Point(lnglat), properties={
            "elevation":float(value)
        }))

class ShedHandler(ApiHandler):
    @gen.coroutine
    def get(self, lng, lat, altitude, radius):
        try:
            lng, lat, altitude, radius = map(float, (lng, lat, altitude, radius))
        except Exception:
            raise tornado.web.HTTPError(400)
        print 'Getting elevation at lng: {}, lat: {}, altitude: {}, radius:{}'.format(lng, lat, altitude, radius)
        center = CoordSystem.lnglat_to_pixel((lng, lat))
        sampler = TileSampler()
        for start, stop in generate_line_segments(radius, center):
            elevations, pixels = yield sampler.sample_line(start, stop)
            ret = iter_to_runs(generate_visible(altitude, elevations), pixels)
        self.write_json(ret)


application = tornado.web.Application([
    (r"/elevation/(-?\d+\.?\d*)/(-?\d+\.?\d*)", ElevationHandler),
    (r"/shed/(-?\d+\.?\d*)/(-?\d+\.?\d*)/(\d+\.?\d*)/(\d+\.?\d*)", ShedHandler),
])

if __name__ == "__main__":
    application.listen(PORT)
    print 'listening on port %s' % PORT
    tornado.ioloop.IOLoop.current().start()
