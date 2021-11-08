#!/usr/bin/env bash
set -o errexit
set -o nounset
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$#" -eq 0 ] ; then
  echo "Usage: step3_stripAndCompressTiles.sh tile_pyramid_dir"
  exit 1
fi

echo "stripping extra band and compressing tiles..."
cd "$1"
find tiles -name "*.tiff" | parallel 'gdal_translate -co "PREDICTOR=2" -co "TILED=YES" -co "COMPRESS=DEFLATE" -b 1 {} {.}; mv {.} {}'
