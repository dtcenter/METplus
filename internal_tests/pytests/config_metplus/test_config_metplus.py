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
    both_parm_base = os.path.join(test_data_dir, 'both')

    old_list = ['metplus_config/metplus_system.conf',
                'metplus_config/metplus_data.conf',
                'metplus_config/metplus_runtime.conf',
                'metplus_config/metplus_logging.conf']
    new_list = ['metplus_config/defaults.conf']

    # old conf files should be parsed before new if both are found
    both_list = old_list + new_list

    expected_old = [os.path.join(old_parm_base, item) for item in old_list]
    expected_new = [os.path.join(new_parm_base, item) for item in new_list]
    expected_both = [os.path.join(both_parm_base, item) for item in both_list]

    actual_old = config_metplus._get_default_config_list(old_parm_base)
    actual_new = config_metplus._get_default_config_list(new_parm_base)
    actual_both = config_metplus._get_default_config_list(both_parm_base)
    assert actual_old == expected_old
    assert actual_new == expected_new
    assert actual_both == expected_both
