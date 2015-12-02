from __future__ import division
import math
import matplotlib.pyplot as plt

heightmap = [math.sin(x/15.0) * x for x in xrange(360)]
tower_height = 100.0  # foots above MSL

#plt.plot(heightmap)
#plt.show()

def ray():
    min_angle = -10000
    for i, height in enumerate(heightmap):
        if tower_height - height == 0:
            angle_to_point = 0
        elif tower_height > height:
            angle_to_point = math.atan(i / (tower_height - height))
        else:
            angle_to_point = math.atan((height - tower_height) / i) + math.pi / 2

        if angle_to_point >= min_angle:
            min_angle = angle_to_point
            yield True
        else:
            yield False

filt = ray()

fhm = [h if fl else 0 for (h, fl) in zip(heightmap, ray())]

plt.scatter(range(len(heightmap)), fhm)
plt.scatter([0], [tower_height], color='red')
plt.plot(heightmap)
plt.show()



ZOOM = 12

def sample(center_xy, angle, length, get_tile_fn):
    """Get a list of values along a line across many tiles.

    Args:
      center_xy: starting point for the line in pixels like (x,y)
      angle: angle in degrees, unit circle style (starting at 3 o'clock, going CCW)
      length: length of the line to cast in pixels
      get_tile_fn: callback(zoom, x, y) -> returns tile x,y at zoom, as 2d numpy array

    Returns:
      list of `length` values as floats
    """
    dx = 1  # one pixel steps, whatever

    out = []
    x, y = center_xy

    slope = math.tan(math.radians(angle))

    end = (
        x + math.cos(math.radians(angle)) * length,
        y + math.sin(math.radians(angle)) * length,
    )

    while len(out) < length:
        x += dx
        y += dx * slope

    tile = get_tile_fn(ZOOM, 
