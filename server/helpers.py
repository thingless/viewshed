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

    @classmethod
    def meters_per_pixel(cls, lnglat, zoom=ZOOM):
        '''meters per pixel in epsg3857'''
        return (math.cos(lnglat[1] * math.pi/180.0) * 2.0 * math.pi * 6378137.0) / (256.0 * math.pow(2, zoom))

    @classmethod
    def pixel_per_meter(cls, lnglat, zoom=ZOOM):
        return 1.0/cls.meters_per_pixel(lnglat, zoom)

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
        self.pixel = (pixel[0]//256*256, pixel[1]//256*256) #round pixel to top left corner
        self.data = self._retrieve_data() #data is actually a future

    @property
    def url(self):
        tile = CoordSystem.pixel_to_tile(self.pixel, self.zoom)
        return self.url_template.format(z=self.zoom, x=tile[0], y=tile[1])

    @gen.coroutine
    def _retrieve_data(self):
        self.res = yield AsyncHTTPClient().fetch(self.url, raise_error=False)
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
        _, idxs = np.unique(data.view(data.dtype.descr * data.shape[1]), return_index=True)
        return data[sorted(idxs),:]

    @gen.coroutine
    def _sample_tile_pixels(self, tile_pixel, pixels):
        """Returns pixel's values which intersect a single tile"""
        pixels = pixels - np.array(tile_pixel)
        pixels = pixels[(pixels[:,0]>=0) & (pixels[:,0]<=255) & (pixels[:,1]>=0) & (pixels[:,1]<=255)]
        xs = pixels[:,0]
        ys = pixels[:,1]
        tile_data = yield self.get_tile(tile_pixel).data
        if tile_data is None: raise Return(None)
        raise Return(tile_data[ys.astype(int), xs.astype(int)]) #numpy is row column

    def get_tile(self, pixel):
        """Returns a tile. If tile already exists a cached version will be returned. 

        Args:
            pixel ((int, int)): A pixel in the tile to be returned
        """
        tile_pixel = (pixel[0]//256*256, pixel[1]//256*256)
        if tile_pixel not in self._tiles:
            self._tiles[tile_pixel] = Tile(self.zoom, tile_pixel, self.url_template)
        return self._tiles[tile_pixel]

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
        data = [d for d in data if d is not None]
        if len(data) == 0:
            raise Return((None, pixels)) #if no tiles were found return None
        raise Return((np.concatenate(data), pixels))

    @gen.coroutine
    def sample_line(self, pixel1, pixel2):
        """Samples a line of pixel values in the map. Pixel values should be ordered from pixel1 to pixel2.

        Args:
            pixel1 ((int,int)): the 1st coordinate of the line in global pixel space
            pixel2 ((int,int)): the 2nd coordinate of the line in global pixel space

        Returns:
            array: numpy array of values
        """
        pixel1 = map(int, pixel1)
        pixel2 = map(int, pixel2)
        xs, ys = line(pixel1[0], pixel1[1], pixel2[0], pixel2[1])
        pixels = np.dstack((xs, ys))[0]
        raise Return((yield self.sample_pixels(pixels)))

    @gen.coroutine
    def sample_pixel(self, pixel):
        raise Return((yield self.sample_pixels(np.array([pixel])))[0][0])


#Testing urls
#http://localhost:8888/elevation/-122.30933440000001/37.8666298
#http://localhost:8888/shed/-122.30933440000001/37.8666298/10/300