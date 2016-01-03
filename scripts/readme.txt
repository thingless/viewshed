This folder contains the scripts nessary to build the DEM tif tile pyramid.

Scripts are named step1_*, step2_*, etc according to the order in which they should be ran.

The folling command will install the required deps on ubuntu 14.04. Turn off virtual env... it sucks!
sudo apt-get install -y libtiff5 gdal-bin python-dev python-gdal parallel zip unzip








Below are random comments probably not worth reading:

#to download files
wget --limit-rate 1m  -N -r -l1 --no-parent -A ".zip" -R "_ArcGrid.zip" "ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/NED/13/ArcGrid/"
