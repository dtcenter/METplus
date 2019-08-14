#!/bin/bash

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pytest_rel_path="internal_tests/pytests"
ush_dir=${script_dir%"$pytest_rel_path"}ush
export PYTHONPATH=$ush_dir:$PYTHONPATH

cd config
pytest -c ../minimum_pytest.eyewall.conf
cd ../grid_stat
pytest -c ../minimum_pytest.eyewall.conf
cd ../logging
pytest -c ../minimum_pytest.eyewall.conf
cd ../met_util
pytest -c ../minimum_pytest.eyewall.conf
cd ../mtd
pytest -c ../minimum_pytest.eyewall.conf
cd ../pcp_combine
pytest -c ../minimum_pytest.eyewall.conf -c ./test1.conf
cd ../StringTemplateSubstitution
pytest -c ../minimum_pytest.eyewall.conf
cd ../compare_gridded
pytest -c ../minimum_pytest.eyewall.conf
