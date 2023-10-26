#! /usr/bin/env python3

"""
Program Name: doc_util.py
Contact(s): George McCabe
Description: METplus utility that generates instructions to help developers
 add new support for setting MET configuration variables through the wrappers.
"""

import sys
import os

try:
    from metplus.util.string_manip import get_wrapper_name
except ImportError:
    # if metplus package is not installed, find util relative to this script
    metplus_home = os.path.join(os.path.dirname(__file__),
                                os.pardir, os.pardir, os.pardir)
    sys.path.insert(0, os.path.abspath(metplus_home))
    from metplus.util.string_manip import get_wrapper_name

SCRIPT_INFO_TEXT = (
    'This script is intended to help developers add support for setting '
    'MET configuration variables from a METplus wrapper.\n\n'
    'WARNING: Guidance output from this script may differ slightly '
    'from the actual steps to take. The text that is generated should be '
    'reviewed for accuracy before adding to codebase.\n\n'
    'NOTE: Text between lines that contain all dashes (-) should be '
    'added or replaced in the files. Do not include the dash lines.'
)


def print_doc_text(tool_name, input_dict):
    """! Format documentation for adding support for a new MET config variable
    through METplus wrappers.

     @param tool_name MET tool name, i.e. grid_stat
     @param met_var MET variable name, i.e. output_flag
     @param dict_items (optional) list of MET dictionary var items if met_var
      is a dictionary
    """
    _print_script_info_text()

    wrapper_camel = get_wrapper_name(tool_name)

    # get info for each variable and store it in a dictionary
    met_vars = _get_met_vars(tool_name, input_dict)

    _step_add_wrapper_env_var_keys(met_vars, tool_name)
    _step_add_wrapper_config_dict(met_vars, tool_name)

    _step_add_parm_metplus_config(met_vars, wrapper_camel)
    _step_add_parm_met_config(met_vars, wrapper_camel)

    _step_add_doc_metplus_config(met_vars, wrapper_camel)
    _step_add_doc_met_config(met_vars, wrapper_camel)
    _step_add_doc_glossary(met_vars, wrapper_camel)
    _step_add_unit_tests(tool_name, met_vars)
    _step_test_met_tool(wrapper_camel)

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


def _step_add_wrapper_env_var_keys(met_vars, tool_name):
    _print_divider_line()
    print(f'In metplus/wrappers/{tool_name}_wrapper.py\n\n'
          f'In the {get_wrapper_name(tool_name)}Wrapper '
          f'class, add the following to the WRAPPER_ENV_VAR_KEYS class '
          f"variable list:\n")
    _print_divider_line(char='-', after=False)
    for var in met_vars:
        print(f"        '{var['env_var_name']}',")
    _print_divider_line(char='-', before=False)


def _step_add_wrapper_config_dict(met_vars, tool_name):
    _print_divider_line()
    print(f'In metplus/wrappers/{tool_name}_wrapper.py\n')
    print(f'In the create_c_dict function for '
          f'{get_wrapper_name(tool_name)}Wrapper, add a '
          'function call to read the new METplus config variables and save '
          'the value to be added to the wrapped MET config file.\n')

    _print_divider_line(char='-', after=False)
    for var in met_vars:
        _print_add_met_config(var)
    _print_divider_line(char='-', before=False)

    print("where DATA_TYPE can be string, list, int, float, bool, "
          "or thresh. Refer to the METplus Contributor's Guide "
          "Basic Components section to see how to add additional info.\n")
    print("Sometimes a function is written to handle MET config dictionary"
          " items that are complex and common to many wrappers."
          " Search for functions that start with handle_ in "
          "CommandBuilder or other parent class wrappers to see if a "
          "function already exists for the item you are adding or to use "
          "as an example to write a new one.")


def _step_add_parm_metplus_config(met_vars, wrapper_camel):
    _print_divider_line()
    print(f'In parm/use_cases/met_tool_wrapper/{wrapper_camel}/{wrapper_camel}.conf')
    print('\nAdd the new variables commented out in the basic use case')

    _print_divider_line(char='-', after=False)

    for var in met_vars:
        for mp_config in var['metplus_config_names']:
            print(f'#{mp_config} =')

    _print_divider_line(char='-', before=False)


def _step_add_parm_met_config(met_vars, wrapper_camel):
    _print_divider_line()

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


def _step_add_doc_metplus_config(met_vars, wrapper_camel):
    _print_divider_line()
    print(f"In docs/Users_Guide/wrappers.rst\n\n"
          f"Under {wrapper_camel} => METplus Configuration section, add:")

    _print_divider_line(char='-', after=False)
    for var in met_vars:
        for metplus_config_name in var['metplus_config_names']:
            print(f'| :term:`{metplus_config_name}`')
    _print_divider_line(char='-', before=False)


def _step_add_doc_met_config(met_vars, wrapper_camel):
    _print_divider_line()
    print(f"In docs/Users_Guide/wrappers.rst\n\n"
          f"Under {wrapper_camel} => MET Configuration section, add:")
    _print_divider_line(char='-')
    for var in met_vars:
        _print_met_config_table(var)
    _print_divider_line(char='-', before=False)


def _step_add_doc_glossary(met_vars, wrapper_camel):
    _print_divider_line()
    print("In docs/Users_Guide/glossary.rst\n\n"
          "Add the following anywhere in the file:")
    _print_divider_line(char='-')
    for var in met_vars:
        _print_glossary_entry(var, wrapper_camel)
    _print_divider_line(char='-', before=False)


def _step_add_unit_tests(tool_name, met_vars):
    _print_divider_line()
    print(f"In internal/tests/pytests/wrappers/{tool_name}/"
          f"test_{tool_name}_wrapper.py"
          "\n\nAdd the following items to "
          "the tests to ensure the new items are set properly. Note: "
          "if the tool does not have unit tests to check the handling of "
          "MET config variables, you will need to add those tests. See "
          "grid_stat/test_grid_stat_wrapper.py for an example. Change "
          "VALUE to an appropriate value for the variable.\n")

    _print_divider_line(char='-', after=False)
    for var in met_vars:
        _print_unit_test(var)
    _print_divider_line(char='-', before=False)


def _step_test_met_tool(wrapper_camel):
    # add note to test setting a valid value in the basic use case config file
    # to ensure that it is formatted properly when read by the MET tool
    _print_divider_line()
    print(f"In parm/use_cases/met_tool_wrapper/{wrapper_camel}"
          "\n\nVerify that the new METplus configuration variable(s) "
          "will be formatted properly when read by the MET tool by "
          "setting the variable(s) in the basic use case config files "
          "to a valid value "
          "and run the use case to ensure that it still succeeds. "
          "Be sure to remove the value and comment out the variable "
          "after you have confirmed this step.")


def _get_met_vars(tool_name, input_dict):
    met_vars = []
    for var_name, dict_list in input_dict.items():
        metplus_var = f'{tool_name.upper()}_{var_name.upper()}'
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
                metplus_config = f'{metplus_var}_{item_name.upper()}'
                met_config = f"{var_name}.{item_name}"
                met_var['metplus_config_names'].append(metplus_config)
                met_var['met_config_names'].append(met_config)

        met_vars.append(met_var)

    _print_divider_line()
    print('Generating instructions for adding support for:\n')
    print(f"Wrapper: {get_wrapper_name(tool_name)}\n")
    for index, var in enumerate(met_vars, 1):
        print(f"MET Variable {index}: {var['name']}")
        if var['dict_items']:
            print(f"  Dictionary Items: {', '.join(var['dict_items'])}")
        print()

    return met_vars


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
    var_header = f"${{{env_var_name}}}\n{'^' * (len(env_var_name)+3)}"
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


def _print_glossary_entry(var, wrapper_camel):
    metplus_names = var['metplus_config_names']
    met_names = var['met_config_names']
    for metplus_config_name, met_config_name in zip(metplus_names, met_names):
        glossary_entry = (
            f"   {metplus_config_name}\n"
            f"     Specify the value for '{met_config_name}' "
            f"in the MET configuration file for {wrapper_camel}.\n\n"
            f"     | *Used by:* {wrapper_camel}"
        )
        print(f'{glossary_entry}\n')


def _print_unit_test(var):
    input_dict_items = []
    output_items = []
    metplus_names = var['metplus_config_names']
    met_names = var['met_config_names']
    dict_items = var['dict_items']
    for metplus_config_name, met_config_name in zip(metplus_names, met_names):
        if dict_items:
            item_name = met_config_name.split('.')[1]
            output_item = f"{item_name} = VALUE;"
        else:
            output_item = 'VALUE;'
        mp_config_dict_item = f"'{metplus_config_name}': 'VALUE',"
        input_dict_items.append(mp_config_dict_item)
        output_items.append(output_item)
        if dict_items:
            output_fmt = f"{{{output_item}}}"
        else:
            output_fmt = output_item

        test_text = (f"        ({{{mp_config_dict_item} }},\n"
                     f"         {{'{var['env_var_name']}': '{var['name']} = "
                     f"{output_fmt}'}}),\n")
        print(test_text)

    if not dict_items:
        return
    all_items_text = "        ({\n"
    for input_dict_item in input_dict_items:
        all_items_text += f"           {input_dict_item}\n"
    all_items_text += (
        f"          }},\n         {{'{var['env_var_name']}': '{var['name']} = {{"
    )
    all_items_text += ''.join(output_items)
    all_items_text += "}'}),"
    print(all_items_text)


def doc_util_usage():
    """! Print usage statement for script """
    print('Usage:\n'
          f'{__file__} <met-tool> "<met-variable> [<met-dict-items>]" '
          '"<met-variable> [<met-dict-items>]"\n'
          f"\nExample: {__file__} grid_stat output_prefix "
          "\n  (simple variable named output_prefix)\n"
          f'\nExample: {__file__} grid_stat "output_flag fho ctc mctc" '
          '\n  (dictionary named output_flag containing fho, ctc, and mctc)\n'
          f'\nExample: {__file__} grid_stat "output_flag fho ctc mctc" '
          'output_prefix \n  (both of the variables from the previous '
          'examples)\n')


if __name__ == "__main__":
    # sys.argv[1] is MET tool name, i.e. grid_stat
    # sys.argv[2+] is MET variable name, i.e. output_flag or a MET variable
    # name followed by a list of MET dictionary var items separated by spaces
    if len(sys.argv) < 3:
        doc_util_usage()
        sys.exit(1)

    TOOL_NAME = sys.argv[1]
    INPUT_DICT = {}
    for arg in sys.argv[2:]:
        variable_name, *dictionary_items = arg.split()
        INPUT_DICT[variable_name] = dictionary_items

    print_doc_text(TOOL_NAME, INPUT_DICT)
