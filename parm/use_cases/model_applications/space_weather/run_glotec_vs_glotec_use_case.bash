#!/bin/bash
#
# This script runs a contributed METplus use case with a specified use case config file and user config file
# In particular, it illustrates how to run the glotec_vs_glotec use case on Irma

# NOTE: Before running METplus, the py3.6.3 python environment must be activated:
# /d1/jvigh/UTILITIES/miniconda/bin/conda activate py3.6.3

HOST=`hostname`

# Specify the project base dir (machine-dependent)
if [[ ${HOST} == "dakota" ]] 
then
   PROJECT_BASE_PATH="/d2/jvigh/PROJECTS"
fi

if [[ ${HOST} == "irma" ]] 
then
   PROJECT_BASE_PATH="/d1/jvigh/PROJECTS/VX/SWPC"
fi


# Specify the use case type
USE_CASE_TYPE="model_applications"

# Specify the use case group
USE_CASE_GROUP="space_weather"

# Specify the use case name
USE_CASE_NAME="glotec_vs_glotec"


# Specify the directory for the METplus installation to use
#METPLUS_VERSION="METplus_feature_281_py_embed_parm"   # was used for the APIK S2S use case
METPLUS_VERSION="METplus-3.0-beta1"   		       # a pre-release version https://github.com/NCAR/METplus/releases


# Set the path to the version of METplus you will run 
# Normally, this should be a release version of METplus obtained from GitHub, but if using beta capabilities, point to the develop branch of a feature branch 
#METPLUS_BASE_DIR="/d1/jvigh/UTILITIES/METplus-2.1.1"
METPLUS_BASE_PATH="/d1/jvigh/UTILITIES/${METPLUS_VERSION}"


# Specify the location of the METplus local user config file 
LOCAL_USER_CONFIG_PATH="/d1/jvigh/UTILITIES/LOCAL_USER_CONFIG"

# Specify the name of the METplus local user config file
LOCAL_USER_CONFIG_FILENAME="swpc-cwdp.conf"


# Specify the location of the actual METplus use cases
USE_CASE_CONFIG_PATH=${PROJECT_BASE_PATH}/METplus/parm/use_cases/${USE_CASE_TYPE}/${USE_CASE_GROUP}
#/d1/jvigh/PROJECTS/VX/SWPC/METplus/parm/use_cases/model_applications/space_weather


# Specify the use case config filename
USE_CASE_CONFIG_FILENAME="${USE_CASE_NAME}.conf"


# Now run the METplus use case
echo "${METPLUS_BASE_PATH}/ush/master_metplus.py -c ${LOCAL_USER_CONFIG_PATH}/${LOCAL_USER_CONFIG_FILENAME} -c ${USE_CASE_CONFIG_PATH}/${USE_CASE_CONFIG_FILENAME}" 
${METPLUS_BASE_PATH}/ush/master_metplus.py -c ${LOCAL_USER_CONFIG_PATH}/${LOCAL_USER_CONFIG_FILENAME} -c ${USE_CASE_CONFIG_PATH}/${USE_CASE_CONFIG_FILENAME}

# NOTE: the above should expand out to the following:
#/d1/jvigh/UTILITIES/METplus-3.0-beta1/ush/master_metplus.py -c /d1/jvigh/UTILITIES/LOCAL_USER_CONFIG/swpc-cwdp.conf -c /d1/jvigh/PROJECTS/VX/SWPC/METplus/parm/use_cases/model_applications/space_weather/glotec_vs_glotec.conf
