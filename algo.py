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
