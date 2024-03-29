#!/usr/bin/env python3

import pytest

from metplus.wrappers.met_db_load_wrapper import METDbLoadWrapper


@pytest.mark.parametrize(
    'filename, expected_result', [
        ('myfile.png', False),
        ('anotherfile.txt', False),
        ('goodfile.stat', True),
        ('goodfile.tcst', True),
        ('mode_goodfile.txt', True),
        ('mtd_goodfile.txt', True),
        ('monster_badfile.txt', False),
    ]
)
@pytest.mark.wrapper
def test_is_loadable_file(filename, expected_result):
    assert METDbLoadWrapper._is_loadable_file(filename) == expected_result


@pytest.mark.parametrize(
    'filenames, expected_result', [
        (['myfile.png',
          'anotherfile.txt'], False),
        (['myfile.png',
          'goodfile.stat'], True),
        (['myfile.png',
          'goodfile.tcst',
          'anotherfile.txt'], True),
        (['myfile.png',
          'mode_goodfile.txt'], True),
        (['myfile.png',
          'mtd_goodfile.txt'], True),
        (['myfile.png',
          'monster_badfile.txt'], False),
        ([], False),
    ]
)
@pytest.mark.wrapper
def test_has_loadable_file(filenames, expected_result):
    assert METDbLoadWrapper._has_loadable_file(filenames) == expected_result
