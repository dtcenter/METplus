#!/bin/bash

# Constants
SONAR_PROPERTIES_DIR=internal/scripts/sonarqube
SONAR_PROPERTIES=sonar-project.properties

# Check that this is being run from the top-level METplus directory
if [ ! -e $SONAR_PROPERTIES_DIR/$SONAR_PROPERTIES ]; then
  echo "ERROR: ${0} -> must be run from the top-level METplus directory"
  exit 1
fi

# Check required environment variables
if [ -z ${SOURCE_BRANCH+x} ]; then
  echo "ERROR: ${0} -> \$SOURCE_BRANCH not defined!"
  exit 1
fi
if [ -z ${WD_REFERENCE_BRANCH+x} ]; then
  echo "ERROR: ${0} -> \$WD_REFERENCE_BRANCH not defined!"
  exit 1
fi
if [ -z ${SONAR_HOST_URL+x} ]; then
  echo "ERROR: ${0} -> \$SONAR_HOST_URL not defined!"
  exit 1
fi
if [ -z ${SONAR_TOKEN+x} ]; then
  echo "ERROR: ${0} -> \$SONAR_TOKEN not defined!"
  exit 1
fi

# Define the version string
SONAR_PROJECT_VERSION=$(cat metplus/VERSION)

#
# Define the $SONAR_REFERENCE_BRANCH as the
#   - Target of any requests
#   - Manual setting for workflow dispatch
#   - Source branch for any pushes (e.g. develop)
#
if [ "$GITHUB_EVENT_NAME" == "pull_request" ]; then
  export SONAR_REFERENCE_BRANCH=$GITHUB_BASE_REF
elif [ "$GITHUB_EVENT_NAME" == "workflow_dispatch" ]; then
  export SONAR_REFERENCE_BRANCH=$WD_REFERENCE_BRANCH
else
  export SONAR_REFERENCE_BRANCH=$SOURCE_BRANCH
fi

# Configure the sonar-project.properties
[ -e $SONAR_PROPERTIES ] && rm $SONAR_PROPERTIES
sed -e "s|SONAR_PROJECT_KEY|METplus-GHA|" \
    -e "s|SONAR_PROJECT_NAME|METplus GHA|" \
    -e "s|SONAR_PROJECT_VERSION|$SONAR_PROJECT_VERSION|" \
    -e "s|SONAR_HOST_URL|$SONAR_HOST_URL|" \
    -e "s|SONAR_TOKEN|$SONAR_TOKEN|" \
    -e "s|SONAR_BRANCH_NAME|$SOURCE_BRANCH|" \
    $SONAR_PROPERTIES_DIR/$SONAR_PROPERTIES > $SONAR_PROPERTIES

# Define new code when the source and reference branches differ
if [ "$SOURCE_BRANCH" != "$SONAR_REFERENCE_BRANCH" ]; then
  echo "sonar.newCode.referenceBranch=${SONAR_REFERENCE_BRANCH}" >> $SONAR_PROPERTIES
fi

echo "Contents of the $SONAR_PROPERTIES file:"
cat $SONAR_PROPERTIES

