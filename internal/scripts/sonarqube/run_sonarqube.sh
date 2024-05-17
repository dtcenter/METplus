#!/bin/bash
#
# Run SonarQube Source Code Analyzer for METplus
#=======================================================================
#
# This run_sonarqube.sh script will check out the specified version
# of METplus and run the SonarQube Source Code Analyzer on it.  First,
# go to the directory where you would like the SCA output written and
# then run:
#
#    git clone https://github.com/dtcenter/METplus
#    METplus/sonarqube/run_sonarqube.sh name
#
# Usage: run_sonarqube.sh name
#    Test the specified branched version of METplus:
#       run_sonarqube.sh {branch name}
#    Test the specified tagged version of METplus:
#       run_sonarqube.sh {tag name}
#
#=======================================================================

# Constants
GIT_REPO_NAME=METplus
GIT_REPO="https://github.com/dtcenter/${GIT_REPO_NAME}"

function usage {
  echo
  echo "USAGE: $(basename $0) name"
  echo "   where \"name\" specifies a branch, tag, or hash."
  echo
}

# Check for arguments
if [[ $# -lt 1 ]]; then usage; exit; fi

# Check that SONAR_TOKEN and SONAR_HOST_URL are defined
if [ -z ${SONAR_TOKEN} ]; then
  echo "ERROR: SONAR_TOKEN must be set"
  exit 1
fi
if [ -z ${SONAR_HOST_URL} ]; then
  echo "ERROR: SONAR_HOST_URL must be set"
  exit 1
fi

# Check that SONARQUBE_WRAPPER_BIN is defined
if [ -z ${SONARQUBE_WRAPPER_BIN} ]; then
  which build-wrapper-linux-x86-64 2> /dev/null
  if [ $? -eq 0 ]; then
    SONARQUBE_WRAPPER_BIN=$(which build-wrapper-linux-x86-64 2> /dev/null)
  else
    which build-wrapper 2> /dev/null
    if [ $? -eq 0 ]; then
      SONARQUBE_WRAPPER_BIN=$(which build-wrapper 2> /dev/null)
    else
      echo "ERROR: SONARQUBE_WRAPPER_BIN must be set"
      exit 1
    fi
  fi
fi
if [ ! -e ${SONARQUBE_WRAPPER_BIN} ]; then
  echo "ERROR: SONARQUBE_WRAPPER_BIN (${SONARQUBE_WRAPPER_BIN}) does not exist"
  exit 1
fi

# Check that SONARQUBE_SCANNER_BIN is defined
if [ -z ${SONARQUBE_SCANNER_BIN} ]; then
  which sonar-scanner 2> /dev/null
  if [ $? -eq 0 ]; then
    SONARQUBE_SCANNER_BIN=$(which sonar-scanner 2> /dev/null)
  else
    echo "ERROR: SONARQUBE_SCANNER_BIN must be set"
    exit 1
  fi
fi
if [ ! -e ${SONARQUBE_SCANNER_BIN} ]; then
  echo "ERROR: SONARQUBE_SCANNER_BIN (${SONARQUBE_SCANNER_BIN}) does not exist"
  exit 1
fi

# Sub-routine for running a command and checking return status
function run_command() {

  # Print the command being called
  echo "CALLING: $1"

  # Run the command and store the return status
  $1
  STATUS=$?

  # Check return status
  if [[ ${STATUS} -ne 0 ]]; then
     echo "ERROR: Command returned with non-zero status ($STATUS): $1"
     exit ${STATUS}
  fi

  return ${STATUS}
}

# Store the full path to the scripts directory
SCRIPT_DIR=`dirname $0`
if [[ ${0:0:1} != "/" ]]; then SCRIPT_DIR=$(pwd)/${SCRIPT_DIR}; fi 

# Clone repo into a sub-directory and checkout the requested version
REPO_DIR="${GIT_REPO_NAME}-${1}"

if [ -e ${REPO_DIR} ]; then
  run_command "rm -rf ${REPO_DIR}"
fi
run_command "git clone ${GIT_REPO} ${REPO_DIR}"
run_command "cd ${REPO_DIR}"
run_command "git checkout ${1}"

# Define the version string
SONAR_PROJECT_VERSION=$(cat metplus/VERSION)

SONAR_PROPERTIES=sonar-project.properties

# Configure the sonar-project.properties
[ -e $SONAR_PROPERTIES ] && rm $SONAR_PROPERTIES
sed -e "s|SONAR_PROJECT_VERSION|$SONAR_PROJECT_VERSION|" \
    -e "s|SONAR_HOST_URL|$SONAR_HOST_URL|" \
    -e "s|SONAR_TOKEN|$SONAR_TOKEN|" \
    -e "s|SONAR_BRANCH_NAME|${1}|" \
    $SCRIPT_DIR/$SONAR_PROPERTIES > $SONAR_PROPERTIES

# Run SonarQube scan for Python code
run_command "${SONARQUBE_SCANNER_BIN}/sonar-scanner"

