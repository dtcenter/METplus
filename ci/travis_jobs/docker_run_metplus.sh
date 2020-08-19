#!/bin/bash

print 'In docker_run_metplus.sh, DOCKERHUB_TAG =', ${DOCKERHUB_TAG}

ret=`docker run --rm -v ${OWNER_BUILD_DIR}:/metplus ${DOCKERHUB_TAG} /bin/bash -c "$1"`

print "In docker_run_metplus.sh $1:", $1
print "In docker_run_metplus.sh $2:", $2
print "In docker_run_metplus.sh $ret:", $ret

#if [ $ret != 0 ]; then
#  exit $ret
#else
#  exit $2
#fi

exit 999
