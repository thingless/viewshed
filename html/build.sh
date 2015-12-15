#!/bin/bash
set -x
rm bundle.*
./node_modules/browserify/bin/cmd.js -t [ babelify --presets [ react ] ] index.js -o bundle.js
./node_modules/node-sass/bin/node-sass ./index.scss > bundle.css
