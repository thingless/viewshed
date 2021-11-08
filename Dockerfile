#build node deps
FROM node:17-bullseye
COPY package.json /usr/local/viewshed/package.json
WORKDIR /usr/local/viewshed
RUN npm install
COPY html /usr/local/viewshed/html
RUN ./html/build.sh

FROM ubuntu:20.04
#update & install
RUN apt-get update \
    && apt-get upgrade -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
      wget \
      libopencv-* \ 
      libtiff5 \
      gdal-bin \
      python3-pip \
      python3-dev \
      python3-gdal \
      python3-numpy \
      python3-scipy \
    && rm -rf /var/lib/apt/lists/*

#install python deps
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

#copy code
RUN mkdir -p /usr/local/viewshed/
COPY download-data.sh /usr/local/viewshed/download-data.sh
COPY server  /usr/local/viewshed/server
COPY --from=0 /usr/local/viewshed/html /usr/local/viewshed/html

WORKDIR /usr/local/viewshed
ENTRYPOINT ["/usr/bin/python3", "./server/server.py", "--tile_template=http://127.0.0.1:8080/api/v1/tiles/{z}/{x}/{y}.tiff", "--leveldb=/usr/local/viewshed/data/tiles.leveldb", "--port=8080"]
EXPOSE 8080
