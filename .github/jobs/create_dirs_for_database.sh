#! /bin/bash

# Create directories used for use case that uses METviewer and METdataio
# Open up write permissions for these directories so that files can
# be written by METviewer Docker container.
# Called by .github/workflows/testing.yml

if [ -z "${RUNNER_WORKSPACE}" ]; then
    echo "ERROR: RUNNER_WORKSPACE env var must be set"
    exit 1
fi

mkdir -p $RUNNER_WORKSPACE/mysql
mkdir -p $RUNNER_WORKSPACE/output/metviewer
chmod a+w $RUNNER_WORKSPACE/mysql
chmod a+w $RUNNER_WORKSPACE/output/metviewer
