import math
import gdal
import numpy as np
import itertools

import tornado.queues
from tornado.httpclient import AsyncHTTPClient
from skimage.draw import line

ONE_DAY=60*60*24

class UrlGetter(object):
    def __init__():
        self.data = {}

    @tornado.gen.coroutine
    def get_urls(self, urls, concurrency=4):
        queue = tornado.queues.Queue()
        #put the jobs on the queue
        for url in urls:
            queue.put(url)
        #spin up the workers
        for _ in range(concurrency):
            self.work(queue)
        yield queue.join(timeout=datetime.timedelta(seconds=ONE_DAY))
        raise Return(self.data)

    @tornado.gen.coroutine
    def work(self, queue):
        while True:
            try:
                url = yield queue.get()
                yield self.get_data(url)
            finally:
                queue.task_done()

    @tornado.gen.coroutine
    def get_url(self, url):
        if url not in self.data:
            res = yield AsyncHTTPClient().fetch(url)
            self.data[url] = load_float32_image(res.body) if res.code == 200 else None
        raise Return(self.data[url])

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

class TileSampler(object):
    """Samples tile values. Everything is in global pixel space"""
    TILE_HOST = "http://127.0.0.1:8080"

    def __init__(self, zoom=12):
        self._url_getter = UrlGetter()
        self.zoom = zoom

    def _get_tile_url(self, pixel):
        tile = CoordSystem.pixel_to_tile(pixel, self.zoom)
        return self.TILE_HOST + "/{z}/{x}/{y}.tiff".format(z=self.zoom, x=tile[0], y=tile[1])

    def _unique_rows(data):
        uniq = np.unique(data.view(data.dtype.descr * data.shape[1]))
        return uniq.view(data.dtype).reshape(-1, data.shape[1])

    @gen.coroutine
    def sample_line(self, p1, p2):
        xs, ys = line(p1[0], p1[1], p2[0], p2[1])
        coords = np.dstack((xs, ys))[0]
        tiles_coords = np.dstack((np.floor_divide(xs,256), np.floor_divide(ys,256)))[0]
        tiles_coords = self._unique_rows(tiles_coords)
        tiles = yield self.get_tiles(tiles_coords)
        ret = [ for tile in tiles]

    def _sample_line_in_tiles(self, tiles, xs, ys):
        return itertools.chain.from_iterable((self._sample_line_in_tile(tile, xs, ys) for tile in tiles))

    def _sample_line_in_tile(self, tile, xs, ys):
        xs = (xs-tile.x)[x[:,0]>=0) & (x[:,0]<=255)] #filter to just this tile
        ys = (ys-tile.y)[x[:,0]>=0) & (x[:,0]<=255)]
        return tile[xs, ys] #select and return values :)

    @gen.coroutine
    def get_pixel_value(self, zoom, pixel):
        """Get the value at a given pixel's global coordinates."""
        resp = yield self._url_getter.get_data(self._get_tile_url(zoom, pixel))
        nparr = load_float32_image(resp.body)
        return nparr[pixel[1] % 256, pixel[0] % 256]
