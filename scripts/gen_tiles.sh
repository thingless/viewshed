#!/usr/bin/env bash
gdalbuildvrt ./merged.vrt $1
#Zoom level 12 is 29.277080383193702 m / pixel near SF
#(Math.cos(40 * Math.PI/180) * 2 * Math.PI * 6378137) / (256 * Math.pow(2, 12))
~/projects/shed/scripts/gdal2tiles.py -w none -n -f tiff -p mercator -z 12 -v tiles
