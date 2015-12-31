#!/bin/bash
set -o errexit
set -o nounset
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
__file="${__dir}/$(basename "${BASH_SOURCE[0]}")"

if [ "$#" -eq 0 ] ; then
  echo "Usage: step3_buildDockerContainer.sh tiles_dir"
  exit 1
fi

docker build -f ${__dir}/Dockerfile -t "freethenation/viewshed:data" $1
docker push freethenation/viewshed:data