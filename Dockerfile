FROM phusion/baseimage:0.9.18
MAINTAINER FreeTheNation

#update & install
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y libopencv-* libtiff5 gdal-bin python-dev python-pip python-opencv python-numpy python-scipy python-gdal nginx libleveldb-dev

#install python deps
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

#copy source
RUN mkdir -p /var/www/viewshed/
COPY server /var/www/viewshed/server
COPY html /var/www/viewshed/html
RUN chown -R www-data:www-data /var/www

#config nginx & runit
COPY config/upstart-viewshed.conf /etc/init/viewshed.conf
RUN rm /etc/nginx/sites-enabled/default || true
COPY config/nginx-viewshed.conf /etc/nginx/sites-enabled/viewshed.conf

EXPOSE 80
CMD /sbin/init