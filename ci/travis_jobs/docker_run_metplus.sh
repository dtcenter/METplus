#!/bin/bash

ret=`docker run --rm -v ${OWNER_BUILD_DIR}:/metplus ${DOCKERHUB_TAG} /bin/bash -c "$1"`
if [ $ret != 0 ]; then
  exit $ret
else
  exit $2
fi
