from __future__ import division

import math
import itertools

SPACING = 5

def iter_to_runs(visibles, pixels):
    cur_val = 6666666
    start_idx = None

    out = []
    for i, val in enumerate(itertools.chain(visibles, [None])):
        if cur_val != val:
            if cur_val is True:
                # we just ended a run of "True" values
                out.append((pixels[start_idx], pixels[i - 1]))
            cur_val = val
            start_idx = i

    return out

def generate_line_segments(radius, center):
    """Generate radii of a circle that are a fixed width apart on the circle.

    Args:
      radius: radius of the circle, in pixels
      center: center of the circle (x, y) as tuple
    Returns:
      iterator of points (center, point on circle)
    """
    ang_step = SPACING / radius  # angle step in radians
    ang = 0
    while ang < 2 * math.pi:
        ang += ang_step
        yield (center, (center[0] + radius * math.cos(ang), center[1] + radius * math.sin(ang)))

def generate_visible(tower_height, heightmap):
    """Trace a ray and determine if a region is viewable.

    Args:
      tower_height: the elevation in meters above sea level of your antenna
      heightmap: an enumerable of heights in a given direction
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

if __name__ == '__main__':
    assert iter_to_runs([False, False, True, True, False, True, False, True, True]) == [(2, 3), (5, 5), (7, 8)]
    assert iter_to_runs([True]) == [(0, 0)]
    assert iter_to_runs([True, True, True, True, False, True, True]) == [(0, 3), (5, 6)]

    import matplotlib.pyplot as plt

    heightmap = [math.sin(x/15.0) * x for x in xrange(360)]
    tower_height = 100.0  # foots above MSL

    filt = ray(tower_height, heightmap)

    fhm = [h if fl else 0 for (h, fl) in zip(heightmap, filt)]

    plt.scatter(range(len(heightmap)), fhm)
    plt.scatter([0], [tower_height], color='red')
    plt.plot(heightmap)
    plt.show()
