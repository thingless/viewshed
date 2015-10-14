#!/bin/bash
set -o errexit
set -o nounset
if [ "$#" -ne 2 ] ; then
  echo "Usage: view_band.sh band_number input_file"
  exit 1
fi
INPUT_FILE=$(readlink -f $2)
#make temp working directory
TEMP_DIR=$(mktemp -d)
function finish {
  rm -r $TEMP_DIR #cleanup
}
trap finish EXIT
cd $TEMP_DIR
#copy tiff to working dir
OUTPUT_FILE="${INPUT_FILE%.*}.png"
printf "Reading $INPUT_FILE and creating $OUTPUT_FILE from band 1\n\n"
cp $INPUT_FILE ./input_file
#extract band
gdal_translate -b $1 input_file band
#color the band
echo "100% 255 255 255" > color_relief.txt
echo "75% 235 220 175" >> color_relief.txt
echo "50% 190 185 135" >> color_relief.txt
echo "25% 240 250 150" >> color_relief.txt
echo "0% 50 180 50" >> color_relief.txt
gdaldem color-relief band color_relief.txt band_color
#convert and return
gdal_translate -of PNG band_color $OUTPUT_FILE
open $OUTPUT_FILE