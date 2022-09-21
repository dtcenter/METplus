#!/bin/bash
#
# Run SonarQube Source Code Analyzer on a specified revision of MET
#=======================================================================
#
# This run_sonarqube.sh script will check out the specified version
# of MET and run the SonarQube Source Code Analyzer on it.  First,
# go to the directory where you would like the SCA output written and
# then run:
#
#    git clone https://github.com/dtcenter/METplus
#    METplus/internal/scripts/sonarqube/run_sonarqube.sh name
#
# Usage: run_sonarqube.sh name
#    Test the specified branched version of MET:
#       run_sonarqube.sh {branch name}
#    Test the specified tagged version of MET:
#       run_sonarqube.sh {tag name}
#
#=======================================================================

# Constants
GIT_REPO="https://github.com/dtcenter/METplus"

function usage {
        echo
        echo "USAGE: $(basename $0) name"
        echo "   where \"name\" specifies a branch, tag, or hash."
        echo
}

# Check for arguments
if [[ $# -lt 1 ]]; then usage; exit; fi

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
REPO_DIR="METplus-${1}"

if [ -e ${REPO_DIR} ]; then
  run_command "rm -rf ${REPO_DIR}"
fi
run_command "git clone ${GIT_REPO} ${REPO_DIR}"
run_command "cd ${REPO_DIR}"
run_command "git checkout ${1}"

SONAR_PROPERTIES=sonar-project.properties

# Copy sonar-project.properties for Python code
[ -e $SONAR_PROPERTIES ] && rm $SONAR_PROPERTIES
cp -p $SCRIPT_DIR/sonar-project.properties $SONAR_PROPERTIES

# Run SonarQube scan for Python code
run_command "${SONARQUBE_SCANNER_BIN}/sonar-scanner"

# Run SonarQube report generator to make a PDF file
#TODAY=`date +%Y%m%d`
