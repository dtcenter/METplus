#!/bin/bash

ret=`docker run --rm -v ${OWNER_BUILD_DIR}:/metplus ${DOCKERHUB_TAG} /bin/bash -c "$1"`

echo "docker run $1" $1
echo "docker run $ret" $ret

if [ $ret != 0 ]; then
  exit $ret
else
  exit $2
fi
