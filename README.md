ViewSHED
=========

ViewSHED is an open-source API for computing the visible area given a location and elevation. It was built to aid in the construction of mesh networks and for use by amateur radio. The API currently supports [GeoJSON](http://geojson.org/) and an [HTML interface](http://viewshed.mod64.net/viewshed).

Calculating viewshed is not particularly hard but wrangling together the data and learning an appropriate GIS tool can be challenging. ViewSHED has an [easy to use web interface](http://viewshed.mod64.net/viewshed) and uses accurate (90 meter) global elevation data making calculating viewshed easy.

##  [DEMO](http://viewshed.mod64.net/viewshed)

## API
### ViewShed
Calculates the the [viewshed](https://en.wikipedia.org/wiki/Viewshed) given a location and elevation.
``` bash
curl http://viewshed.mod64.net/api/v1/viewshed/{format}?lng={longitude}&lat={latitude}&altitude={altitude}&radius={radius}
```
#### Parameters:
| Name         | Description                                                                                                                      |
|--------------|----------------------------------------------------------------------------------------------------------------------------------|
| format       | The return type. Currently geojson and html are supported. If html is specified a map will be rendered, visualizing the viewshed |
| longitude    | longitude of location                                                                                                            |
| latitude     | latitude of location                                                                                                             |
| altitude     | altitude of location/tower in meters above ground level                                                                          |
| radius       | radius of viewshed calculation in meters                                                                                         |
| abs_altitude | if specified aka `abs_altitude=1` altitude will be relative to sea level rather than ground level                                |
#### Examples:

### Elevation
Returns the elevation of the ground at a given location.
```bash
curl http://viewshed.mod64.net/api/v1/elevation/{format}?lng={longitude}&lat={latitude}
```

### Top of Hill
Returns the elevation and lat/lng of the highest point in a given radius.
```bash
curl http://viewshed.mod64.net/api/v1/topofhill/{format}?lng={longitude}&lat={latitude}&radius=100
```

#### Parameters:
| Name         | Description                                                                                                                      |
|--------------|----------------------------------------------------------------------------------------------------------------------------------|
| format       | The return type. Currently geojson and html are supported. If html is specified a map will be rendered, visualizing the elevation |
| longitude    | longitude of location                                                                                                            |
| latitude     | latitude of location                                                                                                         |
#### Examples:

## Running
First, try the publicly hosted version and ensure it does what you want. The elevation data is approx. 30G and takes a while to download. Assuming you still wish to deploy your own server:

1. [Install docker](https://docs.docker.com/engine/install/).
2. Download the ~30GB of data by running `./download-data.sh`. This will probably take a while.
3. Run the container with
```
docker run -it --rm -p 8080:8080 -v "./tiles.leveldb:/usr/local/viewshed/data/tiles.leveldb" viewshed:latest
```

## Data Source & Quality
The calculations are currently based on [SRTM Digital Elevation Database v4.1](http://www.cgiar-csi.org/data/srtm-90m-digital-elevation-database-v4-1). Calculations are accurate worldwide to approx. 90m. 
