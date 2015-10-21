import tornado.ioloop
import tornado.web
from tornado import gen

class TileHandler(tornado.web.RequestHandler):
  @gen.coroutine
  def get(self, lat, lng):
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch("http://example.com")
    do_something_with_response(response)
    self.render("template.html")

application = tornado.web.Application([
  (r"/", MainHandler),
])

if __name__ == "__main__":
  application.listen(8888)
  tornado.ioloop.IOLoop.current().start()