#!/bin/bash
set -o errexit
set -o nounset
if [ "$#" -ne 2 ] ; then
  echo "Usage: view_float32_band.sh band_number input_file"
  exit 1
fi
INPUT_FILE=$(perl -e 'use Cwd "abs_path";print abs_path(shift)' $2)
#make temp working directory
TEMP_DIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'tmp_view_float32_band')
function finish {
  rm -r $TEMP_DIR #cleanup
}
trap finish EXIT
cd $TEMP_DIR
#copy tiff to working dir
OUTPUT_FILE="${INPUT_FILE%.*}.png"
printf "Reading $INPUT_FILE and creating $OUTPUT_FILE from band 1\n\n"
cp $INPUT_FILE ./input_file
NODATA=$(gdalinfo $INPUT_FILE | grep -i nodata | awk "NR==$1" | awk -F'=' '{print $2}')

#extract band
gdal_translate -b $1 input_file band
#color the band
echo "100 255 255 255" > color_relief.txt
echo "1 128 128 128" >> color_relief.txt
echo "0 0 0 0" >> color_relief.txt
#echo "$NODATA 255 0 0" >> color_relief.txt
gdaldem color-relief band color_relief.txt band_color
#convert and return
gdal_translate -of PNG band_color $OUTPUT_FILE
open $OUTPUT_FILE || feh $OUTPUT_FILE
