#!/bin/bash

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pytest_rel_path="internal_tests/pytests"
ush_dir=${script_dir%"$pytest_rel_path"}ush
export PYTHONPATH=$ush_dir:$PYTHONPATH

# tc_pairs pytest takes approx. 20 minutes to run
cd tc_pairs
pytest -c ../minimum_pytest.eyewall.conf -c ./tc_pairs_wrapper_test.conf
