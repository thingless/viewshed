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
RUN mkdir -p /var/www/viewshed/server
RUN mkdir -p /var/www/viewshed/html
COPY server /var/www/viewshed/server #python code
COPY html /var/www/viewshed/html     #html & JS
RUN chown -R www-data:www-data /var/www

#config nginx & upstart
COPY config/upstart-viewshed.conf /etc/init/viewshed.conf
RUN rm /etc/nginx/sites-enabled/default || true
COPY conf/nginx-viewshed.conf /etc/nginx/sites-enabled/viewshed.conf

EXPOSE 80
CMD /sbin/init