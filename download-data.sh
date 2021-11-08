#!/bin/bash
set -e
DOWNLOAD_URL="https://b2-free-egress-worker.mod64.workers.dev/cf-public/b03108db-65f2-4d7c-b884-bb908d111400/tiles.leveldb.tar.gz"
if [ -d "tiles.leveldb" ] 
then
    echo "tiles.leveldb already exsits" 
else
    echo "downloading tiles.leveldb..."
    wget "$DOWNLOAD_URL" -O - | tar -xz
fi

