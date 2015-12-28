#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
__file="${__dir}/$(basename "${BASH_SOURCE[0]}")"
cd $__dir

set -x #log cmds
rm bundle.*
./node_modules/browserify/bin/cmd.js -t [ babelify --presets [ react ] ] index.js -o bundle.js
./node_modules/node-sass/bin/node-sass ./index.scss > bundle.css
