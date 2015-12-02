import math
import gdal

import tornado.queues
from tornado.httpclient import AsyncHTTPClient

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
        return cls.pixel_to_tile(r, zoom)

    @classmethod
    def pixel_to_tile(cls, pixel, zoom=ZOOM):
        return (int(pixel[0]//256), 2**zoom - int(pixel[1]//256) - 1)

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

class TileGetter(object):
    TILE_HOST = "http://127.0.0.1:8080"

    def __init__(self):
        self._url_getter = UrlGetter()

    def _get_tile_url(self, zoom, pixel):
        tile = CoordSystem.pixel_to_tile(pixel, zoom)
        return self.TILE_HOST + "/{z}/{x}/{y}.tiff".format(z=ZOOM, x=tile[0], y=tile[1])

    @gen.coroutine
    def get_pixel_value(self, zoom, pixel):
        """Get the value at a given pixel's global coordinates."""
        resp = yield self._url_getter.get_data(self._get_tile_url(zoom, pixel))
        nparr = load_float32_image(resp.body)
        return nparr[pixel[1] % 256, pixel[0] % 256]
