import tornado.ioloop
import tornado.web
from tornado import gen

TILE_HOST = "http://127.0.0.1"

class ElevationHandler(tornado.web.RequestHandler):
  @gen.coroutine
  def get(self, lat, lng):
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(TILE_HOST+"")
    do_something_with_response(response)
    self.render("template.html")

application = tornado.web.Application([
  (r"/(\d+\.?\d*)/(\d+\.?\d*)", ElevationHandler),
])

if __name__ == "__main__":
  application.listen(8888)
  tornado.ioloop.IOLoop.current().start()