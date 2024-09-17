"""
Program Name: met_config.py
Contact(s): George McCabe
"""

import os
import re

from .constants import PYTHON_EMBEDDING_TYPES, CLIMO_TYPES, MISSING_DATA_VALUE
from .string_manip import getlist, get_threshold_via_regex
from .string_manip import remove_quotes as util_remove_quotes
from .string_manip import find_indices_in_config_section
from .config_metplus import parse_var_list
from .field_util import format_all_field_info


class METConfig:
    """! Stores information for a member of a MET config variables that
      can be used to set the value, the data type of the item,
      optional name of environment variable to set (without METPLUS_ prefix)
      if it differs from the name,
      and any additional requirements such as remove quotes or make uppercase.
      output_dict argument is ignored and only added to allow the argument
      to the function that creates an instance of this object.
    """
    def __init__(self, name, data_type,
                 env_var_name=None,
                 metplus_configs=None,
                 extra_args=None,
                 children=None,
                 output_dict=None):
        self.name = name
        self.data_type = data_type
        self.metplus_configs = metplus_configs
        self.extra_args = extra_args
        self.env_var_name = env_var_name if env_var_name else name
        self.children = children

    def __repr__(self):
        return (f'{self.__class__.__name__}({self.name}, {self.data_type}, '
                f'{self.env_var_name}, '
                f'{self.metplus_configs}, '
                f'{self.extra_args}'
                f', {self.children}'
                ')')

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        self._name = name

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, data_type):
        self._data_type = data_type

    @property
    def env_var_name(self):
        return self._env_var_name

    @env_var_name.setter
    def env_var_name(self, env_var_name):
        if not isinstance(env_var_name, str):
            raise TypeError("Name must be a string")
        self._env_var_name = env_var_name

    @property
    def metplus_configs(self):
        return self._metplus_configs

    @metplus_configs.setter
    def metplus_configs(self, metplus_configs):
        # convert to a list if input is a single value
        config_names = metplus_configs
        if config_names and not isinstance(config_names, list):
            config_names = [config_names]
            
        self._metplus_configs = config_names

    @property
    def extra_args(self):
        return self._extra_args

    @extra_args.setter
    def extra_args(self, extra_args):
        args = extra_args if extra_args else {}
        if not isinstance(args, dict):
            raise TypeError("Expected a dictionary")

        self._extra_args = args

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, children):
        if not children and 'dict' in self.data_type:
            raise TypeError("Must have children if data_type is dict.")

        if children and 'dict' not in self.data_type:
            raise TypeError("data_type must be dict to have "
                            f"children. data_type is {self.data_type}")

        self._children = children


def get_wrapped_met_config_file(config, app_name, default_config_file=None):
    """! Get the MET config file path for the wrapper from the
    METplusConfig object. If unset, use the default value if provided.

    @param default_config_file (optional) filename of wrapped MET config
     file found in parm/met_config to use if config file is not set
    @returns path to wrapped config file or None if no default is provided
    """
    config_name = f'{app_name.upper()}_CONFIG_FILE'
    config_file = config.getraw('config', config_name, '')
    if config_file:
        return config_file

    if not default_config_file:
        return None

    default_config_path = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       default_config_file)
    config.logger.debug(f"{config_name} is not set. "
                        f"Using {default_config_path}")
    return default_config_path


def add_met_config_dict(config, app_name, output_dict, dict_name, items):
    """! Read config variables for MET config dictionary and set output_dict
     (typically CommandBuilder's env_var_dict) with formatted values

    @param config METplusConfig object to read
    @param app_name name of application to find wrapper-specific variables
    @param output_dict dictionary to save formatted output
    @param dict_name name of MET dictionary variable
    @param items dictionary where the key is name of variable inside MET
     dictionary and the value is info about the item (see parse_item_info
     function for more information)
    """
    dict_items = []

    # config prefix i.e GRID_STAT_CLIMO_MEAN_
    metplus_prefix = f'{app_name}_{dict_name}_'.upper()
    for name, item_info in items.items():
        data_type, extra, kids, nicknames = _parse_item_info(item_info)

        # config name i.e. GRID_STAT_CLIMO_MEAN_FILE_NAME
        metplus_name = f'{metplus_prefix}{name.upper()}'

        # change (n) to _N i.e. distance_map.beta_value(n)
        metplus_name = metplus_name.replace('(N)', '_N')
        metplus_configs = []

        if 'dict' not in data_type:
            children = None
            metplus_configs.append(metplus_name)

            # if variable ends with _BEG, read _BEGIN first
            if metplus_name.endswith('BEG'):
                metplus_configs.append(f'{metplus_name}IN')

            if dict_name == 'obs_window':
                suffix = 'BEGIN' if name == 'beg' else name.upper()

                # handle legacy OBS_WINDOW variables that put OBS_ before
                # app name i.e. OBS_GRID_STAT_WINDOW_[BEGIN/END]
                metplus_configs.append(
                    f"OBS_{app_name}_WINDOW_{suffix}".upper()
                )

                # also add support for legacy PB2NC_WINDOW_[BEGIN/END]
                if app_name.lower() == 'pb2nc':
                    metplus_configs.append(
                        f"{app_name}_WINDOW_{suffix}".upper()
                    )

                # also add OBS_WINDOW_[BEGIN/END]
                metplus_configs.append(f"{dict_name}_{name}".upper())
                if name == 'beg':
                    metplus_configs.append(f"{dict_name}_{name}IN".upper())

            # add other variable names to search if expected name is unset
            if nicknames:
                for nickname in nicknames:
                    metplus_configs.append(nickname)

        # if list of dictionaries (dictlist)
        elif 'list' in data_type:
            children = get_met_config_dict_list(config, app_name, name, kids, parent=dict_name)
            if not children:
                continue
        # if dictionary, read get children from MET config
        else:
            children = []
            for kid_name, kid_info in kids.items():
                kid_upper = kid_name.upper()
                kid_type, kid_extra, _, _ = _parse_item_info(kid_info)

                metplus_configs.append(f'{metplus_name}_{kid_upper}')
                metplus_configs.append(f'{metplus_prefix}{kid_upper}')

                kid_args = _parse_extra_args(kid_extra)
                child_item = METConfig(
                    name=kid_name,
                    data_type=kid_type,
                    metplus_configs=metplus_configs.copy(),
                    extra_args=kid_args,
                )
                children.append(child_item)

                # reset metplus config list for next kid
                metplus_configs.clear()

            # set metplus_configs
            metplus_configs = None

        extra_args = _parse_extra_args(extra)
        dict_item = (
            METConfig(
                name=name,
                data_type=data_type,
                metplus_configs=metplus_configs,
                extra_args=extra_args,
                children=children,
            )
        )
        dict_items.append(dict_item)

    final_met_config = METConfig(
        name=dict_name,
        data_type='dict',
        children=dict_items,
    )

    return add_met_config_item(config,
                               final_met_config,
                               output_dict)


def add_met_config_item(config, item, output_dict, depth=0):
    """! Reads info from METConfig object, gets value from
    METplusConfig, and formats it based on the specifications. Sets
    value in output dictionary with key starting with METPLUS_.

    @param config METplusConfig object to read
    @param item METConfig object to read and determine what to get
    @param output_dict dictionary to save formatted output
    @param depth counter to check if item being processed is nested within
     another variable or not. If depth is 0, it is a top level variable.
     This is used internally by this function and shouldn't be supplied
     outside of calls within this function.
    """
    env_var_name = item.env_var_name.upper()
    if not env_var_name.startswith('METPLUS_'):
        env_var_name = f'METPLUS_{env_var_name}'

    # handle dictionary or dictionary list item
    if 'dict' in item.data_type:
        tmp_dict = {}
        # handle list of dictionaries (dictlist)
        if isinstance(item.children, dict):
            dict_string = format_met_config_dict_list(config, item.name, item.children)
            if dict_string is None:
                return False
        # handle dictionary with list of children
        else:
            for child in item.children:
                if not add_met_config_item(config, child, tmp_dict,
                                           depth=depth+1):
                    return False

            dict_string = format_met_config(item.data_type,
                                            tmp_dict,
                                            item.name,
                                            keys=None)

        # if handling dict MET config that is not nested inside another
        if not depth and item.data_type == 'dict':
            env_var_name = f'{env_var_name}_DICT'

        output_dict[env_var_name] = dict_string
        return True

    # handle non-dictionary item
    set_met_config = set_met_config_function(item.data_type)
    if not set_met_config:
        return False

    return set_met_config(config,
                          output_dict,
                          item.metplus_configs,
                          item.name,
                          c_dict_key=env_var_name,
                          **item.extra_args)


def get_met_config_dict_list(config, app_name, dict_name, dict_items, parent=None):
    """! Read METplusConfig and format MET config variables that are a list of
    dictionaries. Sets value in output dict with key starting with METPLUS_.

    @param config METplusConfig object to read
    @param app_name name of application to find wrapper-specific variables
    @param output_dict dictionary to save formatted output
    @param dict_name name of MET dictionary variable
    @param dict_items dictionary where the key is name of variable inside MET
     dictionary and the value is info about the item (see parse_item_info
     function for more information)
    @param parent optional name of dictionary that contains the item (nested
     dictionaries)
    """
    regex_end = r'(\d*)_(\w+)$'
    if not parent:
        search_string = f'{app_name}_{dict_name}'.upper()
        regex = r'^' + search_string + regex_end
        indices = find_indices_in_config_section(regex, config,
                                                 index_index=1,
                                                 id_index=2)
    else:
        search_string = f'{app_name}_{parent}_{dict_name}'.upper()
        regex = r'^' + search_string + regex_end
        indices = find_indices_in_config_section(regex, config,
                                                 index_index=1,
                                                 id_index=2)
        # if no indices were found, try again excluding sub dict name
        if not indices:
            search_string = f'{app_name}_{parent}'.upper()
            regex = r'^' + search_string + regex_end
            indices = find_indices_in_config_section(regex, config,
                                                     index_index=1,
                                                     id_index=2)

    all_met_config_items = {}
    for index, _ in indices.items():
        # read all variables for each index
        met_config_items = []
        for name, item_info in dict_items.items():
            data_type, extra, kids, nicknames = _parse_item_info(item_info)
            metplus_configs = [f'{search_string}{index}_{name.upper()}']
            extra_args = _parse_extra_args(extra)
            item = METConfig(name=name,
                             data_type=data_type,
                             metplus_configs=metplus_configs,
                             extra_args=extra_args,
                             )

            met_config_items.append(item)

        all_met_config_items[index] = met_config_items

    return all_met_config_items


def add_met_config_dict_list(config, app_name, output_dict, dict_name,
                             dict_items):
    is_ok = True
    all_met_configs = get_met_config_dict_list(config, app_name, dict_name, dict_items)
    if all_met_configs is None:
        return False
    output_string = format_met_config_dict_list(config, dict_name, all_met_configs)
    if output_string is None:
        is_ok = False

    output_dict[f'METPLUS_{dict_name.upper()}_LIST'] = output_string
    return is_ok


def format_met_config_dict_list(config, dict_name, all_met_configs):
    all_met_config_items = {}
    for index, met_configs in all_met_configs.items():
        met_config_items = {}
        for met_config in met_configs:
            if not add_met_config_item(config, met_config, met_config_items):
                return None

        dict_string = format_met_config('dict', met_config_items, name='')
        all_met_config_items[index] = dict_string

    # format list of dictionaries
    output_string = format_met_config('list', all_met_config_items, dict_name)
    return output_string


def format_met_config(data_type, c_dict, name, keys=None):
    """! Return formatted variable named <name> with any <items> if they
    are set to a value. If none of the items are set, return empty string

    @param data_type type of value to format
    @param c_dict config dictionary to read values from
    @param name name of dictionary to create
    @param keys list of c_dict keys to use if they are set. If unset (None)
     then read all keys from c_dict
    @returns MET config formatted dictionary/list
     if any items are set, or empty string if not
    """
    values = []
    if keys is None:
        keys = c_dict.keys()

    for key in keys:
        value = c_dict.get(key)
        if value:
            values.append(str(value))

    # if none of the keys are set to a value in dict, return empty string
    if not values:
        return ''

    # separate items with commas if data type is list (not dictlist)
    if data_type == 'list':
        output = ','.join(values)
    else:
        output = ''.join(values)

    # add curly braces if dictionary
    if 'dict' in data_type:
        output = f"{{{output}}}"

    # add square braces if list
    if 'list' in data_type:
        output = f"[{output}];"

    # if name is not empty, add variable name and equals sign
    if name:
        output = f'{name} = {output}'
    return output


def set_met_config_function(item_type):
    """! Return function to use based on item type

         @param item_type type of MET config variable to obtain
         Valid values: list, string, int, float, thresh, bool
         @returns function to use or None if invalid type provided
    """
    if item_type == 'int':
        return set_met_config_int
    elif item_type == 'string':
        return set_met_config_string
    elif item_type == 'list':
        return set_met_config_list
    elif item_type == 'float':
        return set_met_config_float
    elif item_type == 'thresh':
        return set_met_config_thresh
    elif item_type == 'bool':
        return set_met_config_bool
    else:
        raise ValueError(f"Invalid argument for item type: {item_type}")


def _get_config_or_default(mp_config_name, get_function,
                           default=None):
    conf_value = ''

    # if no possible METplus config variables are not set
    if mp_config_name is None:
        # if no default defined, return without doing anything
        if not default:
            return None

    # if METplus config variable is set, read the value
    else:
        conf_value = get_function('config',
                                  mp_config_name,
                                  '')

    # if variable is not set and there is a default defined, set default
    if not conf_value and default:
        conf_value = default

    return conf_value


def set_met_config_list(config, c_dict, mp_config, met_config_name,
                        c_dict_key=None, **kwargs):
    """!Get list from METplus configuration file and format it to be passed
     into a MET configuration file. Set c_dict item with formatted string.

    @param config METplusConfig to read values from
    @param c_dict configuration dictionary to set
    @param mp_config_name METplus configuration variable name. Assumed to be
     in the [config] section. Value can be a comma-separated list of items.
    @param met_config name of MET configuration variable to set. Also used
     to determine the key in c_dict to set (upper-case)
    @param c_dict_key optional argument to specify c_dict key to store result.
     If set to None (default) then use upper-case of met_config_name
    @param allow_empty if True, if METplus config variable is set
     but is an empty string, then set the c_dict value to an empty
     list. If False, behavior is the same as when the variable is
     not set at all, which is to not set anything for the c_dict
     value
    @param remove_quotes if True, output value without quotes.
     Default value is False
    @param default (Optional) if set, use this value as default
     if config is not set
    @returns False if there was an error trying to read/set the value or True
    if everything ran fine even if no value was set
    """
    if c_dict is None:
        return False

    mp_config_name = config.get_mp_config_name(mp_config)
    conf_value = _get_config_or_default(
        mp_config_name,
        get_function=config.getraw,
        default=kwargs.get('default')
    )
    if conf_value is None:
        return True

    # convert value from config to a list
    conf_values = getlist(conf_value)

    # if no values are found and the value cannot be set to an empty list
    # e.g. the MET default is non-empty, return without setting anything
    if not conf_values and not kwargs.get('allow_empty', False):
        return True

    out_values = []
    for conf_value in conf_values:
        remove_quotes = kwargs.get('remove_quotes', False)
        # if not removing quotes, escape any quotes found in list items
        if not remove_quotes:
            conf_value = conf_value.replace('"', '\\"')

        conf_value = util_remove_quotes(conf_value)
        if not remove_quotes:
            conf_value = f'"{conf_value}"'

        if kwargs.get('uppercase', False):
            conf_value = conf_value.upper()

        out_values.append(conf_value)
    out_value = f"[{', '.join(out_values)}]"

    if met_config_name:
        out_value = f'{met_config_name} = {out_value};'

    c_key = c_dict_key if c_dict_key else met_config_name.upper()
    c_dict[c_key] = out_value

    return True


def set_met_config_string(config, c_dict, mp_config, met_config_name,
                          c_dict_key=None, **kwargs):
    """!Get string from METplus configuration file and format it to be passed
     into a MET configuration file. Set c_dict item with formatted string.

    @param c_dict configuration dictionary to set
    @param mp_config METplus configuration variable name. Assumed to be
     in the [config] section. Value can be a comma-separated list of items.
    @param met_config_name name of MET configuration variable to set. Also used
     to determine the key in c_dict to set (upper-case)
    @param c_dict_key optional argument to specify c_dict key to store result. If
     set to None (default) then use upper-case of met_config_name
    @param remove_quotes if True, output value without quotes.
     Default value is False
    @param to_grid if True, format to_grid value
     Default value is False
    @param default (Optional) if set, use this value as default
     if config is not set
    @param add_x if True, add (x) to variable name, e.g. convert(x)
     Default value is False
    @returns False if there was an error trying to read/set the value or True
    if everything ran fine even if no value was set
    """
    if c_dict is None:
        return False

    mp_config_name = config.get_mp_config_name(mp_config)
    conf_value = _get_config_or_default(
        mp_config_name,
        get_function=config.getraw,
        default=kwargs.get('default')
    )
    if not conf_value:
        return True

    conf_value = util_remove_quotes(conf_value)
    # add quotes back if remote quotes is False
    if not kwargs.get('remove_quotes'):
        conf_value = f'"{conf_value}"'

    if kwargs.get('uppercase', False):
        conf_value = conf_value.upper()

    if kwargs.get('to_grid', False):
        conf_value = format_regrid_to_grid(conf_value)

    if met_config_name:
        config_name = met_config_name
        if kwargs.get('add_x'):
            config_name = f'{config_name}(x)'
        conf_value = f'{config_name} = {conf_value};'

    c_key = c_dict_key if c_dict_key else met_config_name.upper()
    c_dict[c_key] = conf_value

    return True


def set_met_config_number(config, c_dict, num_type, mp_config,
                          met_config_name, c_dict_key=None):
    """! Get integer from METplus configuration file and format it to be passed
          into a MET configuration file. Set c_dict item with formatted string.

       @param c_dict configuration dictionary to set
       @param num_type type of number to get from config. If set to 'int',
        call getint function. If not, call getfloat function.
       @param mp_config METplus configuration variable name. Assumed to be
        in the [config] section. Value can be a comma-separated list of items.
       @param met_config_name name of MET configuration variable to set.
        Also used to determine the key in c_dict to set (upper-case) if
        c_dict_key is None.
       @param c_dict_key optional argument to specify c_dict key to store
        result. If set to None (default) then use upper-case of met_config_name
       @param default (Optional) if set, use this value as default
        if config is not set
    """
    mp_config_name = config.get_mp_config_name(mp_config)
    if mp_config_name is None:
        return True

    if num_type == 'int':
        conf_value = config.getint('config', mp_config_name)
    else:
        conf_value = config.getfloat('config', mp_config_name)

    if conf_value is None:
        return False
    if conf_value != MISSING_DATA_VALUE:
        if not c_dict_key:
            c_key = met_config_name.upper()
        else:
            c_key = c_dict_key

        if met_config_name:
            out_value = f"{met_config_name} = {str(conf_value)};"
        else:
            out_value = str(conf_value)
        c_dict[c_key] = out_value

    return True


def set_met_config_int(config, c_dict, mp_config_name, met_config_name,
                       c_dict_key=None):
    return set_met_config_number(config, c_dict, 'int',
                                 mp_config_name,
                                 met_config_name,
                                 c_dict_key=c_dict_key)


def set_met_config_float(config, c_dict, mp_config_name,
                         met_config_name, c_dict_key=None):
    return set_met_config_number(config, c_dict, 'float',
                                 mp_config_name,
                                 met_config_name,
                                 c_dict_key=c_dict_key)


def set_met_config_thresh(config, c_dict, mp_config, met_config_name,
                          c_dict_key=None):
    mp_config_name = config.get_mp_config_name(mp_config)
    if mp_config_name is None:
        return True

    conf_value = config.getstr('config', mp_config_name, '')
    if conf_value:
        if get_threshold_via_regex(conf_value) is None:
            config.logger.error(f"Incorrectly formatted threshold: {mp_config_name}")
            return False

        if not c_dict_key:
            c_key = met_config_name.upper()
        else:
            c_key = c_dict_key

        if met_config_name:
            out_value = f"{met_config_name} = {str(conf_value)};"
        else:
            out_value = str(conf_value)

        c_dict[c_key] = out_value

    return True


def set_met_config_bool(config, c_dict, mp_config, met_config_name,
                        c_dict_key=None, **kwargs):
    """! Get boolean from METplus configuration file and format it to be
         passed into a MET configuration file. Set c_dict item with boolean
         value expressed as a string.
         Args:
             @param c_dict configuration dictionary to set
             @param mp_config METplus configuration variable name.
              Assumed to be in the [config] section.
             @param met_config_name name of MET configuration variable to
              set. Also used to determine the key in c_dict to set
              (upper-case)
             @param c_dict_key optional argument to specify c_dict key to
              store result. If set to None (default) then use upper-case of
              met_config_name
             @param uppercase If true, set value to TRUE or FALSE
    """
    mp_config_name = config.get_mp_config_name(mp_config)
    if mp_config_name is None:
        return True
    conf_value = config.getbool('config', mp_config_name, '')
    if conf_value is None:
        config.logger.error(f'Invalid boolean value set for {mp_config_name}')
        return False

    # if not invalid but unset, return without setting c_dict with no error
    if conf_value == '':
        return True

    conf_value = str(conf_value)
    if kwargs.get('uppercase', True):
        conf_value = conf_value.upper()

    if not c_dict_key:
        c_key = met_config_name.upper()
    else:
        c_key = c_dict_key

    conf_value = util_remove_quotes(conf_value)
    if met_config_name:
        conf_value = f'{met_config_name} = {conf_value};'
    c_dict[c_key] = conf_value
    return True


def format_regrid_to_grid(to_grid):
    to_grid = to_grid.strip('"')
    if not to_grid:
        to_grid = 'NONE'

    # if NONE, FCST, or OBS force uppercase, otherwise add quotes
    if to_grid.upper() in ['NONE', 'FCST', 'OBS']:
        to_grid = to_grid.upper()
    else:
        to_grid = f'"{to_grid}"'

    return to_grid


def _parse_item_info(item_info):
    """! Parses info about a MET config dictionary item. The input can
    be a single string that is the data type of the item. It can also be
    a tuple containing 2 to 4 values. The additional values must be
    supplied in order:
    * extra: string of extra information about item, i.e.
      'remove_quotes', 'uppercase', or 'allow_empty'
    * kids: dictionary describing child values (used only for dict items)
      where the key is the name of the variable and the value is item info
      for the child variable in the same format as item_info that is
      parsed in this function
    * nicknames: list of other METplus config variable name that can be
       used to set a value. The app name i.e. GRID_STAT_ is prepended to
       each nickname in the list. Used for backwards compatibility for
       METplus config variables whose name does not match the MET config
       variable name

    @param item_info string or tuple containing information about a
     dictionary item
    @returns tuple of data type, extra info, children, and nicknames or
     None for each tuple value that is not set
    """
    if isinstance(item_info, tuple):
        data_type, *rest = item_info
    else:
        data_type = item_info
        rest = []

    extra = rest.pop(0) if rest else None
    kids = rest.pop(0) if rest else None
    nicknames = rest.pop(0) if rest else None

    return data_type, extra, kids, nicknames


def _parse_extra_args(extra):
    """! Check string for extra option keywords and set them to True in
     dictionary if they are found. Supports 'remove_quotes', 'uppercase',
     'allow_empty', 'to_grid', 'default', and 'add_x'.

        @param extra string to parse for keywords
        @returns dictionary with extra args set if found in string
    """
    extra_args = {}
    if not extra:
        return extra_args

    VALID_EXTRAS = (
        'remove_quotes',
        'uppercase',
        'allow_empty',
        'to_grid',
        'default',
        'add_x',
    )
    for extra_option in VALID_EXTRAS:
        if extra_option in extra:
            extra_args[extra_option] = True
    return extra_args


def handle_climo_dict(config, app_name, output_dict, sub_groups):
    """! Read climo mean/stdev variables with and set env_var_dict
     appropriately. Handle previous environment variables that are used
     by wrapped MET configs pre 4.0 (CLIMO_MEAN_FILE and CLIMO_STDEV_FILE)

    @param config METplusConfig object to read
    @param app_name name of application to find wrapper-specific variables
    @param output_dict dictionary to save formatted output
    @param sub_groups tuple of dictionaries that can contain climo dicts, e.g.
     ('fcst', 'obs'). If None, do not look for climo dicts in other dicts.
    @returns False if config settings are invalid, otherwise True
    """
    items = {
        'file_name': 'list',
        'field': ('list', 'remove_quotes'),
        'regrid': ('dict', '', {
            'method': ('string', 'uppercase,remove_quotes'),
            'width': 'int',
            'vld_thresh': 'float',
            'shape': ('string', 'uppercase,remove_quotes'),
        }),
        'time_interp_method': ('string', 'remove_quotes,uppercase'),
        'match_month': ('bool', 'uppercase'),
        'day_interval': ('string', 'remove_quotes,uppercase'),
        'hour_interval': ('string', 'remove_quotes,uppercase'),
        'file_type': ('string', 'remove_quotes'),
    }
    is_ok = True

    # get MET dictionaries that may contain climo dictionaries
    sub_group_prefixes = [None]
    if isinstance(sub_groups, str):
        sub_group_prefixes += [sub_groups]
    elif isinstance(sub_groups, tuple):
        sub_group_prefixes += list(sub_groups)

    for climo_type in CLIMO_TYPES:
        for sub_group_prefix in sub_group_prefixes:
            # make sure _FILE_NAME is set from INPUT_TEMPLATE/DIR if used
            _read_climo_file_name(climo_type, config, app_name, sub_group_prefix)
            _read_climo_field(climo_type, config, app_name, sub_group_prefix)

            dict_name = f'climo_{climo_type.lower()}'
            if sub_group_prefix:
                dict_name = f'{sub_group_prefix}_{dict_name}'
            add_met_config_dict(config=config, app_name=app_name,
                                output_dict=output_dict,
                                dict_name=dict_name, items=items)
            # remove fcst_ or obs_ prefix from dictionary name
            if sub_group_prefix:
                value = output_dict[f'METPLUS_{dict_name.upper()}_DICT']
                output_dict[f'METPLUS_{dict_name.upper()}_DICT'] = value.removeprefix(f'{sub_group_prefix}_')
            # handle use_fcst or use_obs options for setting field list
            elif not _climo_use_fcst_or_obs_fields(dict_name, config, app_name,
                                                   output_dict):
                is_ok = False

    return is_ok

def _get_climo_prefix(climo_type, app_name, fo_prefix):
    """!Build prefix string for climatology config variables.
    If fo_prefix is set, return uppercase {app_name}_{fo_prefix}_{climo_type},
    otherwise return uppercase {app_name}_{climo_type}

    @param climo_type type of climo field (mean or stdev)
    @param app_name name of application to find wrapper-specific variables
    @param fo_prefix forecast or obs prefix, e.g. 'fcst' or 'obs' or None if
     no prefix should be used.
    """
    # prefix i.e. GRID_STAT_CLIMO_MEAN_ or GRID_STAT_FCST_CLIMO_MEAN_
    prefix = f'CLIMO_{climo_type}_'
    if fo_prefix:
        prefix = f'{fo_prefix}_{prefix}'
    return f'{app_name}_{prefix}'.upper()

def _read_climo_file_name(climo_type, config, app_name, fo_prefix=None):
    """!Used to support pre v4.0 variables.
    Check values for {APP}_CLIMO_{climo_type}_ variables FILE_NAME,
    INPUT_TEMPLATE, and INPUT_DIR. If FILE_NAME is set, use it and warn
    if the INPUT_TEMPLATE/DIR variables are also set. If FILE_NAME is not
    set, read template and dir variables and format the values to set
    FILE_NAME, i.e. the variables:
      GRID_STAT_CLIMO_MEAN_INPUT_TEMPLATE = a, b
      GRID_STAT_CLIMO_MEAN_INPUT_DIR = /some/dir
    will set:
      GRID_STAT_CLIMO_MEAN_FILE_NAME = /some/dir/a, some/dir/b
    If fo_prefix is not None, add capitalized value in front of climo type.

    @param climo_type type of climo field (mean or stdev)
    @param config METplusConfig object to read
    @param app_name name of application to find wrapper-specific variables
    @param fo_prefix forecast or obs prefix, e.g. 'fcst' or 'obs' or None if
     no prefix should be used.
    """
    prefix = _get_climo_prefix(climo_type, app_name, fo_prefix)

    input_dir = config.getdir_nocheck(f'{prefix}INPUT_DIR', '')
    input_template = config.getraw('config', f'{prefix}INPUT_TEMPLATE', '')
    file_name = config.getraw('config', f'{prefix}FILE_NAME', '')

    # if input template is not set, nothing to do
    if not input_template:
        return

    # if input template is set and file name is also set,
    # warn and use file name values
    if file_name:
        config.logger.warning(f'Both {prefix}INPUT_TEMPLATE and '
                              f'{prefix}FILE_NAME are set. Using '
                              f'value set in {prefix}FILE_NAME '
                              f'({file_name})')
        return

    template_list_string = input_template
    # if file name is not set but template is, set file name from template
    # if dir is set and not python embedding,
    # prepend it to each template in list
    if input_dir and input_template not in PYTHON_EMBEDDING_TYPES:
        template_list = getlist(input_template)
        for index, template in enumerate(template_list):
            template_list[index] = os.path.join(input_dir, template)

        # change formatted list back to string
        template_list_string = ','.join(template_list)

    config.set('config', f'{prefix}FILE_NAME', template_list_string)


def _read_climo_field(climo_type, config, app_name, fo_prefix=None):
    """!Check values for {APP}_CLIMO_{climo_type}_ variable FIELD and
    VAR<n>_[NAME/LEVELS/OPTIONS]. If VAR<n> variables are set, format those
    values and set the FIELD variable in the METplusConfig.
    If FIELD is also set warn that it the value will be replaced. If only
    FIELD is set, use that value.
    The variables:
      GRID_STAT_CLIMO_MEAN_VAR1_NAME = TMP
      GRID_STAT_CLIMO_MEAN_VAR1_LEVELS = "(*,*)"
    will set:
      GRID_STAT_CLIMO_MEAN_FIELD = {name="TMP"; level="(*,*)";}
    Used to allow users to format the field info for climo fields in the same
    way as other field info such as FCST or OBS.

    @param climo_type type of climo field (mean or stdev)
    @param config METplusConfig object to read
    @param app_name name of application to find wrapper-specific variables
    @param fo_prefix forecast or obs prefix, e.g. 'fcst' or 'obs' or None if
     no prefix should be used.
    """
    # prefix i.e. GRID_STAT_CLIMO_MEAN or GRID_STAT_FCST_CLIMO_MEAN
    prefix = _get_climo_prefix(climo_type, app_name, fo_prefix).rstrip('_')

    field = config.getraw('config', f'{prefix}_FIELD', '')
    var_list = parse_var_list(config, data_type=prefix)

    # if field info is not set using VAR<n> variables, nothing to do
    if not var_list:
        return

    # if FIELD is set and VAR<n> is also set, warn and use VAR<n> values
    if field:
        config.logger.warning(f'Both {prefix}_FIELD and '
                              f'{prefix}_VAR<n>_* variables are set. Using '
                              f'values set in {prefix}_VAR<n>_* variables')

    # format var list and set it to the _FIELD value
    all_formatted = format_all_field_info(c_dict={},
                                          var_list=var_list,
                                          data_type=prefix)

    config.set('config', f'{prefix}_FIELD', all_formatted)


def _climo_use_fcst_or_obs_fields(dict_name, config, app_name, output_dict):
    """! If climo field is not explicitly set, check if config is set
     to use forecast or observation fields.

    @param dict_name name of climo to check: climo_mean or climo_stdev
    @param config METplusConfig object to read
    @param app_name name of application to find wrapper-specific variables
    @param output_dict dictionary to save formatted output
    @returns False if config settings are invalid, otherwise True
    """
    # if {APP}_CLIMO_[MEAN/STDEV]_FIELD is set, do nothing
    field_conf = f'{app_name}_{dict_name}_FIELD'.upper()
    if config.has_option('config', field_conf):
        return True

    use_fcst_conf = f'{app_name}_{dict_name}_USE_FCST'.upper()
    use_obs_conf = f'{app_name}_{dict_name}_USE_OBS'.upper()

    use_fcst = config.getbool('config', use_fcst_conf, False)
    use_obs = config.getbool('config', use_obs_conf, False)

    # if both are set, report an error
    if use_fcst and use_obs:
        config.logger.error(f'Cannot set both {use_fcst_conf} and '
                            f'{use_obs_conf} in config.')
        return False

    # if neither are set, do nothing
    if not use_fcst and not use_obs:
        return True

    env_var_name = f'METPLUS_{dict_name.upper()}_DICT'
    rvalue = 'fcst' if use_fcst else 'obs'

    output_dict[env_var_name] += f'{dict_name} = {rvalue};'
    # rvalue = '${METPLUS_FCST_FIELD}' if use_fcst else '${METPLUS_OBS_FIELD}'
    # for fcst_obs in ('FCST', 'OBS'):
    #     if output_dict[f'METPLUS_{fcst_obs}_{dict_name.upper()}_DICT'].endswith('}'):
    #         output_dict[f'METPLUS_{fcst_obs}_{dict_name.upper()}_DICT'] = f"{output_dict[f'METPLUS_{fcst_obs}_{dict_name.upper()}_DICT'][0:-1]}{rvalue}}}"
    #     else:
    #         output_dict[f'METPLUS_{fcst_obs}_{dict_name.upper()}_DICT'] = f'{dict_name} = {{{rvalue}}}'
    return True
