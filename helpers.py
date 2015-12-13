import math
import gdal
import numpy as np

from tornado.httpclient import AsyncHTTPClient
from skimage.draw import line
from tornado.gen import Return
from tornado import gen

ZOOM=12

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

class Tile(object):
    def __init__(self, zoom, pixel, url_template):
        self.zoom = zoom
        self.url_template = url_template
        self.pixel = (pixel[0]//255*255, pixel[1]//255*255) #round pixel to top left corner
        self.data = self._retrieve_data() #data is actually a future

    @property
    def url(self):
        tile = CoordSystem.pixel_to_tile(self.pixel, self.zoom)
        return self.url_template.format(z=self.zoom, x=tile[0], y=tile[1])

    @gen.coroutine
    def _retrieve_data(self):
        self.res = yield AsyncHTTPClient().fetch(self.url) #NOTE: currently will throw an http error if status code is not 200
        raise Return(load_float32_image(self.res.body) if self.res.code == 200 else None)


class TileSampler(object):
    """Samples tile values. Everything is in global pixel space at specified zoom"""

    def __init__(self, zoom=ZOOM, url_template='http://127.0.0.1:8080/{z}/{x}/{y}.tiff'):
        self.zoom = zoom
        self.url_template = url_template
        self._tiles = {}

    def _unique_rows(self, data):
        """Returns only the unique rows in a numpy array

        Args:
            data (array): numpy array to dedupe

        Returns:
            array: deduped numpy array
        """
        uniq = np.unique(data.view(data.dtype.descr * data.shape[1]))
        return uniq.view(data.dtype).reshape(-1, data.shape[1])

    @gen.coroutine
    def _sample_tile_pixels(self, tile_pixel, pixels):
        """Returns pixel's values which intersect a single tile"""
        xs = pixels[:,0]
        ys = pixels[:,1]
        print ys, xs
        print tile_pixel
        xs = (xs-tile_pixel[0])[(xs[:]>=0) & (xs[:]<=255)] #filter to just this tile
        ys = (ys-tile_pixel[1])[(ys[:]>=0) & (ys[:]<=255)]
        tile_data = yield self.get_tile(tile_pixel).data
        raise Return(tile_data[ys, xs]) #numpy is row column

    def get_tile(self, pixel):
        """Returns a tile. If tile already exists a cached version will be returned. 

        Args:
            pixel ((int, int)): A pixel in the tile to be returned
        """
        tile_pixel = (pixel[0]//256*256, pixel[1]//256*256)
        return self._tiles.get(tile_pixel, Tile(self.zoom, tile_pixel, self.url_template))

    @gen.coroutine
    def sample_pixels(self, pixels):
        """Samples arbitrary pixel values from the map. Returned order may not match input order (will for lines)

        Args:
            pixels (array): 2d numpy array where each row is a pixel to sample

        Returns:
            array: numpy array of values
        """
        #determin required tiles
        tile_pixels = np.floor_divide(pixels, 256)*256
        tile_pixels = self._unique_rows(tile_pixels)
        #preload tiles
        for tile_pixel in tile_pixels: self.get_tile(tile_pixel)
        #sample tiles
        data = [(yield self._sample_tile_pixels(tile_pixel, pixels)) for tile_pixel in tile_pixels]
        raise Return(np.concatenate(data))

    @gen.coroutine
    def sample_line(self, pixel1, pixel2):
        """Samples a line of pixel values in the map. Pixel values should be ordered from pixel1 to pixel2.

        Args:
            pixel1 ((int,int)): the 1st coordinate of the line in global pixel space
            pixel2 ((int,int)): the 2nd coordinate of the line in global pixel space

        Returns:
            array: numpy array of values
        """
        xs, ys = line(pixel1[0], pixel1[1], pixel2[0], pixel2[1])
        pixels = np.dstack((xs, ys))[0]
        raise Return((yield self.sample_pixels(pixels)))

    @gen.coroutine
    def sample_pixel(self, pixel):
        raise Return((yield self.sample_pixels(np.array([pixel])))[0])
