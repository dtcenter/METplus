#!/usr/bin/env python

import pytest

from metplus.util import metplus_check

# test that:
#  the same version of python passes
#  a later version of python passes
#  an earlier version of python fails
@pytest.mark.parametrize(
    'user, supported, torf', [
        ('3.6.3', '3.6.3', True), # same
        ('2.7',   '3.6.3', False), # earlier major
        ('3.6.2', '3.6.3', False), # earlier bugfix
        ('3.6.4', '3.6.3', True), # later bugfix
        ('3.5.5', '3.6.3', False), # earlier minor, later bugfix
        ('3.8.1', '3.6.3', True), # later minor, earlier bugfix
        ('4.0.0', '3.6.3', True), # later major
    ]
)
def test_metplus_check_python(user, supported, torf):
    assert(metplus_check.metplus_check_python_version(user, supported) == torf)

# checking METPLUS_DISABLE_PLOT_WRAPPERS and METPLUS_ENABLE_PLOT_WRAPPERS
# both cannot be set
@pytest.mark.parametrize(
    'env_vars, expected_result', [
        ({}, True), # neither set
        ({'METPLUS_DISABLE_PLOT_WRAPPERS': 'yes'}, True), #disable set
        ({'METPLUS_ENABLE_PLOT_WRAPPERS': 'yes'}, True), #enable set
        ({'METPLUS_ENABLE_PLOT_WRAPPERS': 'yes',
          'METPLUS_DISABLE_PLOT_WRAPPERS': 'yes'}, False), #both set
    ]
)
def test_metplus_check_environment_variables(env_vars, expected_result):
    assert(metplus_check.metplus_check_environment_variables(env_vars) == expected_result)

# checking METPLUS_DISABLE_PLOT_WRAPPERS and METPLUS_ENABLE_PLOT_WRAPPERS to determine
# if plot wrappers are enabled. Default is True (run). Both cannot be set
@pytest.mark.parametrize(
    'env_vars, expected_result', [
        ({}, True), # neither set
        ({'METPLUS_DISABLE_PLOT_WRAPPERS': 'yes'}, False), #disable set
        ({'METPLUS_ENABLE_PLOT_WRAPPERS': 'yes'}, True), #enable set
        ({'METPLUS_ENABLE_PLOT_WRAPPERS': 'yes',
          'METPLUS_DISABLE_PLOT_WRAPPERS': 'yes'}, None), #both set
    ]
)
def test_plot_wrappers_are_enabled(env_vars, expected_result):
    assert(metplus_check.plot_wrappers_are_enabled(env_vars) == expected_result)

@pytest.mark.parametrize(
    'value, expected_result', [
        ('true', True),
        ('True', True),
        ('TRUE', True),
        ('yes', True),
        ('YES', True),
        ('on', True),
        ('ON', True),
        ('1', True),
        ('T', True),
        ('t', True),
        ('pizza', True),
        ('False', False),
        ('false', False),
        ('FALSE', False),
        ('no', False),
        ('NO', False),
        ('off', False),
        ('OFF', False),
        ('0', False),
        ('F', False),
        ('f', False),
    ]
)
def test_evaluates_to_true(value, expected_result):
    assert(metplus_check.evaluates_to_true(value) == expected_result)
