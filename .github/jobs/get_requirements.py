#! /usr/bin/env python3

# Used in GitHub Actions (in .github/actions/run_tests/entrypoint.sh)
# to obtain list of requirements from use case group

import os
import sys

import get_use_case_commands

# add METplus directory to path so the test suite can be found
METPLUS_TOP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir,
                                               os.pardir))
sys.path.insert(0, METPLUS_TOP_DIR)

from internal_tests.use_cases.metplus_use_case_suite import METplusUseCaseSuite

def main():
    all_requirements = set()
    categories, subset_list, compare = (
        get_use_case_commands.handle_command_line_args()
    )

    test_suite = METplusUseCaseSuite()
    test_suite.add_use_case_groups(categories, subset_list)

    for group_name, use_cases_by_req in test_suite.category_groups.items():
        for use_case_by_req in use_cases_by_req:
            for requirement in use_case_by_req.requirements:
                all_requirements.add(requirement)

    return list(all_requirements)

if __name__ == '__main__':
    all_requirements = main()
    print(','.join(all_requirements))
