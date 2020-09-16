#! /bin/bash

gempak_to_cf_location=https://dtcenter.org/sites/default/files/community-code/metplus/utilities/GempakToCF.jar

export GEMPAK_LOCATION=$OWNER_BUILD_DIR/input

echo mkdir -p ${GEMPAK_LOCATION}
mkdir -p ${GEMPAK_LOCATION}

cd ${GEMPAK_LOCATION}
echo Downloading $gempak_to_cf_location into ${GEMPAK_LOCATION}
curl -L -O $gempak_to_cf_location
