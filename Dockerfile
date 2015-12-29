FROM ubuntu:14.04
MAINTAINER FreeTheNation

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y libopencv-* libtiff5 gdal-bin python-dev python-pip python-opencv python-numpy python-scipy python-gdal nginx
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

EXPOSE 80
CMD /sbin/init