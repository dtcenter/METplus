#!/usr/bin/env python3

import sys
import re

import get_data_volumes
import use_cases_list

# read command line arguments to determine which use cases to run
if sys.argv < 2:
    print("No use cases specified")
    sys.exit(1)

# split up categories by & or ,
categories = sys.argv[1]
categories_list = re.split('[,&]', categories)

# get subset values if specified
#if sys.argv > 2:
#    subset = sys.argv[2]
#    # if X-Y, get range of values
#    if re.match(r''
    
# get data volumes
volumes_from = get_data_volumes.main(categories_list)

# run use cases
all_use_cases = use_cases_list.METplusUseCaseSuite()
all_use_cases.add_use_case_groups(categories)
#${TRAVIS_BUILD_DIR}/ci/travis_jobs/docker_run_metplus.sh "${DOCKER_WORK_DIR}/METplus/internal_tests/use_cases/run_test_use_cases.sh docker --met_tool_wrapper" $returncode "$VOLUMES"
