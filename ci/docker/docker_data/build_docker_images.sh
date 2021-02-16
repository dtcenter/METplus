#!/bin/bash
# 
# Build METplus-Data Docker images for sample data tarballs
#=======================================================================
#
# This script pulls sample data tarfiles from:
#   https://dtcenter.ucar.edu/dfiles/code/METplus/METplus_Data/<version>
#
# Where <version> is specified using the required "-pull" command line
# option. It searches for tarfiles in that directory named
# "sample_data-<dataset name>.tgz". When the "-data" option is used,
# it only processes the specified list of datasets. Otherwise, it
# processes all datasets in that directory. For each dataset, it builds
# a Docker data volume.
#
# Each <version> directory must contain a file named
# "volume_mount_directories". Each line of that file is formatted as:
#   <dataset name>:<mount point directory>
# For example, "s2s:model_applications/s2s" indicates the directory
# that should be mounted for the s2s dataset. 
#
# When "-union" is used, it also builds a Docker data volume for all
# datasets in that directory. When "-push" is used, it pushes the
# resulting images to the specified DockerHub repository.
#
# See Usage statement below.
#
#=======================================================================

# Constants
SCRIPT_DIR=$(dirname $0)
PULL_URL="https://dtcenter.ucar.edu/dfiles/code/METplus/METplus_Data"
MOUNTPT_FILE="volume_mount_directories"
MOUNTPT_BASE="/data/input/METplus_Data"

#
# Usage statement for this script
#
function usage {
  cat << EOF

Usage: build_docker_images.sh
        -pull version
        [-data list]
        [-union]
        [-all]
        [-push repo]
        [-help]

        where:
          "-pull version" defines the version of the datasets to be pulled (required).
          "-data list" overrides the use of all datasets for this version with a comma-separated list (optional).
          "-union" also creates one data volume with all datasets for this version (optional).
          "-all" create data volumes from all available datasets for this version (optional).
          "-push repo" pushes the images to the specified DockerHub repository (optional).
          "-help" prints the usage statement.

  e.g. Pull from ${PULL_URL}/<version>
       Push to DockerHub <repo>:<version>-<data>

EOF

  exit 1
}

#
# Command runner utility function
#
function run_command {
  echo "RUNNING: $*"
  $*
  error=$?
  if [ ${error} -ne 0 ]; then
    echo "ERROR:"
    echo "ERROR: '$*' exited with status = ${error}"
    echo "ERROR:"
    exit ${error}
  fi
}

# Defaults for command line options
DO_UNION=0
DO_PUSH=0
DO_ALL=0

# Default for checking if using tagged version
TAGGED_VERSION=0

# Parse command line options
while true; do
  case "$1" in

    pull | -pull | --pull )
      VERSION=$2
      echo "Will pull data from ${PULL_URL}/${VERSION}"
      shift 2;;

    data | -data | --data )
      if [ -z ${PULL_DATA+x} ]; then
        PULL_DATA=$2
      else
        PULL_DATA="${PULL_DATA},$2"
      fi
      shift 2;;

    union | -union | --union )
      DO_UNION=1
      echo "Will create a data volume containing all input datasets."
      shift;;

    all | -all | --all )
      DO_ALL=1
      echo "Will create a data volume for each available input dataset."
      shift;;

    push | -push | --push )
      DO_PUSH=1
      PUSH_REPO=$2
      if [ -z ${PUSH_REPO} ]; then
        echo "ERROR: Must provide push repository after -push"
        usage
      fi
      echo "Will push images to DockerHub ${PUSH_REPO}."
      shift 2;;

    help | -help | --help )
      usage
      shift;;

    -* )
      echo "ERROR:"
      echo "ERROR: Unsupported option: $1"
      echo "ERROR:"
      usage;;

    * )
      break;;

  esac
done

# Check that the version has been specified
if [ -z ${VERSION+x} ]; then
  echo "ERROR:"
  echo "ERROR: The '-pull' option is required!"
  echo "ERROR:"
  usage
fi

# use VERSION in the Docker image tag unless using a tagged version
DOCKER_VERSION=${VERSION}

# check if using a tagged version (e.g v4.0)
# remove v from version if tagged version
if [[ ${VERSION} =~ ^v[0-9.]+$ ]]; then
    TAGGED_VERSION=1
    DOCKER_VERSION=${VERSION:1}
fi


# Define the target repository if necessary 
if [ -z ${PUSH_REPO+x} ]; then

  # Push tagged versions (e.g. v4.0) to metplus-data
  # and all others to metplus-data-dev
  if [ ${TAGGED_VERSION} == 1 ]; then
    PUSH_REPO="dtcenter/metplus-data"
  else
    PUSH_REPO="dtcenter/metplus-data-dev"
  fi
fi 

# Print the datasets to be processed
if [ -z ${PULL_DATA+x} ]; then
  echo "Will process all available datasets."
else
  echo "Will process the following datasets: ${PULL_DATA}"
fi

# Get list of available tarfiles
TARFILE_LIST=`curl -s ${PULL_URL}/${VERSION}/ | tr "<>" "\n" | egrep sample_data | egrep -v href`

if [[ ${TARFILE_LIST} == "" ]]; then
  echo "ERROR:"
  echo "ERROR: No tarfiles found in ${PULL_URL}/${VERSION}"
  echo "ERROR:"
  exit 1
fi

# Build separate image for each tarfile
for TARFILE in $TARFILE_LIST; do 

  # Build a list of all URL's
  CUR_URL="${PULL_URL}/${VERSION}/${TARFILE}"

  if [ -z ${URL_LIST+x} ]; then
    URL_LIST=${CUR_URL}
  else
    URL_LIST="${URL_LIST},${CUR_URL}"
  fi

  # Parse the current dataset name
  CUR_DATA=`echo $TARFILE | cut -d'-' -f2 | sed 's/.tgz//g'`

  if [ -z ${PULL_DATA+x} ] || [ `echo ${PULL_DATA} | grep ${CUR_DATA}` ] || [ ${DO_ALL} == 1 ]; then
    echo "Processing \"${TARFILE}\" ..." 
  else
    echo "Skipping \"${TARFILE}\" since \"${CUR_DATA}\" was not requested in \"-data\"." 
    continue 
  fi

  # Define the docker image name
  IMGNAME="${PUSH_REPO}:${DOCKER_VERSION}-${CUR_DATA}"

  # Determine the mount point
  MOUNTPT_URL="${PULL_URL}/${VERSION}/${MOUNTPT_FILE}"
  MOUNTPT=${MOUNTPT_BASE}/`curl -s ${MOUNTPT_URL} | grep "${CUR_DATA}:" | cut -d':' -f2`

  if [[ ${MOUNTPT} == "" ]]; then
    echo "ERROR:"
    echo "ERROR: No entry found for \"${CUR_DATA}\" found in ${MOUNTPT_URL}!"
    echo "ERROR:"
    exit 1
  fi

  echo
  echo "Building image ... ${IMGNAME}" 
  echo

  run_command docker build -t ${IMGNAME} ${SCRIPT_DIR} \
    --build-arg TARFILE_URL=${CUR_URL} \
    --build-arg MOUNTPT=${MOUNTPT}

  if [ ${DO_PUSH} == 1 ]; then
    echo
    echo "Pushing image ... ${IMGNAME}"
    echo
    # if DOCKER_USERNAME is set, then run docker login
    if [ ! -z ${DOCKER_USERNAME+x} ]; then
      echo "Logging into Docker ..."
      echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
    fi
    run_command docker push ${IMGNAME}

  fi

done

#
# Build one image for all tarfiles
#

if [ ${DO_UNION} == 1 ]; then

  IMGNAME="${PUSH_REPO}:${DOCKER_VERSION}"
  MOUNTPT="${MOUNTPT_BASE}"

  run_command docker build -t ${IMGNAME} ${SCRIPT_DIR} \
    --build-arg TARFILE_URL=${URL_LIST} \
    --build-arg MOUNTPT=${MOUNTPT}

  if [ ${DO_PUSH} == 1 ]; then
    echo
    echo "Pushing image ... ${IMGNAME}"
    echo

    run_command docker push ${IMGNAME}

  fi
fi

