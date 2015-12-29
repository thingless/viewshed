FROM ubuntu:14.04
MAINTAINER FreeTheNation

#update
RUN apt-get update
RUN apt-get upgrade -y

#install deps
RUN apt-get install -y libopencv-* libtiff5 gdal-bin python-dev python-pip python-opencv python-numpy python-scipy python-gdal nginx
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

#copy source
RUN mkdir -p /var/www/viewshed
COPY server/* /var/www/viewshed/
RUN chown -R www-data:www-data /var/www

#config nginx & upstart

EXPOSE 80
CMD /sbin/init