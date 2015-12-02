from tornado.web import RequestHandler
from tornado.gen import Return
import tornado.gen
import tornado.queues
import tornado, os, datetime
from tornado.httpclient import AsyncHTTPClient
from server import load_float32_image

ONE_DAY=60*60*24

class UrlGetter(object):
    def __init__():
        self.data = {}

    @tornado.gen.coroutine
    def get_urls(self, urls, concurrency=4):
        if type(urls) == str:
            urls = [urls]
        queue = tornado.queues.Queue()
        #put the jobs on the queue
        for url in urls:
            queue.put(url)
        #spin up the workers
        for _ in range(concurrency):
            self.work(queue)
        yield queue.join(timeout=datetime.timedelta(seconds=ONE_DAY))

    @tornado.gen.coroutine
    def work(self, queue):
        while True:
            try:
                url = yield queue.get()
                image = yield self.get_data(url)
                self.data[url] = image
            finally:
                queue.task_done()

    @tornado.gen.coroutine
    def get_data(self, url):
        if url in self.data:
            return self.data[url]
        http_client = AsyncHTTPClient()
        raise Return(yield http_client.fetch(url))

class ViewShedHandler(RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        getter = UrlGetter()
        urls = yield getter.url_getter(['https://www.google.com/'])
