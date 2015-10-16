#!/usr/bin/env bash
set -o errexit
set -o nounset
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$#" -ne 1 ] ; then
  echo "Usage: gen_tiles.sh tif_files"
  exit 1
fi

gdalbuildvrt ./merged.vrt $1
#Zoom level 12 is 29.277080383193702 m / pixel near SF
#(Math.cos(40 * Math.PI/180) * 2 * Math.PI * 6378137) / (256 * Math.pow(2, 12))
${__dir}/gdal2tiles.py -w none -n -f tiff -p mercator -z 12 -v ./merged.vrt tiles
#need to strip 2nd band and compress
find ./tiles/ -name "*.tiff" | parallel 'echo gdal_translate -co "PREDICTOR=2" -co "TILED=YES" -co "COMPRESS=DEFLATE" -b 1 {} {.}; mv {.} {}'
