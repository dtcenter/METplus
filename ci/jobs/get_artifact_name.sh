#! /bin/bash

# Run by GitHub Actions (in .github/workflows/main.yml and
# ci/actions/run_tests/entrypoint.sh) to get properly
# formatted artifact name for use case output

artifact_name=$1
# strip of :NEW if found at end of name
if [ ${artifact_name: -4} == ":NEW" ]; then
  artifact_name=${artifact_name:0: -4}
fi
artifact_name=`echo $artifact_name | tr , _`
artifact_name=`echo $artifact_name | tr : _`
artifact_name=`echo $artifact_name | tr + p`
artifact_name=use_cases_${artifact_name}
echo $artifact_name
