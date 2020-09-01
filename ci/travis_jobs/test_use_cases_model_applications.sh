# Test Use Cases in Model Applications
# Author: George McCabe 05/2020
# Usage: test_use_case_model_applications.sh [ <use_case_dir> ]
#   Where use_case_dir is the name of a directory under parm/use_cases/model_applications
#   Multiple values can be specified separated by a space
# About: Called by the .travis.yml file to run use cases found in parm/use_cases/model_applications/<use_case_dir>
# Note: Sample data tarball values must be updated if a new version is added to a release
#   If a new subdirectory is added to the repository, add a new tarball variable (with a
#   name ending with _var) and add a new block to the if/elif/else statement to pick the
#   correct use case tarball.

source ${OWNER_BUILD_DIR}/METplus/internal_tests/use_cases/metplus_test_env.docker.sh
export TRAVIS_OUTPUT_BASE=${METPLUS_TEST_OUTPUT_BASE/$DOCKER_WORK_DIR/$OWNER_BUILD_DIR}
export TRAVIS_INPUT_BASE=${METPLUS_TEST_INPUT_BASE/$DOCKER_WORK_DIR/$OWNER_BUILD_DIR}
export TRAVIS_PREV_OUTPUT_BASE=${METPLUS_TEST_PREV_OUTPUT_BASE/$DOCKER_WORK_DIR/$OWNER_BUILD_DIR}

echo 'Owner Build Dir:' ${OWNER_BUILD_DIR}
echo 'pwd:' `pwd`
echo mkdir -p ${TRAVIS_PREV_OUTPUT_BASE}
mkdir -p ${TRAVIS_PREV_OUTPUT_BASE}
echo mkdir -p ${TRAVIS_OUTPUT_BASE}
mkdir -p ${TRAVIS_OUTPUT_BASE}
echo mkdir -p ${TRAVIS_INPUT_BASE}
mkdir -p ${TRAVIS_INPUT_BASE}

cd ${OWNER_BUILD_DIR}/test.metplus.data

climate_tar=v3.1/sample_data-climate-3.1.tgz
convection_allowing_models_tar=v3.1/sample_data-convection_allowing_models-3.1.tgz
cryosphere_tar=v3.0/sample_data-cryosphere-3.0.tgz
medium_range_tar=v3.1/sample_data-medium_range-3.1.tgz
precipitation_tar=v3.0/sample_data-precipitation-3.0.tgz
s2s_tar=v3.1/sample_data-s2s-3.1.tgz
space_weather_tar=v3.0/sample_data-space_weather-3.0.tgz
tc_and_extra_tc_tar=v3.1/sample_data-tc_and_extra_tc-3.1.tgz

met_tool_wrapper_tarball=https://github.com/dtcenter/METplus/releases/download/v3.1/sample_data-met_tool_wrapper-3.1.tgz

gempak_to_cf_location=https://dtcenter.org/sites/default/files/community-code/metplus/utilities/GempakToCF.jar

# get sample data for all use case categories provided and add arguments to call to test script
test_args=''
for i in "$@"
do
  if [ -z "$i" ]; then
    continue
  fi

  echo Processing $i

  # get sample data tarball name
  if [ $i == "convection_allowing_models" ]; then
      tarball=$convection_allowing_models_tar
  elif [ $i == "climate" ]; then
      tarball=$climate_tar
  elif [ $i == "cryosphere" ]; then
      tarball=$cryosphere_tar
  elif [ ${i:0: -1} == "medium_range" ]; then
      tarball=$medium_range_tar
  elif [ $i == "precipitation" ]; then
      tarball=$precipitation_tar
  elif [ $i == "s2s" ]; then
      tarball=$s2s_tar
  elif [ $i == "space_weather" ]; then
      tarball=$space_weather_tar
  elif [ $i == "tc_and_extra_tc" ]; then
      tarball=$tc_and_extra_tc_tar
  else
      echo Invalid model_applications directory specified: $i
      exit 1
  fi

  echo Downloading $tarball
  echo curl -L -O https://github.com/dtcenter/METplus/releases/download/${tarball}
  curl -L -O https://github.com/dtcenter/METplus/releases/download/${tarball}

  echo file basename $tarball
  tarball_basename=`basename $tarball`
  echo `file $tarball_basename`

  echo tar xfzp `basename $tarball`
  tar xfzp `basename $tarball`

  test_args=${test_args}" --"${i}
done

# get met_test data because some cases use this data still
echo Downloading $met_tool_wrapper_tarball
echo curl -L -O $met_tool_wrapper_tarball
curl -L -O $met_tool_wrapper_tarball

# untar all tarballs
echo tar xfzp `basename $met_tool_wrapper_tarball`
tar xfzp `basename $met_tool_wrapper_tarball`

# get GempakToCF jar file in case any use cases use GEMPAK data
echo Downloading $gempak_to_cf_location
echo curl -L -O $gempak_to_cf_location
curl -L -O $gempak_to_cf_location

${TRAVIS_BUILD_DIR}/ci/travis_jobs/docker_setup.sh

echo Run tests...

if [ $i == "medium_range3" ]; then

  echo medium_range3
  echo TRAVIS_BUILD_DIR ${TRAVIS_BUILD_DIR}
  echo DOCKER_WORK_DIR ${DOCKER_WORK_DIR}
  echo calling docker_run_metplus
  
# use docker_run_metplus.sh
  ${TRAVIS_BUILD_DIR}/ci/travis_jobs/docker_run_metplus.sh "${DOCKER_WORK_DIR}/METplus/ci/travis_jobs/get_pygrib.sh; pip3 install metpy; /metplus/METplus/internal_tests/use_cases/run_test_use_cases.sh docker --config model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_IVT.conf,user_env_vars.MET_PYTHON_EXE=python3" $returncode
returncode=$?

else
  docker run --rm -v ${OWNER_BUILD_DIR}:/metplus ${DOCKERHUB_TAG} /bin/bash /metplus/METplus/internal_tests/use_cases/run_test_use_cases.sh docker ${test_args}
  returncode=$?
fi

echo Tests completed.
# Dump the output directories from running METplus
ls -alR ${OWNER_BUILD_DIR}/test-use-case-output

# Dump and see how much space is left on Travis disk.
df -h

exit $returncode
