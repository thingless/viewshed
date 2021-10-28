This folder contains the scripts nessary to build the DEM tif tile pyramid.

Scripts are named step1_*, step2_*, etc according to the order in which they should be ran.

The folling command will install the required deps on ubuntu 20.04. Turn off virtual env... it sucks!
sudo apt-get install -y libtiff5 gdal-bin python3-dev python3-gdal parallel zip unzip







Below are random comments probably not worth reading:

#to download files
wget --limit-rate 1m  -N -r -l1 --no-parent -A ".zip" "https://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF/"
