#!/bin/bash
set -o errexit
set -o pipefail

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
__file="${__dir}/$(basename "${BASH_SOURCE[0]}")"

set -x #log cmds
cd $__dir
rm bundle.* || true
../node_modules/browserify/bin/cmd.js -t [ babelify --presets [ react ] ] ./index.js -o ./bundle.js
../node_modules/uglify-js/bin/uglifyjs ./bundle.js --screw-ie8 --output ./bundle.js
../node_modules/node-sass/bin/node-sass ./index.scss > ./bundle.css
