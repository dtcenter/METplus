"""
Program Name: met_config.py
Contact(s): George McCabe
Abstract:
History Log:  Initial version
Usage:
Parameters: None
Input Files: N/A
Output Files: N/A
"""

import os

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

        if children:
            if 'dict' not in self.data_type:
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
