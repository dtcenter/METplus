#!/bin/bash
# 
# Build METplus-Data Docker images for sample data tarballs
#=======================================================================
#
# This script reads the metplus_sample_data file as input.
# For each entry, formatted as follows:
#   <dataset name>:<tarfile>:<path to data volume mount point>
# It creates a Docker data volume image named:
#   dtcenter/metplus-data:<version>-<dataset name>
#
# For example, the metplus_sample_data entry:
#   s2s:develop/sample_data-s2s.tgz:/data/input/METplus_Data/model_applications/s2s
# Creates an image named:
#   dtcenter/metplus-data:develop-s2s
#
# If the optional -push command line option is used, all images created
# are automatically pushed to DockerHub.
#
# Usage: build_docker_images.sh [-version name] [-push]
#   where -version name overrides the default METplus version (develop)
#         -push pushes the images to DockerHub
#
#=======================================================================

# Defaults for command line options
METPLUS_VERSION=develop
DO_PUSH=0

# Process arguments
for ARG in "$@"; do

  # Pushing to DockerHub
  if [ $ARG == "push" -o $ARG == "-push" -o $ARG == "--push" ]; then
    DO_PUSH=1
    echo "Will push images to DockerHub."

  # METplus Version
  elif [ $ARG == "version" -o $ARG == "-version" -o $ARG == "--version" ]; then
    shift
    METPLUS_VERSION=$1
    echo "Will create images for METPLUS_VERSION = ${METPLUS_VERSION}."
  fi

done

# Script directory
SCRIPT_DIR=$(dirname $0)

# Loop over data assets
for ASSET in $(cat ${SCRIPT_DIR}/metplus_sample_data); do

  IMGNAME="dtcenter/metplus-data:${METPLUS_VERSION}-`echo ${ASSET} | cut -d':' -f1`"
  TARFILE=`echo ${ASSET} | cut -d':' -f2`
  MOUNTPT=`echo ${ASSET} | cut -d':' -f3`

  echo
  echo "Building image ... ${IMGNAME}" 
  echo

  docker build -t ${IMGNAME} . \
    --build-arg TARFILE=${TARFILE} \
    --build-arg MOUNTPT=${MOUNTPT}

  if [ ${DO_PUSH} == 1 ]; then
    echo
    echo "Pushing image ... ${IMGNAME}"
    echo

    docker push ${IMGNAME} 

  fi

done

