FROM phusion/baseimage:0.9.18
MAINTAINER FreeTheNation

#update & install
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y libopencv-* libtiff5 gdal-bin python-dev python-pip python-opencv python-numpy python-scipy python-gdal libleveldb-dev

#install python deps
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

#copy source
RUN mkdir -p /usr/local/viewshed/
COPY server  /usr/local/viewshed/server
COPY html    /usr/local/viewshed/html

#config runit
RUN mkdir -p /etc/service/viewshed/
COPY config/viewshed.runit /etc/service/viewshed/run
RUN chmod +x /etc/service/viewshed/run

EXPOSE 80
