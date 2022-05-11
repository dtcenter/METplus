#!/bin/bash
#
# Run nightly SonarQube scan
#=======================================================================
#
# This run_nightly.sh script calls the run_sonarqube.sh script.
# It is intented to be run nightly through cron. Output should be
# directed to the LOGFILE, per cron convention. To run this script, use
# the following commands:
#
#    git clone https://github.com/dtcenter/MET
#    MET/scripts/sosnarqube/run_nightly.sh name
#
# Usage: run_nightly.sh name
#    where "name" specifies a branch, tag, or hash
#
# For example, scan the develop branch:
#    run_nightly.sh develop
#
#=======================================================================

# Constants
#EMAIL_LIST="johnhg@ucar.edu hsoh@ucar.edu jpresto@ucar.edu linden@ucar.edu mccabe@ucar.edu"
EMAIL_LIST="johnhg@ucar.edu hsoh@ucar.edu mccabe@ucar.edu"
#EMAIL_LIST="hsoh@ucar.edu"
KEEP_DAYS=5

function usage {
  echo
  echo "USAGE: run_nightly.sh name"
  echo "   where \"name\" specifies a branch, tag, or hash."
  echo
}

# Check for arguments
if [ $# -lt 1 ]; then usage; exit 1; fi

# Store the full path to the scripts directory
SCRIPT_DIR=`dirname $0`
if [[ ${0:0:1} != "/" ]]; then SCRIPT_DIR=$(pwd)/${SCRIPT_DIR}; fi 

# Define the development environment
ENV_FILE=${SCRIPT_DIR}/../environment/development.`hostname`
if [[ ! -e ${ENV_FILE} ]]; then
  echo "$0: ERROR -> Development environment file missing: ${ENV_FILE}"
  exit 1
fi
source ${ENV_FILE}

SONARQUBE_WORK_DIR=${MET_PROJ_DIR}/MET_regression/sonarqube_METplus

# Delete old directories
find ${SONARQUBE_WORK_DIR} -mtime +${KEEP_DAYS} -name "NB*" | \
     xargs rm -rf

# Create and switch to a run directory
TODAY=`date +%Y%m%d`
YESTERDAY=`date -d "1 day ago" +%Y%m%d`
RUN_DIR=${SONARQUBE_WORK_DIR}/NB${TODAY}
[[ -e ${RUN_DIR} ]] && rm -rf ${RUN_DIR}
mkdir -p ${RUN_DIR}
cd ${RUN_DIR}

# Create a logfile
LOGFILE=${RUN_DIR}/run_sonarqube_${TODAY}.log

# Run scan and check for bad return status
${SCRIPT_DIR}/run_sonarqube.sh ${1} >& ${LOGFILE}
if [[ $? -ne 0 ]]; then
  echo "$0: The nightly SonarQube scan for METplus FAILED in `basename ${RUN_DIR}`." >> ${LOGFILE}
  cat ${LOGFILE} | mail -s "METplus SonarQube scan Failed for ${1} in `basename ${RUN_DIR}` (autogen msg)" ${EMAIL_LIST}
  exit 1
fi

# Convert SonarQube report from pdf to html

exit 0
