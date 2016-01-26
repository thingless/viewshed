#!/usr/bin/env python
import tornado.ioloop
import tornado.web
from tornado import gen
import tornado
from tornado.options import define, options
from helpers import TileSampler, CoordSystem
import json
from geojson import Feature, Point, MultiLineString
import geojson
from algo import generate_line_segments, generate_visible, iter_to_runs
import plyvel

define("port", default="8888", help="http port to listen on")
define("zoom", default=12, help="web mercator zoom level of dem data")
define("tile_template", default="http://localhost:8888/api/v1/tiles/{z}/{x}/{y}.tiff", help="url template where web mercator dem tiles can be fetched")
define("leveldb", default="")

db = None
class TileHandler(tornado.web.RequestHandler):
    def get(self, z, x, y):
        if not db:
            raise tornado.web.HTTPError(503)
        try:
            z = int(z)
            x = int(x)
            y = int(y)
        except Exception:
            raise tornado.web.HTTPError(400, 'tiles coordinates must be integers')
        data = db.get(b'/{}/{}/{}.tiff'.format(z, x, y))
        if not data:
            raise tornado.web.HTTPError(404, 'tile not found')
        self.set_header("Content-type", "image/tiff")
        self.write(data)
        self.finish()

class ApiHandler(tornado.web.RequestHandler):
    def write_api_response(self, format, obj):
        format = format.lower()
        if format=="geojson":
            self.set_header("Content-Type", "application/vnd.geo+json")
            self.write(geojson.dumps(obj))
        elif format=="html":
            self.render("../html/viewer.html", title="Viewshed API", geojson=geojson.dumps(obj))
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
    def get(self, format):
        lng = self.get_argument('lng')
        lat = self.get_argument('lat')
        try:
            lnglat = map(float, (lng, lat))
        except Exception:
            raise tornado.web.HTTPError(400)
        sampler = TileSampler(url_template=options.tile_template)
        pixel = CoordSystem.lnglat_to_pixel(lnglat)
        print 'Getting elevation at lng,lat:%s,%s %s,%s:' % (lng, lat, pixel[0], pixel[1])
        value = yield sampler.sample_pixel(pixel)
        lnglat = CoordSystem.pixel_to_lnglat(pixel)
        self.write_api_response(format, Feature(geometry=Point(lnglat), properties={
            "elevation":float(value),
            "uiMapCenter":lnglat,
            "uiPopupContent": "{} meters".format(float(value))
        }))

class ShedHandler(ApiHandler):
    @gen.coroutine
    def get(self, format):
        #168036.0, 404958.0
        #(168036.0, 404958.0) (168038.83662185463, 404948.41075725335)
        lng = self.get_argument('lng')
        lat = self.get_argument('lat')
        altitude = self.get_argument('altitude')
        radius = self.get_argument('radius', 1000)
        abs_altitude = self.get_argument('abs_altitude', False)
        try:
            lng, lat, altitude, radius = map(float, (lng, lat, altitude, radius))
        except Exception:
            raise tornado.web.HTTPError(400)
        radius = CoordSystem.pixel_per_meter((lng, lat))*radius #meters -> pixels
        print 'Getting viewshed at lng: {}, lat: {}, altitude: {}, radius:{}'.format(lng, lat, altitude, radius)
        center = CoordSystem.lnglat_to_pixel((lng, lat))
        sampler = TileSampler(url_template=options.tile_template)
        #add relative altitude offset
        if not abs_altitude:
            value = yield sampler.sample_pixel(center)
        else:
            value = 0
        line_segments = []
        for start, stop in generate_line_segments(radius, center):
            print start, stop
            elevations, pixels = yield sampler.sample_line(start, stop)
            if elevations is None: continue #if no data found skip it
            line_segments.extend(iter_to_runs(generate_visible(altitude+value, elevations), pixels))
        if len(line_segments) == 0:
            raise tornado.web.HTTPError(404, "No elevation data was found for query")
        line_segments = [[CoordSystem.pixel_to_lnglat(coord) for coord in segment] for segment in line_segments]
        self.write_api_response(format, Feature(geometry=MultiLineString(line_segments), properties={
            "calculationAltitude":altitude,
            "calculationRaduis":float(self.get_argument('radius', 1000)),
            "calculationLat":lat,
            "calculationLng":lng,
            "uiMapCenter":line_segments[0][0],
            "uiPopupContent":"Viewshed at {} meters above sea level".format(altitude)
        }))

application = tornado.web.Application([
    (r'/bundle\.js()', tornado.web.StaticFileHandler, {'path': '../html/bundle.js'}),
    (r'/bundle\.css()', tornado.web.StaticFileHandler, {'path': '../html/bundle.css'}),
    (r"/index\.html", tornado.web.RedirectHandler, {"url": "/viewshed"}),
    (r'/viewshed()', tornado.web.StaticFileHandler, {'path': '../html/viewshed.html'}),
    (r"/api/v1/elevation/(\w+)", ElevationHandler),
    (r"/api/v1/viewshed/(\w+)", ShedHandler),
    (r"/api/v1/tiles/(\d+)/(\d+)/(\d+)\.tiff", TileHandler)
])

if __name__ == "__main__":
    tornado.options.parse_command_line()
    if options.leveldb:
        db = plyvel.DB(options.leveldb, create_if_missing=False)
    application.listen(options.port)
    print 'listening on port %s' % options.port
    tornado.ioloop.IOLoop.current().start()