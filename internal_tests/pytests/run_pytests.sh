#!/bin/bash

exit_script=1
remove_commands="\n"

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pytest_rel_path="internal_tests/pytests"
ush_dir=${script_dir%"$pytest_rel_path"}ush
export PYTHONPATH=$ush_dir:$PYTHONPATH

host=$HOSTNAME
minimum_pytest_env_file=$script_dir"/minimum_pytest."$host".sh"
if [ ! -e $minimum_pytest_env_file ]; then
    echo Cannot only run run_pytests.sh with minimum pytest environment file. Create minimum_pytest.$host.sh to run on this host
    exit
fi

source $minimum_pytest_env_file

ls $script_dir/*/__pycache__ &> /dev/null
ret=$?
if [ $ret == 0 ]; then
    echo -e "\n\nRemove all __pycache__ directories before running."
    remove_commands=${remove_commands}"\nrm -r $script_dir/*/__pycache__"
    exit_script=0
fi

ls $METPLUS_TEST_OUTPUT_BASE &> /dev/null
ret=$?
if [ $ret == 0 ]; then
    echo -e "\n\nRemove $METPLUS_TEST_OUTPUT_BASE before running tests."
    remove_commands=${remove_commands}"\nrm -rf $METPLUS_TEST_OUTPUT_BASE"
    exit_script=0
fi

if [ $exit_script == 0 ]; then
    echo -e $remove_commands
    exit
fi

all_good=0

cd $script_dir/config
pytest -c ../minimum_pytest.conf
if [ $? != 0 ]; then
    all_good=1
fi

cd $script_dir/grid_stat
pytest -c ../minimum_pytest.conf
if [ $? != 0 ]; then
    all_good=1
fi

cd $script_dir/logging
pytest -c ../minimum_pytest.conf
if [ $? != 0 ]; then
    all_good=1
fi

cd $script_dir/met_util
pytest -c ../minimum_pytest.conf
if [ $? != 0 ]; then
    all_good=1
fi

cd $script_dir/mtd
pytest -c ../minimum_pytest.conf
if [ $? != 0 ]; then
    all_good=1
fi

cd $script_dir/pcp_combine
pytest -c ../minimum_pytest.conf -c ./test1.conf
if [ $? != 0 ]; then
    all_good=1
fi

cd $script_dir/stat_analysis
pytest -c ../minimum_pytest.conf -c ./test_stat_analysis.conf
if [ $? != 0 ]; then
    all_good=1
fi

cd $script_dir/plotting/stat_analysis
pytest -c ../../minimum_pytest.conf -c ./test_stat_analysis.conf
if [ $? != 0 ]; then
    all_good=1
fi

cd $script_dir/plotting/make_plots
pytest -c ../../minimum_pytest.conf -c ./test_make_plots.conf
if [ $? != 0 ]; then
    all_good=1
fi

cd $script_dir/plotting/plot_util
pytest -c ../../minimum_pytest.conf
if [ $? != 0 ]; then
    all_good=1
fi

cd $script_dir/StringTemplateSubstitution
pytest -c ../minimum_pytest.conf
if [ $? != 0 ]; then
    all_good=1
fi

cd $script_dir/compare_gridded
pytest -c ../minimum_pytest.conf
if [ $? != 0 ]; then
    all_good=1
fi

cd $script_dir/time_util
pytest -c ../minimum_pytest.conf
if [ $? != 0 ]; then
    all_good=1
fi

cd $script_dir/pb2nc
pytest -c ../minimum_pytest.conf -c ./conf1
if [ $? != 0 ]; then
    all_good=1
fi

cd $script_dir/extract_tiles
python ./run_precondition.py >/dev/null 2>&1
pytest -c ../minimum_pytest.conf -c  ./extract_tiles_test.conf -c ./custom.conf
if [ $? != 0 ]; then
    all_good=1
fi


cd $script_dir/series_init
python ./run_cleanup.py
pytest -c ../minimum_pytest.conf -c ./series_init_test.conf -c ./custom.conf
if [ $? != 0 ]; then
    all_good=1
fi


if [ $all_good == 0 ]; then
    echo SUCCESS: All tests passed
else
    echo ERROR: Some tests failed
    exit 1
fi
