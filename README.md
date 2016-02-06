ViewSHED
=========

ViewSHED is an open-source API for computing the visible area given a location and elevation. It was built to aid in the construction of mesh networks and for use by amateur radio. The API currently supports [GeoJSON](http://geojson.org/) and an [HTML interface](http://viewshed.icyego.com/viewshed).

Calculating viewshed is not particularly hard but wrangling together the data and learning an appropriate GIS tool can be challenging. ViewSHED has an [easy to use web interface](http://viewshed.icyego.com/viewshed) and uses accurate (90 meter) global elevation data making calculating viewshed easy.

##[DEMO](http://viewshed.icyego.com/viewshed)

##API
### ViewShed
Calculates the the [viewshed](https://en.wikipedia.org/wiki/Viewshed) given a location and elevation.
``` bash
curl http://viewshed.icyego.com/api/v1/viewshed/{format}?lng={longitude}&lat={latitude}&altitude={altitude}&radius={radius}
```
####Parameters:
| Name         | Description                                                                                                                      |
|--------------|----------------------------------------------------------------------------------------------------------------------------------|
| format       | The return type. Currently geojson and html are supported. If html is specified a map will be rendered, visualizing the viewshed |
| longitude    | longitude of location                                                                                                            |
| latitude     | latitude of location                                                                                                             |
| altitude     | altitude of location/tower in meters above ground level                                                                          |
| radius       | radius of viewshed calculation in meters                                                                                         |
| abs_altitude | if specified aka `abs_altitude=1` altitude will be relative to sea level rather than ground level                                |
####Examples:

###Elevation
Returns the elevation of the ground at a given location.
```bash
curl http://viewshed.icyego.com/api/v1/elevation/{format}?lng={longitude}&lat={latitude}
```
####Parameters:
| Name         | Description                                                                                                                      |
|--------------|----------------------------------------------------------------------------------------------------------------------------------|
| format       | The return type. Currently geojson and html are supported. If html is specified a map will be rendered, visualizing the elevation |
| longitude    | longitude of location                                                                                                            |
| latitude     | latitude of location                                                                                                         |
####Examples:


##Running Locally & Contributing
Because of its dependence on GDAL and OpenCV ViewSHED can be a little tricky to get running locally for development. The steps below will work on Ubuntu 14.04 if your not using virtualenv:

1. Run `sudo apt-get install -y libopencv-* libtiff5 gdal-bin python-dev python-pip python-opencv python-numpy python-scipy python-gdal libleveldb-dev`
2. Run `git clone https://github.com/thingless/viewshed.git`
3. Run `cd viewshed`
4. Run `sudo pip install -r ./requirements.txt`
5. Run `./server.py --tile_template 'http://viewshed.icyego.com/api/v1/tiles/{z}/{x}/{y}.tiff'`

__NOTE __: the setup instructions above are only suitable for development as there are rate limits enforced. If you want to deploy your own ViewSHED sever consult the deployment section.

##Deploying
First, try the publicly hosted version and ensure it does what you want. The elevation data is approx. 30G and takes a while to download. Assuming you still wish to deploy your own server:

1. [Install docker](https://docs.docker.com/engine/installation/) on the server you'll be running ViewSHED on.
2. Download the data with wget by running `wget http://somedamurl`
3. Clone the prebuilt docker container with all requirements preinstalled by running `docker pull blah blah blah`.
4. Start the container by running `docker start {data_folder} blah blah blah`
 where the `data_folder` is the path where you extracted the data tar ball you downloaded in step 2.

##Data Source & Quality
The calculations are currently based on [SRTM Digital Elevation Database v4.1](http://www.cgiar-csi.org/data/srtm-90m-digital-elevation-database-v4-1). Calculations are accurate worldwide to approx. 90m. 
