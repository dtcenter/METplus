#!/bin/bash

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pytest_rel_path="internal_tests/pytests"
ush_dir=${script_dir%"$pytest_rel_path"}ush
export PYTHONPATH=$ush_dir:$PYTHONPATH

host=$HOSTNAME
if [ ! -e $script_dir"/minimum_pytest."$host".conf" ]; then
    echo Cannot only run run_pytests.sh with minimum pytest config file. Create minimum_pytest.$host.conf to run on this host
    exit
fi

ls $script_dir/*/__pycache__ &> /dev/null
ret=$?
if [ $ret == 0 ]; then
    echo Remove all __pycache__ directories before running.
    echo rm -r $script_dir/*/__pycache__
    exit
fi


cd $script_dir/config
pytest -c ../minimum_pytest.$host.conf
cd $script_dir/grid_stat
pytest -c ../minimum_pytest.$host.conf
cd $script_dir/logging
pytest -c ../minimum_pytest.$host.conf
cd $script_dir/met_util
pytest -c ../minimum_pytest.$host.conf
cd $script_dir/mtd
pytest -c ../minimum_pytest.$host.conf
cd $script_dir/pcp_combine
pytest -c ../minimum_pytest.$host.conf -c ./test1.conf
cd $script_dir/stat_analysis
pytest -c ../minimum_pytest.$host.conf -c ./test_stat_analysis.conf
cd $script_dir/plotting/stat_analysis
pytest -c ../../minimum_pytest.$host.conf -c ./test_stat_analysis.conf
cd $script_dir/plotting/make_plots
pytest -c ../../minimum_pytest.$host.conf -c ./test_make_plots.conf
cd $script_dir/plotting/plot_util
pytest -c ../../minimum_pytest.$host.conf
cd $script_dir/StringTemplateSubstitution
pytest -c ../minimum_pytest.$host.conf
cd $script_dir/compare_gridded
pytest -c ../minimum_pytest.$host.conf
cd $script_dir/time_util
pytest -c ../minimum_pytest.$host.conf
cd $script_dir/pb2nc
pytest -c ../minimum_pytest.$host.conf -c ./conf1
cd $script_dir/extract_tiles
python ./run_precondition.py >/dev/null 2>&1
pytest -c ../minimum_pytest.$host.conf -c  ./extract_tiles_test.conf -c ./custom.conf
cd $script_dir/series_init
python ./run_cleanup.py
pytest -c ../minimum_pytest.$host.conf -c ./series_init_test.conf -c ./custom.conf
