#! /bin/bash

pip3 install matplotlib
pip3 install scipy

basedir=$(dirname "$0")
work_dir=$basedir/../..

# run manage externals to obtain METcalcpy
${work_dir}/manage_externals/checkout_externals -e ${work_dir}/ci/parm/Externals_metcalcpy.cfg

pip3 install ${work_dir}/METcalcpy
