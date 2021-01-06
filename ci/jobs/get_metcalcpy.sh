#! /bin/bash

# run manage externals to obtain METcalcpy
${DOCKER_WORK_DIR}/METplus/manage_externals/checkout_externals -e ${DOCKER_WORK_DIR}/METplus/ci/parm/Externals.cfg
