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

    wrapper_camel = get_wrapper_name(wrapper_caps)


    metplus_var = f'{wrapper_caps}_{met_var_caps}'

    metplus_config_names = []
    met_config_values = []
    if not dict_items:
        metplus_config_names.append(metplus_var)
        met_config_values.append(met_var)
    else:
        for item_name in dict_items:
            item_name_caps = item_name.upper()
            metplus_config_name = f'{metplus_var}_{item_name_caps}'

            metplus_config_names.append(metplus_config_name)
            met_config_values.append(f"{met_var}.{item_name}")

    print(f"\nWrapper: {wrapper_camel}")
    print(f"MET Variable: {met_var}")
    if dict_items:
        print(f"Dictionary Items:")
        for item in dict_items:
            print(f'  {item}')

    print(f"\n\nIn docs/Users_Guide/wrappers.rst under {wrapper_camel} => "
          "METplus Configuration section, add:\n\n")
    for metplus_config_name in metplus_config_names:
        print(f'| :term:`{metplus_config_name}`')

    print(f"\n\nIn docs/Users_Guide/wrappers.rst under {wrapper_camel} => "
          "MET Configuration section, add:\n\n")
    var_header = (f"**${{METPLUS_{met_var_caps}"
                  f"{'_DICT' if dict_items else ''}"
                  "}**")

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

    print(f"In docs/Users_Guide/glossary.rst, add:\n\n")
    for metplus_config_name, met_config_name in zip(metplus_config_names, met_config_values):
        glossary_entry = (f"   {metplus_config_name}\n"
                          f"     Specify the value for '{met_config_name}' "
                          f"in the MET configuration file for {wrapper_camel}.\n\n"
                          f"     | *Used by:* {wrapper_camel}")
        print(f'{glossary_entry}\n')

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
