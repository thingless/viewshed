![Build Status](https://circleci.com/gh/KISSPrinciple/viewshed.png?circle-token=e2680171f6e2175b7b89e695fbc235c48b22c0c3 "Build Status")
Testing
-------
1. Start some server (e.g. node's `http-server`) in the tiles directory.
2. Install gdal and everything in requirements (virtualenvs don't work)
3. `python2 server.py`
4. curl 'http://localhost:8888/elevation/-122.32047/37.87312'
