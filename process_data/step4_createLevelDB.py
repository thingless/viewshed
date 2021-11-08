#!/usr/bin/env python3
import os
import plyvel
import sys
import re

if len(sys.argv) != 2:
    print('usage ./step3_createLevelDb.py TILE_DIRECTORY')
    sys.exit(1)

TILE_DIR = sys.argv[1]
print(f'Creating leveldb database from tile directory {TILE_DIR}...')
try:
    os.remove('tiles.leveldb')
except OSError:
    pass
db = plyvel.DB('tiles.leveldb', create_if_missing=True)
for root, dirs, files in os.walk(TILE_DIR):
    for name in files:
        path = os.path.join(root, name)
        key = "/"+re.search(r'.*?(\d+/\d+/\d+\.tiff$)', path).group(1)
        print(key, path)
        with open(path, mode='rb') as file: # b is important -> binary
            fileContent = file.read()
            db.put(str.encode(key), fileContent)

#filter zeros? https://stackoverflow.com/questions/49689575/geotiff-image-is-read-as-all-zeros-in-numpy-array-using-gdal