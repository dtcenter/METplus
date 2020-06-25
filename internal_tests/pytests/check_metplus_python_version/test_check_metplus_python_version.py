#!/usr/bin/env python

import pytest

from metplus.util import metplus_check_python_version as check_mp_py

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
def test_check_metplus_python(user, supported, torf):
    assert(check_mp_py.check_metplus_python_version(user, supported) == torf)
