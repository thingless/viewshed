import tornado.ioloop
import tornado.web
from tornado import gen
import tornado
from helpers import TileSampler, CoordSystem
import json
from geojson import Feature, Point, MultiLineString
import geojson
from algo import generate_line_segments, generate_visible, iter_to_runs

PORT = 8888
ZOOM = 12

#class MainHandler(tornado.web.RequestHandler):
#    def get(self):
#        items = ["Item 1", "Item 2", "Item 3"]
#        self.render("template.html", title="My title", items=items)

class ApiHandler(tornado.web.RequestHandler):

    def write_api_response(self, format, obj):
        format = format.lower()
        if format=="geojson":
            self.set_header("Content-Type", "application/vnd.geo+json")
            self.write(geojson.dumps(obj))
        elif format=="html":
            self.render("html/viewer.html", title="Viewshed API", geojson=geojson.dumps(obj))

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
        sampler = TileSampler()
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
        try:
            lng, lat, altitude, radius = map(float, (lng, lat, altitude, radius))
        except Exception:
            raise tornado.web.HTTPError(400)
        radius = CoordSystem.pixel_per_meter((lng, lat))*radius #meters -> pixels
        print 'Getting viewshed at lng: {}, lat: {}, altitude: {}, radius:{}'.format(lng, lat, altitude, radius)
        center = CoordSystem.lnglat_to_pixel((lng, lat))
        sampler = TileSampler()
        line_segments = []
        for start, stop in generate_line_segments(radius, center):
            print start, stop
            elevations, pixels = yield sampler.sample_line(start, stop)
            line_segments.extend(iter_to_runs(generate_visible(altitude, elevations), pixels))

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
    (r'/bundle\.js()', tornado.web.StaticFileHandler, {'path': 'html/bundle.js'}),
    (r'/bundle\.css()', tornado.web.StaticFileHandler, {'path': 'html/bundle.css'}),
    (r"/api/v1/elevation/(\w+)", ElevationHandler),
    (r"/api/v1/viewshed/(\w+)", ShedHandler),
])

if __name__ == "__main__":
    application.listen(PORT)
    print 'listening on port %s' % PORT
    tornado.ioloop.IOLoop.current().start()
