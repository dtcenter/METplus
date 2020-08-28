#!/bin/bash

METPLUS_VERSION=3.1

for ASSET in $(cat metplus_data_assets); do
  IMGNAME="dtcenter/metplus_data_`echo ${ASSET} | cut -d':' -f1`:${METPLUS_VERSION}"
  VERSION=`echo ${ASSET} | cut -d':' -f2`
  TARFILE=`echo ${ASSET} | cut -d':' -f3`

  echo
  echo "Building image ... ${IMGNAME}" 
  echo

  docker build -t ${IMGNAME} . \
    --build-arg VERSION=${VERSION} \
    --build-arg TARFILE=${TARFILE}
done
