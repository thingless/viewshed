#!/bin/bash
set -o errexit
set -o nounset
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
__file="${__dir}/$(basename "${BASH_SOURCE[0]}")"
ZIP_FILE=$(readlink -f $1)
ZIP_DIR=$(dirname $ZIP_FILE)
OUT_DIR=${2-$ZIP_DIR}
OUT_DIR=$(readlink -f $OUT_DIR)
set -x
echo $(pwd)
#create working dir
TEMP_DIR=$(mktemp -d)
pushd $TEMP_DIR
cp $ZIP_FILE ./
#unzip
unzip -j *.zip
rm *.zip
#to tif and correct projection
#ls *.img *.hgt | parallel 'gdalwarp -co "PREDICTOR=2" -co "TILED=YES" -co "COMPRESS=DEFLATE" -t_srs epsg:3857 -of GTiff {} {.}.tif'
ls *.img *.hgt | parallel 'gdalwarp -co "PREDICTOR=2" -co "TILED=YES" -co "COMPRESS=DEFLATE" -of GTiff {} {.}.tif'
#copy output
mv *.tif $OUT_DIR
#cleanup
popd
rm -r $TEMP_DIR


#ls *.img | parallel -j 2 'gdal_translate -co "COMPRESS=LZW" -of GTiff {.}.img {.}.tif'
#gdalwarp -t_srs epsg:3857 ./imgn38w123_13.tif ./imgn38w123_13_57.tif
#gdaldem color-relief ./imgn38w123_13_57.tif color.txt relief.tif
#gdal2tiles.py -z 10 relief.tif tiles


#gdalbuildvrt out.vrt *.tif
