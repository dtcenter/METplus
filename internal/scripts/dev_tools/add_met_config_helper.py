#! /usr/bin/env python3

"""
Program Name: doc_util.py
Contact(s): George McCabe
Description: METplus utility that generates instructions to help developers
 add new support for setting MET configuration variables through the wrappers.
"""

import sys
import os
from typing import Any

try:
    from metplus.util.string_manip import get_wrapper_name, camel_to_underscore
    from metplus.util.constants import LOWER_TO_WRAPPER_NAME
except ImportError:
    # if metplus package is not installed, find util relative to this script
    metplus_home = os.path.join(os.path.dirname(__file__),
                                os.pardir, os.pardir, os.pardir)
    sys.path.insert(0, os.path.abspath(metplus_home))
    from metplus.util.string_manip import get_wrapper_name, camel_to_underscore
    from metplus.util.constants import LOWER_TO_WRAPPER_NAME

SCRIPT_INFO_TEXT = (
    'This script is intended to help developers add support for setting '
    'MET configuration variables from a METplus wrapper.\n\n'
    'WARNING: Guidance output from this script may differ slightly '
    'from the actual steps to take. The text that is generated should be '
    'reviewed for accuracy before adding to codebase.\n\n'
    'NOTE: Text between lines that contain all dashes (-) should be '
    'added or replaced in the files. Do not include the dash lines.'
)

WRAPPERS_TO_SKIP = (
    'CyclonePlotter',
    'Example',
    'GempakToCF',
    'GFDLTracker',
    'Usage',
)


def print_doc_text(tool_name, input_dict, skip_met_config=False):
    """! Format documentation for adding support for a new MET config variable
    through METplus wrappers.

     @param tool_name MET tool name, i.e. grid_stat
     @param met_var MET variable name, i.e. output_flag
     @param dict_items (optional) list of MET dictionary var items if met_var
      is a dictionary
    """
    tool_names = []
    if tool_name == "all":
        for wrapper_name in LOWER_TO_WRAPPER_NAME.values():
            if wrapper_name not in WRAPPERS_TO_SKIP and camel_to_underscore(wrapper_name) not in tool_names:
                tool_names.append(camel_to_underscore(wrapper_name))
    else:
        tool_names = tool_name.split()

    _print_script_info_text()

    wrapper_camel_list = []
    for tool in tool_names:
        wrapper_camel = get_wrapper_name(tool)
        if wrapper_camel is None:
            print(f'ERROR: Invalid tool name: {tool}')
            sys.exit(1)
        wrapper_camel_list.append(wrapper_camel)

    # get info for each variable and store it in a dictionary
    met_vars_dict = _get_met_vars(tool_names, wrapper_camel_list, input_dict)

    _step_add_wrapper_content(met_vars_dict, skip_met_config)

    _step_add_parm_metplus_config(met_vars_dict)
    if not skip_met_config:
        _step_add_parm_met_config(met_vars_dict)

    _step_add_unit_tests(met_vars_dict, skip_met_config)
    _step_test_met_tool(met_vars_dict.keys())

    _step_add_doc_wrappers(met_vars_dict, skip_met_config)
    _step_add_doc_glossary(met_vars_dict, skip_met_config)

    _print_script_end_text()


def _print_script_info_text():
    _print_divider_line(after=False)
    print(f'Running script: {__file__}')
    _print_divider_line(before=False)
    print(SCRIPT_INFO_TEXT)


def _print_script_end_text():
    _print_divider_line(after=False)
    print('END OF SCRIPT')
    _print_divider_line(before=False)


def _step_add_wrapper_content(met_vars_dict, skip_met_config):
    _print_divider_line()
    if skip_met_config:
        print("Add handling of the METplus config variable as needed\n")

    for _, (tool_name, met_vars) in met_vars_dict.items():
        print(f'In metplus/wrappers/{tool_name}_wrapper.py')
        if skip_met_config:
            continue

        print(f'\nIn the {get_wrapper_name(tool_name)}Wrapper '
              f'class, add the following to the WRAPPER_ENV_VAR_KEYS class '
              f"variable list:")
        _print_divider_line(char='-', after=False)
        for var in met_vars:
            print(f"        '{var['env_var_name']}',")
        _print_divider_line(char='-', before=False)

        print(f'In the create_c_dict function for '
              f'{get_wrapper_name(tool_name)}Wrapper, add a '
              'function call to read the new METplus config variables and save '
              'the value to be added to the wrapped MET config file.')

        _print_divider_line(char='-', after=False)
        for var in met_vars:
            _print_add_met_config(var)
        _print_divider_line(char='-', before=False)

    if skip_met_config:
        return

    print("DATA_TYPE can be string, list, int, float, bool, "
          "or thresh. Refer to the METplus Contributor's Guide "
          "Basic Components section to see how to add additional info.\n")
    print("NOTE: Sometimes a function is written to handle MET config dictionary"
          " items that are complex and common to many wrappers."
          " Search for functions that start with handle_ in "
          "CommandBuilder or other parent class wrappers to see if a "
          "function already exists for the item you are adding or to use "
          "as an example to write a new one.")


def _step_add_parm_metplus_config(met_vars_dict):
    _print_divider_line()
    for wrapper_camel, (tool_name, met_vars) in met_vars_dict.items():
        print(f'In parm/use_cases/met_tool_wrapper/{wrapper_camel}/{wrapper_camel}.conf')
        print('\nAdd the new variables commented out in the basic use case')

        _print_divider_line(char='-', after=False)

        for var in met_vars:
            for mp_config in var['metplus_config_names']:
                print(f'#{mp_config} =')

        _print_divider_line(char='-', before=False)


def _step_add_parm_met_config(met_vars_dict):
    _print_divider_line()
    for wrapper_camel, (tool_name, met_vars) in met_vars_dict.items():
        var_names = '/'.join([var['name'] for var in met_vars])
        print(f"In parm/met_config/{wrapper_camel}Config_wrapped\n\n"
              "IMPORTANT: Compare the default values set for "
              f"{var_names} "
              "to the version"
              f" in share/met/config/{wrapper_camel}Config_default. If "
              "they do differ, make sure to add variables to the use case "
              "config files so that they produce the same output.\n\n")

        for var in met_vars:
            print("REPLACE:")
            _print_divider_line(char='-', after=False)
            print(f"{var['name']} = ...")
            _print_divider_line(char='-', before=False)
            print('with:')
            _print_divider_line(char='-', after=False)
            print(f"//{var['name']} ={' {' if var['dict_items'] else ''}")
            print(f"${{{var['env_var_name']}}}")
            _print_divider_line(char='-', before=False)


def _step_add_doc_wrappers(met_vars_dict, skip_met_config):
    _print_divider_line()
    print("In docs/Users_Guide/wrappers.rst\n")

    for wrapper_camel, (tool_name, met_vars) in met_vars_dict.items():
        print(f"Under {wrapper_camel} => METplus Configuration section, add:")

        _print_divider_line(char='-', after=False)
        for var in met_vars:
            for metplus_config_name in var['metplus_config_names']:
                print(f'| :term:`{metplus_config_name}`')
        _print_divider_line(char='-', before=False)

        if skip_met_config:
            continue

        print(f"Under {wrapper_camel} => MET Configuration section, add:")
        _print_divider_line(char='-')
        for var in met_vars:
            _print_met_config_table(var)
        _print_divider_line(char='-', before=False)


def _step_add_doc_glossary(met_vars_dict, skip_met_config):
    _print_divider_line()
    print("In docs/Users_Guide/glossary.rst\n\n"
          "Add the following anywhere in the file:")
    _print_divider_line(char='-')
    for wrapper_camel, (_, met_vars) in met_vars_dict.items():
        for var in met_vars:
            _print_glossary_entry(var, wrapper_camel, skip_met_config)
    _print_divider_line(char='-', before=False)


def _step_add_unit_tests(met_vars_dict, skip_met_config):
    _print_divider_line()
    if skip_met_config:
        print("Add any unit tests as needed")

    for _, (tool_name, met_vars) in met_vars_dict.items():
        print(f"In internal/tests/pytests/wrappers/{tool_name}/test_{tool_name}_wrapper.py")
        if skip_met_config:
            continue

        print("\nAdd the following items to "
              "the tests to ensure the new items are set properly. Note: "
              "if the tool does not have unit tests to check the handling of "
              "MET config variables, you will need to add those tests. See "
              "grid_stat/test_grid_stat_wrapper.py for an example. Change "
              "VALUE to an appropriate value for the variable.\n")

        _print_divider_line(char='-', after=False)
        for var in met_vars:
            _print_unit_test(var)
        _print_divider_line(char='-', before=False)


def _step_test_met_tool(wrapper_camel_list):
    # add note to test setting a valid value in the basic use case config file
    # to ensure that it is formatted properly when read by the MET tool
    _print_divider_line()
    for wrapper_camel in wrapper_camel_list:
        print(f"In parm/use_cases/met_tool_wrapper/{wrapper_camel}")

    print("\nVerify that the new METplus configuration variable(s) "
          "will be formatted properly when read by the MET tool by "
          "setting the variable(s) in the basic use case config files "
          "to a valid value "
          "and run the use case to ensure that it still succeeds. "
          "Be sure to remove the value and comment out the variable "
          "after you have confirmed this step.")


def _get_met_vars(tool_names, wrapper_camel_list, input_dict):
    _print_divider_line()
    print('Generating instructions for adding support for:\n')

    met_vars_dict = {}
    for tool_name, wrapper_camel in zip(tool_names, wrapper_camel_list):
        met_vars = []
        for var_name, dict_list in input_dict.items():
            metplus_var = f"{tool_name.upper()}_{var_name.upper().replace('.', '_')}"
            env_var_name = f'METPLUS_{var_name.upper()}'
            met_var = {'name': var_name, 'dict_items': dict_list,
                       'metplus_config_names': [], 'met_config_names': []}
            if not dict_list:
                met_var['env_var_name'] = env_var_name
                met_var['metplus_config_names'].append(metplus_var)
                met_var['met_config_names'].append(var_name)
            else:
                met_var['env_var_name'] = f'{env_var_name}_DICT'
                for item_name in dict_list:
                    metplus_config = f"{metplus_var}_{item_name.upper().replace('.', '_')}"
                    met_config = f"{var_name}.{item_name}"
                    met_var['metplus_config_names'].append(metplus_config)
                    met_var['met_config_names'].append(met_config)

            met_vars.append(met_var)

        met_vars_dict[wrapper_camel] = (tool_name, met_vars)

        _print_met_vars(met_vars, tool_name)

    return met_vars_dict


def _print_met_vars(met_vars: list[Any], tool_name):
    print(f"Wrapper: {get_wrapper_name(tool_name)}")
    for index, var in enumerate(met_vars, 1):
        print(f"  MET Variable {index}: {var['name']}")
        if var['dict_items']:
            print(f"    Dictionary Items: {', '.join(var['dict_items'])}")
        print()


def _print_divider_line(char='=', count=80, before=True, after=True):
    value = char * count
    if before:
        value = f'\n{value}'
    if after:
        value = f'{value}\n'
    print(value)


def _print_add_met_config(var):
    met_var = var['name']
    dict_items = var['dict_items']
    if not dict_items:
        print(f"        self.add_met_config(name='{met_var}',\n"
              "                            data_type='DATA_TYPE')")
    else:
        print(f"        self.add_met_config_dict('{met_var}', {{")
        for item in dict_items:
            print(f"            '{item}': 'DATA_TYPE',")
        print("        })")
    print()


def _print_met_config_table(var):
    env_var_name = var['env_var_name']
    metplus_names = var['metplus_config_names']
    met_names = var['met_config_names']
    var_header = f"${{{env_var_name}}}\n{'"' * (len(env_var_name)+3)}"
    list_table_text = (f"{var_header}\n\n"
                       ".. list-table::\n"
                       "   :widths: 5 5\n"
                       "   :header-rows: 1\n\n"
                       "   * - METplus Config(s)\n"
                       "     - MET Config File\n"
                       )

    for metplus_config_name, met_config_name in zip(metplus_names, met_names):
        list_table_text += (f"   * - :term:`{metplus_config_name}`\n"
                            f"     - {met_config_name}\n"
                            )
    print(list_table_text)


def _print_glossary_entry(var, wrapper_camel, skip_met_config):
    metplus_names = var['metplus_config_names']
    met_names = var['met_config_names']
    for metplus_config_name, met_config_name in zip(metplus_names, met_names):
        variable_info = "     REPLACE ME"
        if not skip_met_config:
            variable_info = (
                f"     Specify the value for '{met_config_name}' "
                f"in the MET configuration file"
            )

        glossary_entry = (
            f"   {metplus_config_name}\n{variable_info} for {wrapper_camel}.\n\n"
            f"     | *Used by:* {wrapper_camel}"
        )
        print(f'{glossary_entry}\n')


def _print_unit_test(var):
    input_dict_items = []
    output_items = []
    output_dict_items = {}
    metplus_names = var['metplus_config_names']
    met_names = var['met_config_names']
    dict_items = var['dict_items']
    for metplus_config_name, met_config_name in zip(metplus_names, met_names):
        child_name = None
        item_name = None
        output_item = _get_output_item(dict_items, met_config_name)

        mp_config_dict_item = f"'{metplus_config_name}': 'VALUE',"
        input_dict_items.append(mp_config_dict_item)
        if child_name and item_name:
            if item_name not in output_dict_items:
                output_dict_items[item_name] = []
            output_dict_items[item_name].append(f"{child_name} = VALUE;")
        else:
            output_items.append(output_item)

        output_fmt = output_item
        if dict_items:
            output_fmt = f"{{{output_item}}}"

        test_text = (f"        ({{{mp_config_dict_item} }},\n"
                     f"         {{'{var['env_var_name']}': '{var['name']} = "
                     f"{output_fmt}'}}),\n")
        print(test_text)

    if not dict_items:
        return

    for key, value in output_dict_items.items():
        output_items.append(f"{key} = {{" + ''.join(value) + "}")

    all_items_text = "        ({\n"
    for input_dict_item in input_dict_items:
        all_items_text += f"           {input_dict_item}\n"
    all_items_text += (
        f"          }},\n         {{'{var['env_var_name']}': '{var['name']} = {{"
    )
    all_items_text += ''.join(output_items)
    all_items_text += "}'}),"
    print(all_items_text)


def _get_output_item(dict_items, met_config_name):
    if not dict_items:
        return 'VALUE'

    item_name, *rest = met_config_name.split('.')[1:]
    child_name = rest[0] if rest else None
    if not child_name:
        return f"{item_name} = VALUE;"

    return f"{item_name} = {{{child_name} = VALUE;}}"


def doc_util_usage():
    """! Print usage statement for script """
    file = os.path.basename(__file__)
    print(
        'Usage:\n'
        f'{file} <met-tool> "<met-variable> [<met-dict-items>]" '
        '"<met-variable> [<met-dict-items>]" [--skip_met_config]\n'
        f"\nExample: {file} grid_stat output_prefix "
        "\n  (simple variable named output_prefix)\n"
        f'\nExample: {file} grid_stat "output_flag fho ctc mctc" '
        '\n  (dictionary named output_flag containing fho, ctc, and mctc)\n'
        f'\nExample: {file} grid_stat "output_flag fho ctc mctc" '
        'output_prefix \n  (both of the variables from the previous '
        'examples)\n'
        f'\nExample: {file} point_stat "topo_mask interp.method interp.width" '
        '\n  (dictionary named topo_mask containing dictionary interp containing method and width)\n'
        f"\nExample: {file} \"grid_stat point_stat\" output_prefix "
        "\n  (variable named output_prefix for multiple wrappers)\n"
        f"\nExample: {file} all skip_warn_output_overwrite --skip_met_config"
        "\n  (variable named skip_warn_output_overwrite for all wrappers, skipping MET config steps)\n"
    )


if __name__ == "__main__":
    import argparse


    # custom ArgumentParser for custom usage statement function
    class CustomParser(argparse.ArgumentParser):
        def error(self, message):
            # Override standard error handling to print usage statement and exit
            doc_util_usage()
            sys.exit(1)

    parser = CustomParser(add_help=False)

    # Add optional boolean flag
    parser.add_argument(
        "--skip_met_config",
        action="store_true",
        help="Skip steps specific to MET config variables",
    )

    parser.add_argument("TOOL_NAME")
    parser.add_argument("raw_vars", nargs="+")
    args = parser.parse_args()

    variable_info = {}
    for arg in args.raw_vars:
        variable_name, *dictionary_items = arg.split()
        variable_info[variable_name] = dictionary_items

    print_doc_text(args.TOOL_NAME, variable_info, skip_met_config=args.skip_met_config)
