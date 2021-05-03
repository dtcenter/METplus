#!/usr/bin/env python3

import pytest
import os

from metplus.util import config_metplus

def test_get_default_config_list():
    test_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 os.pardir,
                                                 os.pardir,
                                                 'data',
                                                 'config_metplus'))
    old_parm_base = os.path.join(test_data_dir, 'old')
    new_parm_base = os.path.join(test_data_dir, 'new')

    old_list = ['metplus_config/metplus_system.conf',
                'metplus_config/metplus_data.conf',
                'metplus_config/metplus_runtime.conf',
                'metplus_config/metplus_logging.conf']
    new_list = ['metplus_config/defaults.conf']
    old_config = [os.path.join(old_parm_base, item) for item in old_list]
    new_config = [os.path.join(new_parm_base, item) for item in new_list]

    assert config_metplus.get_default_config_list(old_parm_base) == old_config
    assert config_metplus.get_default_config_list(new_parm_base) == new_config
