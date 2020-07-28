#!/bin/bash

exit_script=1
remove_commands="\n"

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pytest_rel_path="internal_tests/pytests"
ush_dir=${script_dir%"$pytest_rel_path"}ush
metplus_dir=${script_dir%"$pytest_rel_path"}
export PYTHONPATH=$metplus_dir:$ush_dir:$PYTHONPATH

host=$1
if [ -z "$host" ]; then
    host=$HOSTNAME
fi

minimum_pytest_env_file=$script_dir"/minimum_pytest."$host".sh"
if [ ! -e $minimum_pytest_env_file ]; then
    echo Cannot only run run_pytests.sh with minimum pytest environment file. Create minimum_pytest.$host.sh to run on this host
    exit 1
fi

source $minimum_pytest_env_file

ls $script_dir/*/__pycache__ &> /dev/null
ret=$?
if [ $ret == 0 ]; then
    echo -e "\n\nRemove all __pycache__ directories before running."
    remove_commands=${remove_commands}"\nrm -r $script_dir/*/__pycache__"
    exit_script=0
fi

ls $script_dir/*/*/__pycache__ &> /dev/null
ret=$?
if [ $ret == 0 ]; then
    echo -e "\n\nRemove all __pycache__ directories before running."
    remove_commands=${remove_commands}"\nrm -r $script_dir/*/*/__pycache__"
    exit_script=0
fi

[ "$(ls -A $METPLUS_TEST_OUTPUT_BASE)" ]
ret=$?
if [ $ret == 0 ]; then
    echo -e "\n\nRemove all finds under $METPLUS_TEST_OUTPUT_BASE before running tests."
    echo Exiting...
    exit 1
fi

if [ "$remove_commands" != "\n" ]; then
    echo -e $remove_commands

    echo -e "\nWould you like to run these remove commands now? (y/n)"
    read confirm_remove

    if [ "${confirm_remove:0:1}" == 'y' ]; then
        rm -r $script_dir/*/__pycache__ &> /dev/null
        rm -r $script_dir/*/*/__pycache__ &> /dev/null
        exit_script=1
    fi
fi


if [ $exit_script == 0 ]; then
    exit 1
fi

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

run_pytest_and_check config
run_pytest_and_check metplus_check
run_pytest_and_check grid_stat
run_pytest_and_check logging
run_pytest_and_check met_util
run_pytest_and_check mtd
run_pytest_and_check pcp_combine -c ./test1.conf
run_pytest_and_check stat_analysis -c ./test_stat_analysis.conf
run_pytest_and_check StringTemplateSubstitution
run_pytest_and_check compare_gridded
run_pytest_and_check regrid_data_plane
run_pytest_and_check point2grid 
run_pytest_and_check time_util
run_pytest_and_check series_lead
run_pytest_and_check pb2nc -c ./conf1

#cd $script_dir/extract_tiles
#python ./run_precondition.py >/dev/null 2>&1
#run_pytest_and_check extract_tiles -c  ./extract_tiles_test.conf -c ./custom.conf
#python ./run_cleanup.py

#run_pytest_and_check series_init -c ./series_init_test.conf -c ./custom.conf

if [ -z "$METPLUS_DISABLE_PLOT_WRAPPERS" ]; then
    echo Running plot wrapper tests
    run_pytest_and_check plotting/stat_analysis -c ./test_stat_analysis.conf
    run_pytest_and_check plotting/make_plots -c ./test_make_plots.conf
    run_pytest_and_check plotting/plot_util
else
    echo WARNING: Skipping plotting tests. Unset METPLUS_DISABLE_PLOT_WRAPPERS to run them.
fi

if [ $all_good == 0 ]; then
    echo SUCCESS: All tests passed
else
    echo -e $failure_output
    exit 1
fi
