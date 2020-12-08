#!/usr/bin/env python3
"""! Utilities to set up and run use cases.
"""

import sys
import os
import re
from os.path import dirname, realpath

# add metplus directory to path so the utilities can be found
sys.path.insert(0, os.path.join(os.path.abspath(dirname(__file__)),
                                os.pardir,
                                os.pardir))
from metplus.util.met_util import subset_list

class METplusUseCase:
    """! Contains name of use case and a list of configuration command line
    arguments that are used to run the use case.
    """

    def __init__(self, name, config_args):
        """! Define a new use case.

        @param name String identifier of the use case, typically the name of
        the conf file used for the case with suffix .conf removed
        @oaram config_args List of configuration arguments that are used to
        run the use case. Value can also be a single config file or a
         comma-separated list of config arguments
        """
        self.name = name
        if isinstance(config_args, str):
            config_args = config_args.split(',')

        self.config_args = config_args

    def add_config_arg(self, config_arg):
        """! Add single configuration argument to use case

        @param config_arg configuration argument to add
        """
        self.config_args.append(config_arg)

    def print(self, indent=0, index=None):
        """! Prints the name of the use case and a list of the command line
        arguments used to run it.

        @param indent (Optional) Number of spaces to indent output. Defaults to
         0. Config argument list is indented by twice the value of indent
        @param index (Optional) value to display before the use case, typically
         the number of the use case in the group
        """
        padding = indent * ' '
        arg_indent = padding * 2
        if index is not None:
            padding = f'{padding}{index}: '
        print(f"{padding}{self.name}: ")
        for config_arg in self.config_args:
            print(f'{arg_indent}{config_arg}')


class METplusUseCasesByRequirement:
    """! Defines a group of use cases that share the same additional python
    package dependencies.
    """

    PYTHON_REQUIREMENTS = {
        'netCDF4': 'pip3 install netCDF4',
        'cartopy': 'ci/jobs/get_cartopy.sh',
        'pygrib': 'ci/jobs/get_pygrib.sh',
        'h5py': 'pip3 install h5py',
        'matplotlib': 'pip3 install matplotlib',
        'metpy': 'pip3 install metpy',
    }
    """! dictionary of extra python packages to
    install for certain use cases the keys are name of the package and the
    value is the command or function to call to obtain the dependency.
     Note: The get_* functions include yum commands to install applications
      needed to build the python packages. yum is not available on every OS
    """

    def __init__(self, requirements=None):
        """! Create empty list of requirements and use cases (METplusUseCase)

        @param requirements (Optional) List of python package requirements
        @param use_cases (Optional) List of METplusUseCase
        """
        self.requirements = []
        self.add_requirements(requirements)
        self.use_cases = []

    def add_requirements(self, requirements):
        """! Add list of requirements for group of use cases

        @param requirements List of python packages that are required to run
         the group of use cases. Also accepts a single package name as a string
        """
        if requirements is None:
            return

        if isinstance(requirements, str):
            requirements = [requirements]

        self.requirements.extend(requirements)

    def add_use_case(self, use_case):
        """! Add new METplusUseCase to list

        @raises TypeError
        @param use_case METplusUseCase to add
        """
        if not isinstance(use_case, METplusUseCase):
            raise TypeError()

        self.use_cases.append(use_case)

    def has_same_requirements(self, requirements):
        """! Checks if the requirement list set for this group of use cases
        contains all of the same items as the list provided to the function

        @param requirements List of python dependencies to compare to the
         stored list
        @returns True if all items in the lists are the same, False if not.
        """
        if len(self.requirements) != len(requirements):
            return False

        if sorted(self.requirements) != sorted(requirements):
            return False

        return True

    def has_use_cases(self):
        """! Check if any use cases are in the list

        @returns True if there are any use cases, False if there are none
        """
        if not self.use_cases:
            return False
        return True

    def print(self, indent=0, start_index=0):
        """! Outputs list of requirements and list of use cases

        @param indent (Optional) Number of spaces to indent output. Defaults to
         0. Config argument list is indented by twice the value of indent
        """
        padding = indent * ' '

        if self.requirements:
            requirements_list = ','.join(self.requirements)
        else:
            requirements_list = "No additional requirements"

        print(f"{padding}Requirements: {requirements_list}")

        for index, use_case in enumerate(self.use_cases):
            use_case.print(indent*2, index=index+start_index+1)
        print()


class METplusUseCaseSuite:
    """! Suite of METplus use cases containing functions to get all use cases
         for a given sub-category, add a group of use cases with a subset of
         sub-category use cases or multiple sub-categories, and install
         additional python packages needed to run certain use cases
    """

    def __init__(self):
        """! Create empty dictionary to store groups of use cases. Keys are
        the name of the category group (i.e. medium_range-group1 or
        s2s&space_weather-group0) and value is a list of
        METplusUseCasesByRequirement
        """
        self.category_groups = {}
        self.all_cases, self.num_cases = parse_all_use_cases_file()

    def add_category_group(self, name, cases_by_requirement):
        """! Add new group of use cases to the test suite
        @param name Identifier of use case group, typically named by the
         category of use cases (or categories separated by &) and an index
         identifier of the group separated by '-group' i.e. medium_range-group1
         or s2s&space_weather-group0
        @param cases_by_requirement List of METplusUseCasesByRequirement
        """
        if name in self.category_groups.keys():
            raise KeyError(f"ERROR: Group name already exists: {name}")

        self.category_groups[name] = cases_by_requirement

    def print(self, indent=2):
        """! Outputs all use cases that have been added to the suite

        @param indent (Optional) Number of spaces to indent output. Defaults to
         2. Config argument list is indented by twice the value of indent
        """
        for name, use_cases_by_req_list in self.category_groups.items():
            print(f'Category Group: {name}')
            start_index = 0
            for use_cases_by_req in use_cases_by_req_list:
                use_cases_by_req.print(indent, start_index=start_index)
                start_index += len(use_cases_by_req.use_cases)
            print()

    def get_total_cases(self):
        """! Total count of all use cases added to the suite in all groups

        @returns Integer number of use cases
        """
        total = 0
        for _, use_cases_list in self.category_groups.items():
            for use_case_group in use_cases_list:
                total += len(use_case_group.use_cases)

        return total

    def add_use_case_groups(self, categories, case_slice=None):
        """! Obtain use cases from a category or list of categories and
        optionally add a subset of the use cases to the test suite. Note: if
        multiple categories are specified, using the slice functionality to
        get a subset of cases will be applied to the full list of cases found.

        @param categories String or list of strings that define use case
        categories that correspond to the data volume used by the case
        @param case_slice (Optional) Used to subset the use case lists that
         are obtained from the categories. Can be a single integer
         that is the index into the list or a slice function call, i.e.
         slice(0,4,1) to obtain every use case from 0-3. Defaults to None
         which gets all of the use cases found.
        """
        if not isinstance(categories, list):
            # split category list by comma or ampersand
            categories = re.split('[,&]', categories)

        use_cases_list = []
        for category in categories:
            use_cases_list.extend(self.all_cases[category])

        use_cases_to_run = subset_list(use_cases_list, case_slice)

        self.add_use_case_group('&'.join(categories),
                                use_cases=use_cases_to_run,
                                )

    def add_use_case_group(self, category, use_cases):
        """! Obtains the name of the next group based on the category, then
        adds the lists of use cases to the category group.

        @param category name of the data volume(s) for the use cases. Multiple
         categories are separated by &. Resulting key of new category group
         will be named {category}-group<n> where <n> is the next integer value
         for the group (starts with 0 and increments for each repeat instance
         of category)
        @param use_cases List of use cases to add.
        """
        group_name = self._get_next_group_name(category)

        group_list = _get_use_case_list(use_cases)

        self.add_category_group(group_name, group_list)

    def _get_next_group_name(self, category):
        """! Builds name of group based on category. Groups are named
         {category}-group<n> where <n> is an integer. First instance of
         category will be named {category}-group0. Each repeat instance of
         category will increment the value of <n>

         @param category String identifier of use case group, typically named
          after the data volume required to run the use cases. If multiple data
          volumes are required, category is a list of data volumes separated by
          &. Examples: precipitation or s2s&space_weather
         @returns generated name of category group
        """
        groups = [group for group in self.category_groups
                  if category in group]
        if not groups:
            next_group_name = f'{category}-group0'
        else:
            highest_group_num = max([group.split('-group')[-1]
                                     for group in groups])
            next_num = int(highest_group_num) + 1
            next_group_name = f'{category}-group{next_num}'

        return next_group_name

def _get_use_case_list(use_cases):
    """! Adds each use case to the appropriate METplusUseCasesByRequirement
    based on the extra python package requirements. Use cases that have no
    additional requirements listed are added to an object with no
    requirements. Use cases with requirements defined are grouped together
    if they contain an identical list of dependencies.

    @param use_cases List of use cases
    """
    use_cases_list = []

    if not isinstance(use_cases, list):
        use_cases = [use_cases]

    # add complex cases
    for use_case in use_cases:
        new_use_case = METplusUseCase(use_case['name'],
                                      use_case['config_args'])

        # check existing use cases by requirement to see if
        # case with the same requirements exists
        requirements = use_case['requirements']
        found = False
        for use_cases_by_req in use_cases_list:
            # if found, add use case
            if use_cases_by_req.has_same_requirements(requirements):
                use_cases_by_req.add_use_case(new_use_case)
                found = True
                break

        # otherwise create new use cases by requirements object
        if not found:
            use_cases_by_req = METplusUseCasesByRequirement(requirements)
            use_cases_by_req.add_use_case(new_use_case)

            # add new use case to list of use cases by requirement
            use_cases_list.append(use_cases_by_req)

    return use_cases_list

def _extract_category_lists(lines):
    """! Look for categories (lines that start with Category). Group the
    lines by use case category.
    @param lines List of all lines from the file
    @returns Dictionary with category name as key and list of use cases as the
    value
    """
    header_indices = [i for i, value in enumerate(lines)
                      if value.startswith('Category')]

    category_lists = []
    for idx, header_index in enumerate(header_indices[:-1]):
        start_idx = header_index
        end_idx = header_indices[idx+1]
        category_lists.append(lines[start_idx:end_idx])

    last_idx = header_indices[-1]
    category_lists.append(lines[last_idx:])

    category_dict = {}
    # extract category name to use as key in output dictionary
    # value will contain a list of the rest of the lines
    for category_list in category_lists:
        # first line contains category name after 'Category:'
        # so get text after : and strip off whitespace
        category = category_list[0].split(':')[1].strip()
        if category in category_dict.keys():
            raise KeyError(f'Duplicate category in use cases file: {category}')

        # remove first item in list that contains the category name
        use_case_list = category_list[1:]
        # remove empty lines and commented out lines
        use_case_list = [use_case for use_case in use_case_list
                         if use_case.strip() and
                         not use_case.strip().startswith('#')]
        category_dict[category] = use_case_list

    return category_dict

def parse_all_use_cases_file():
    """! Read lines the "all use cases" text file and pull out the use cases
    """
    filename = os.path.join(dirname(realpath(__file__)),
                            'all_use_cases.txt')
    with open(filename, 'r') as file_handle:
        lines = file_handle.readlines()

    # pull out use cases by category
    category_dict = _extract_category_lists(lines)

    all_cases = {}
    num_cases = 0
    # parse each set of use cases for given category
    for category, use_case_list in category_dict.items():
        all_cases[category] = []
        for use_case in use_case_list:
            name, *rest = use_case.split('::')
            name = name.strip()
            requirements = []

            # single config use case
            if not rest:
                config_args = [name]
                name = os.path.basename(name).replace('.conf', '')
            else:
                config_args = rest[0].split(',')
                config_args = [arg.strip() for arg in config_args]
                # if python requirements listed, set them
                if len(rest) > 1:
                    requirements = rest[1].split(',')
                    requirements = [req.strip() for req in requirements]


            use_case_dict = {'name': name,
                             'config_args': config_args,
                             'requirements': requirements}
            all_cases[category].append(use_case_dict)
            num_cases += 1

    return all_cases, num_cases

if __name__ == "__main__":
    # run all use cases
    all_use_cases = METplusUseCaseSuite()

    all_use_cases.add_use_case_groups('met_tool_wrapper')

    all_use_cases.add_use_case_groups('climate')

    all_use_cases.add_use_case_groups('convection_allowing_models')

    all_use_cases.add_use_case_groups('cryosphere')

    all_use_cases.add_use_case_groups('data_assimilation')

    # slice(5) == medium range 0-4
    all_use_cases.add_use_case_groups('medium_range',
                                      case_slice=slice(5))
    # 5 = medium range 5
    all_use_cases.add_use_case_groups('medium_range',
                                      case_slice=5)
    # slice(6, None) == medium range 6+
    all_use_cases.add_use_case_groups('medium_range',
                                      case_slice=slice(6, None))

    all_use_cases.add_use_case_groups('precipitation')

    all_use_cases.add_use_case_groups('s2s&space_weather&tc_and_extra_tc')

    all_use_cases.print()

    total_cases_to_run = all_use_cases.get_total_cases()
    print(f"Use cases to run: {total_cases_to_run}")
    print(f'Total number of use cases: {all_use_cases.num_cases}')
