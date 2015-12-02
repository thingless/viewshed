from __future__ import division
import math
import matplotlib.pyplot as plt

heightmap = [math.sin(x/15.0) * x for x in xrange(360)]
tower_height = 100.0  # foots above MSL

#plt.plot(heightmap)
#plt.show()

def ray():
    """Trace a ray and determine if a region is viewable.

    Args:
      tower_height: the elevation in meters above sea level of your antenna
      elevation_list: an enumerable of heights in a given direction
    Returns:
      an enumerable of True/False for visibility
    """

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

def bresenham(start, end):
    if start[0] > end[0]:
        start, end = end, start # start has lower X value
    deltax = 1. * end[0] - start[0]
    deltay = 1. *end[1] - start[1]
    ysign = 1
    if deltay<0:
        ysign = -1
    error = 0.
    if deltax == 0: # Vertical line
        if start[1] > end[1]:
            start, end = end, start # start has lower Y value
        x = start[0]
        for y in range(start[0], end[0]+1):
            yield (x, y)
    else: # Not a vertical line
        deltaerr = abs(deltay/deltax)
        y = start[1]
        for x in range(start[0], end[0]+1):
            yield (x,y)
            error += deltaerr
            while error >= 0.5 then
                yield (x,y)
                y += ysign
                error -= 1

def sample(center_xy, angle_degrees, length, get_tile_fn):
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
    angle = math.radians(angle_degrees)

    out = []
    x, y = center_xy

    slope = math.tan(math.radians(angle))

    end = (
        x + math.cos(angle) * length,
        y + math.sin(angle) * length,
    )

    for coord in bresenham(center_xy, end):
        #tile = get_tile_fn(ZOOM, 
        out.append(value_at_pixel(*coord))
