#!/usr/bin/env python3

import pytest

from metplus.util import METConfig

@pytest.mark.parametrize(
    'name, data_type, mp_configs, extra_args', [
        ('beg', 'int', 'BEG', None),
        ('end', 'int', ['END'], None),
    ]
)
def test_met_config_info(name, data_type, mp_configs, extra_args):
    item = METConfig(name=name, data_type=data_type)

    item.metplus_configs = mp_configs
    item.extra_args = extra_args

    assert(item.name == name)
    assert(item.data_type == data_type)
    if isinstance(mp_configs, list):
        assert(item.metplus_configs == mp_configs)
    else:
        assert(item.metplus_configs == [mp_configs])

    if not extra_args:
        assert(item.extra_args == {})

