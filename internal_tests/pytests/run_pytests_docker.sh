#!/bin/bash

# NOTE: THIS script is meant to ONLY be run within a METplus docker container.
# It will not work as-is outside of a docker container.

# automate with here docs or expect script
# https://stackoverflow.com/questions/2500436/how-does-cat-eof-work-in-bash
# https://en.wikipedia.org/wiki/Here_document#Unix_shells

# ${BASH_SOURCE[0]} is /metplus/METplus/internal_tests/pytests/docker_run_pytests.sh
# $script_dir is /metplus/METplus/internal_tests/pytests
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pytest_rel_path="internal_tests/pytests"
ush_dir=${script_dir%"$pytest_rel_path"}ush
# note: PYTHONPATH must be set here or passed in with -e in docker run command.
# else the PYTHONPATH will not be set, since this is not run with login terminal.
export PYTHONPATH=$ush_dir:$PYTHONPATH

# There will be NO artifacts on a new Travis machine or Docker Container,
# since they are newly provisioned each time a tests is run.
# Search from METplus directory and remove the pytest 
# artifacts  __pycache__ directories.
# Deletes the shortest match of $pytest_rel_path from back of $script_dir
metplus_base=${script_dir%"$pytest_rel_path"}
echo "${metplus_base}" | grep "METplus" >/dev/null 2>&1
ret=$?
echo -e "\nSearching METplus directory: ${metplus_base}"
if [ $ret == 0 ]; then
    echo -e "Removing any __pycache__ directories before running.\n"
    find ${metplus_base} -type d -name __pycache__
    find ${metplus_base} -type d -name __pycache__ -prune -exec rm -rf {} \;
else
    echo -e "METplus is not in the path, not sure why, exiting ...\n"
    exit 1
fi


###host="dockercontainer"
###if [ ! -e $script_dir"/minimum_pytest."$host".sh" ]; then
###    echo Cannot only run run_pytests.sh with minimum pytest config file. Create minimum_pytest.$host.sh to run on this host
    #exit
###fi

#source $minimum_pytest_env_file
#source minimum_pytest.docker.sh
source ${script_dir}/minimum_pytest.docker.sh


# This is NOT needed since is a NEW TRAVIS MACHINE, there will be no output.
#ls $METPLUS_TEST_OUTPUT_BASE &> /dev/null
#ret=$?
#if [ $ret == 0 ]; then
#    echo -e "\n\nRemove $METPLUS_TEST_OUTPUT_BASE before running tests."
#    echo It wants me exit to remove the directory ... but I WILL NOT.
    #exit
#fi

all_good=0
failure_output=""

function run_pytest_and_check() {
  echo -e "\ncd $script_dir/$1"
  cd $script_dir/$1
  cmd="pytest -c $script_dir/minimum_pytest.conf ${@:2}"
  echo $cmd
  $cmd
  ret=$?
  if [ $ret != 0 ]; then
      all_good=1
      failure_output=${failure_output}"\nERROR: pytest $1 failed."
  fi
}

# for METplus docker container just running a subset of pytests as
# a proof of concept.
run_pytest_and_check config
#cd $script_dir/config
#pytest -c ../minimum_pytest.$host.sh
run_pytest_and_check check_metplus_python_version
run_pytest_and_check logging
run_pytest_and_check met_util
run_pytest_and_check StringTemplateSubstitution
run_pytest_and_check pcp_combine -c ./test1.conf


if [ $all_good == 0 ]; then
    echo SUCCESS: All tests passed
else
    echo -e $failure_output
    exit 1
fi

