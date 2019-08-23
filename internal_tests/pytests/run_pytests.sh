#!/bin/bash

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pytest_rel_path="internal_tests/pytests"
ush_dir=${script_dir%"$pytest_rel_path"}ush
export PYTHONPATH=$ush_dir:$PYTHONPATH

cd $script_dir/config
pytest -c ../minimum_pytest.eyewall.conf
cd $script_dir/grid_stat
pytest -c ../minimum_pytest.eyewall.conf
cd $script_dir/logging
pytest -c ../minimum_pytest.eyewall.conf
cd $script_dir/met_util
pytest -c ../minimum_pytest.eyewall.conf
cd $script_dir/mtd
pytest -c ../minimum_pytest.eyewall.conf
cd $script_dir/pcp_combine
pytest -c ../minimum_pytest.eyewall.conf -c ./test1.conf
cd $script_dir/StringTemplateSubstitution
pytest -c ../minimum_pytest.eyewall.conf
cd $script_dir/compare_gridded
pytest -c ../minimum_pytest.eyewall.conf
cd $script_dir/time_util
pytest -c ../minimum_pytest.eyewall.conf
