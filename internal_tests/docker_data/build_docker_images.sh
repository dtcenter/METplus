#!/bin/bash

METPLUS_VERSION=3.1

for ASSET in $(cat metplus_sample_data); do
  IMGNAME="dtcenter/metplus-data:${METPLUS_VERSION}-`echo ${ASSET} | cut -d':' -f1`"
  TARFILE=`echo ${ASSET} | cut -d':' -f2`
  MOUNTPT=`echo ${ASSET} | cut -d':' -f3`

  echo
  echo "Building image ... ${IMGNAME}" 
  echo

  docker build -t ${IMGNAME} . \
    --build-arg TARFILE=${TARFILE} \
    --build-arg MOUNTPT=${MOUNTPT}

done
