#!/usr/bin/env bash
set -o errexit
set -o nounset
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$#" -eq 0 ] ; then
  echo "Usage: step1_unzipToTif.sh tif_files"
  echo "Note: this creates more than 1TB of data :/"
  exit 1
fi

echo "creating tile pyramid for..."
echo $@
sleep 3

gdalbuildvrt ./merged.vrt $@
#Zoom level 12 is 29.277080383193702 m / pixel near SF
#(Math.cos(40 * Math.PI/180) * 2 * Math.PI * 6378137) / (256 * Math.pow(2, 12))
${__dir}/gdal2tiles.py -w none -n -f tiff -p mercator -z 12 -v ./merged.vrt tiles
