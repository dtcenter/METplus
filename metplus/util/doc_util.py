#! /usr/bin/env python3

import sys
import os

# dictionary used by get_wrapper_name function to easily convert wrapper
# name in many formats to the correct name of the wrapper class
LOWER_TO_WRAPPER_NAME = {'ascii2nc': 'ASCII2NC',
                         'cycloneplotter': 'CyclonePlotter',
                         'ensemblestat': 'EnsembleStat',
                         'example': 'Example',
                         'extracttiles': 'ExtractTiles',
                         'gempaktocf': 'GempakToCF',
                         'genvxmask': 'GenVxMask',
                         'griddiag': 'GridDiag',
                         'gridstat': 'GridStat',
                         'makeplots': 'MakePlots',
                         'metdbload': 'METDbLoad',
                         'mode': 'MODE',
                         'mtd': 'MTD',
                         'modetimedomain': 'MTD',
                         'pb2nc': 'PB2NC',
                         'pcpcombine': 'PCPCombine',
                         'plotdataplane': 'PlotDataPlane',
                         'point2grid': 'Point2Grid',
                         'pointtogrid': 'Point2Grid',
                         'pointstat': 'PointStat',
                         'pyembedingest': 'PyEmbedIngest',
                         'regriddataplane': 'RegridDataPlane',
                         'seriesanalysis': 'SeriesAnalysis',
                         'statanalysis': 'StatAnalysis',
                         'tcgen': 'TCGen',
                         'tcpairs': 'TCPairs',
                         'tcrmw': 'TCRMW',
                         'tcstat': 'TCStat',
                         'tcmprplotter': 'TCMPRPlotter',
                         'usage': 'Usage',
                         'userscript': 'UserScript',
                         }

def get_wrapper_name(process_name):
    """! Determine name of wrapper from string that may not contain the correct
         capitalization, i.e. Pcp-Combine translates to PCPCombine

         @param process_name string that was listed in the PROCESS_LIST
         @returns name of wrapper (without 'Wrapper' at the end) and None if
          name cannot be determined
    """
    lower_process = (process_name.replace('-', '')
                         .replace('_', '')
                         .replace(' ', '')
                         .lower())
    if lower_process in LOWER_TO_WRAPPER_NAME.keys():
        return LOWER_TO_WRAPPER_NAME[lower_process]

    return None


def print_doc_text(tool_name, met_var, dict_items):
    """! Format documentation for adding support for a new MET config variable
    through METplus wrappers.

     @param tool_name MET tool name, i.e. grid_stat
     @param met_var MET variable name, i.e. output_flag
     @param dict_items (optional) list of MET dictionary var items if met_var
      is a dictionary
    """
    wrapper_caps = tool_name.upper()
    met_var_caps = met_var.upper()
    env_var_name = f'METPLUS_{met_var_caps}'

    wrapper_camel = get_wrapper_name(wrapper_caps)

    metplus_var = f'{wrapper_caps}_{met_var_caps}'

    metplus_config_names = []
    met_config_values = []
    if not dict_items:
        metplus_config_names.append(metplus_var)
        met_config_values.append(met_var)
    else:
        env_var_name = f'{env_var_name}_DICT'
        for item_name in dict_items:
            item_name_caps = item_name.upper()
            metplus_config_name = f'{metplus_var}_{item_name_caps}'

            metplus_config_names.append(metplus_config_name)
            met_config_values.append(f"{met_var}.{item_name}")

    print('WARNING: Guidance output from this script may differ slightly '
          'from the actual steps to take. It is intended to assist the process.'
          ' The text that is generated should be reviewed for accuracy before '
          'adding to codebase.')

    print(f"\nWrapper: {wrapper_camel}")
    print(f"MET Variable: {met_var}")
    if dict_items:
        print(f"Dictionary Items:")
        for item in dict_items:
            print(f'  {item}')

    print('\n==================================================\n')
    print(f'\n\nIn the {tool_name}_wrapper.py file, in the {wrapper_camel}Wrapper '
          f'class, add the following to the WRAPPER_ENV_VAR_KEYS class '
          f"variable list:\n\n\n        '{env_var_name}',\n\n")

    print('\n==================================================\n')
    print(f'In the create_c_dict function for {wrapper_camel}Wrapper, add a '
          'function call to read the new METplus config variables and save '
          'the value to be added to the wrapped MET config file.\n\n')
    if not dict_items:
        print(f"        self.add_met_config(name='{met_var}',\n"
              "                            data_type='<DATA_TYPE>',\n"
              f"                            metplus_configs=['{metplus_var}'])"
              "\n\n\n"
              "where <DATA_TYPE> can be string, list, int, float, bool, "
              "or thresh.\n\n")
    else:
        print("Typically a function is written to handle MET config dictionary"
              " items. Search for functions that start with handle_ in "
              "CommandBuilder or other parent class wrappers to see if a "
              "function already exists for the item you are adding or to use "
              "as an example to write a new one.\n\n")

    print('\n==================================================\n')
    print('Add the new variables to the basic use case example for the tool,\n'
          f'i.e. parm/use_cases/met_tool_wrapper/{wrapper_camel}/'
          f'{wrapper_camel}.conf:\n\n')
    for mp_config in metplus_config_names:
        print(f'#{mp_config} =')

    print('\n\n==================================================\n')
    print(f"In the parm/met_config/{wrapper_camel}Config_wrapped file, "
          f"compare the default values set for {met_var} to the version"
          f" in share/met/config/{wrapper_camel}Config_default. If "
          "they do differ, make sure to add variables to the use case "
          "config files so that they produce the same output.\n\n")
    print(f"In the parm/met_config/{wrapper_camel}Config_wrapped file, "
          "replace:\n\n")
    print(f"{met_var} = ...\n\n with:\n\n//{met_var} ="
          f"{' {' if dict_items else ''}\n${{{env_var_name}}}\n\n")

    print('\n==================================================\n')
    print(f"\n\nIn docs/Users_Guide/wrappers.rst under {wrapper_camel} => "
         "METplus Configuration section, add:\n\n")
    for metplus_config_name in metplus_config_names:
        print(f'| :term:`{metplus_config_name}`')

    print('\n==================================================\n')
    print(f"\n\nIn docs/Users_Guide/wrappers.rst under {wrapper_camel} => "
          "MET Configuration section, add:\n\n")
    var_header = (f"**${{{env_var_name}}}**")

    list_table_text = (f"{var_header}\n\n"
                       ".. list-table::\n"
                       "   :widths: 5 5\n"
                       "   :header-rows: 0\n\n"
                       "   * - METplus Config(s)\n"
                       "     - MET Config File\n"
                       )

    for metplus_config_name, met_config_name in zip(metplus_config_names, met_config_values):
        list_table_text += (f"   * - :term:`{metplus_config_name}`\n"
                            f"     - {met_config_name}\n"
                            )
    print(list_table_text)

    print('\n==================================================\n')
    print(f"In docs/Users_Guide/glossary.rst, add:\n\n")
    for metplus_config_name, met_config_name in zip(metplus_config_names, met_config_values):
        glossary_entry = (f"   {metplus_config_name}\n"
                          f"     Specify the value for '{met_config_name}' "
                          f"in the MET configuration file for {wrapper_camel}.\n\n"
                          f"     | *Used by:* {wrapper_camel}")
        print(f'{glossary_entry}\n')

    print('\n==================================================\n')
    print(f"In internal_tests/pytests/{tool_name}/"
          f"test_{tool_name}_wrapper.py, add the following items to "
          "the tests to ensure the new items are set properly. Note: "
          "if the tool does not have unit tests to check the handling of "
          "MET config variables, you will need to add those tests. See "
          "grid_stat/test_grid_stat_wrapper.py for an example. Change "
          "VALUE to an appropriate value for the variable.\n\n")

    input_dict_items = []
    output_items = []
    for metplus_config_name, met_config_name in zip(metplus_config_names, met_config_values):
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
                     f"         {{'{env_var_name}': '{met_var} = "
                     f"{output_fmt}'}}),\n")
        print(test_text)

    if dict_items:
        all_items_text = "        ({\n"
        for input_dict_item in input_dict_items:
            all_items_text += f"           {input_dict_item}\n"
        all_items_text += ("          },\n"
                           f"         {{'{env_var_name}': '{met_var} = {{")
        all_items_text += ''.join(output_items)
        all_items_text += "}'}),"
        print(all_items_text)


def doc_util_usage():
    """! Print usage statement for script """
    print(f"{__file__} <met-tool> <met-variable> [<met-dict-items]\n"
          f"Example: {__file__} grid_stat output_prefix\n"
          f'Example: {__file__} grid_stat output_flag fho ctc mctc"\n')

if __name__ == "__main__":
    # sys.argv[1] is MET tool name, i.e. grid_stat
    # sys.argv[2] is MET variable name, i.e. output_flag
    # sys.argv[3] is optional list of MET dictionary var items: fho ctc cts
    if len(sys.argv) < 3:
        doc_util_usage()
        sys.exit(1)

    tool_name = sys.argv[1]
    met_var = sys.argv[2]
    dict_items = None

    if len(sys.argv) > 3:
        items = ','.join(sys.argv[3:]).split(',')
        dict_items = [item.strip() for item in items]

    print_doc_text(tool_name, met_var, dict_items)
