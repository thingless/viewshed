from tornado.web import RequestHandler
from tornado.gen import Return
import tornado.gen
import tornado.queues
import tornado, os, datetime
from tornado.httpclient import AsyncHTTPClient
from helpers import load_float32_image
from server import ApiHandler

class ViewShedHandler(ApiHandler):
    @tornado.gen.coroutine
    def get(self):
        getter = UrlGetter()
        urls = yield getter.url_getter(['https://www.google.com/'])
