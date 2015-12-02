Testing
-------
1. Start some server (e.g. node's `http-server`) in the tiles directory.
2. Install gdal and everything in requirements (virtualenvs don't work)
3. `python2 server.py`
4. curl 'http://localhost:8888/elevation/-122.32047/37.87312'
