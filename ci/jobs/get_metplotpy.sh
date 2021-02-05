#! /bin/bash

pip3 install matplotlib
pip3 install scipy

# run manage externals to obtain METcalcpy
${DOCKER_WORK_DIR}/METplus/manage_externals/checkout_externals -e ${DOCKER_WORK_DIR}/METplus/ci/parm/Externals_metplotpy.cfg

pip3 install ${DOCKER_WORK_DIR}/METplotpy
