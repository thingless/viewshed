#!/bin/bash
#init stuff
set -o errexit
set -o nounset
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
__file="${__dir}/$(basename "${BASH_SOURCE[0]}")"
ZIP_FILE=$1
ZIP_DIR=$(dirname $ZIP_FILE)
OUT_DIR=${$2-$ZIP_DIR}

#create working dir
TEMP_DIR=$(mktemp -d)
pushd $TEMP_DIR
cp $ZIP_FILE ./
#unzip
unzip *.zip
rm *.zip
rm !(*.img)
#to tif and correct projection
ls *.tif | parallel 'gdalwarp -co "COMPRESS=LZW" -t_srs epsg:3857 -of GTiff {.}.img {.}.tif'
#copy output
mv *.tif OUT_DIR
#cleanup
popd
rm $TEMP_DIR


#ls *.img | parallel -j 2 'gdal_translate -co "COMPRESS=LZW" -of GTiff {.}.img {.}.tif'
#gdalwarp -t_srs epsg:3857 ./imgn38w123_13.tif ./imgn38w123_13_57.tif
#gdaldem color-relief ./imgn38w123_13_57.tif color.txt relief.tif
#gdal2tiles.py -z 10 relief.tif tiles
