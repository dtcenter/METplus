#!/bin/bash

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

ush_dir=$script_dir"/../../ush"

export PYTHONPATH=$ush_dir:$PYTHONPATH

host=$HOSTNAME
test_env_file=$script_dir"/metplus_test_env."$host".sh"

if [ ! -e $test_env_file ]; then
    echo Cannot only run test_use_cases.py with an environment file. Create $test_env_file to run on this host
    exit
fi

source $test_env_file

python $script_dir/test_use_cases.py
