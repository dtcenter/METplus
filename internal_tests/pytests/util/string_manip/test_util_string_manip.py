#!/usr/bin/env python3

import pytest

from csv import reader

from metplus.util.string_manip import *
from metplus.util.string_manip import _fix_list

@pytest.mark.parametrize(
    'before, after', [
        ('string', 'string'),
        ('"string"', 'string'),
        ('', ''),
        ('""', ''),
        (None, ''),
    ]
)
def test_remove_quotes(before, after):
    assert(remove_quotes(before) == after)

@pytest.mark.parametrize(
    'string_list, output_list', [
        # 0: list of strings
        ('gt2.7, >3.6, eq42',
         ['gt2.7', '>3.6', 'eq42']),
        # 1: one string has commas within quotes
        ('gt2.7, >3.6, eq42, "has,commas,in,it"',
         ['gt2.7', '>3.6', 'eq42', 'has,commas,in,it']),
        # 2: empty string
        ('',
         []),
        ]
)
def test_getlist(string_list, output_list):
    test_list = getlist(string_list)
    assert test_list == output_list

def test_getlist_int():
    string_list = '6, 7, 42'
    test_list = getlistint(string_list)
    assert test_list == [6, 7, 42]

@pytest.mark.parametrize(
    'list_string, output_list', [
        ('begin_end_incr(3,12,3)',
         ['3', '6', '9', '12']),

        ('1,2,3,4',
         ['1', '2', '3', '4']),

        (' 1,2,3,4',
         ['1', '2', '3', '4']),

        ('1,2,3,4 ',
         ['1', '2', '3', '4']),

        (' 1,2,3,4 ',
         ['1', '2', '3', '4']),

        ('1, 2,3,4',
         ['1', '2', '3', '4']),

        ('1,2, 3, 4',
         ['1', '2', '3', '4']),

        ('begin_end_incr( 3,12 , 3)',
         ['3', '6', '9', '12']),

        ('begin_end_incr(0,10,2)',
         ['0', '2', '4', '6', '8', '10']),

        ('begin_end_incr(10,0,-2)',
         ['10', '8', '6', '4', '2', '0']),

        ('begin_end_incr(2,2,20)',
         ['2']),

        ('begin_end_incr(0,2,1), begin_end_incr(3,9,3)',
         ['0','1','2','3','6','9']),

        ('mem_begin_end_incr(0,2,1), mem_begin_end_incr(3,9,3)',
         ['mem_0','mem_1','mem_2','mem_3','mem_6','mem_9']),

        ('mem_begin_end_incr(0,2,1,3), mem_begin_end_incr(3,12,3,3)',
         ['mem_000', 'mem_001', 'mem_002', 'mem_003', 'mem_006', 'mem_009', 'mem_012']),

        ('begin_end_incr(0,10,2)H, 12',  [ '0H', '2H', '4H', '6H', '8H', '10H', '12']),

        ('begin_end_incr(0,10800,3600)S, 4H',  [ '0S', '3600S', '7200S', '10800S', '4H']),

        ('data.{init?fmt=%Y%m%d%H?shift=begin_end_incr(0, 3, 3)H}.ext',
         ['data.{init?fmt=%Y%m%d%H?shift=0H}.ext',
          'data.{init?fmt=%Y%m%d%H?shift=3H}.ext',
          ]),

    ]
)
def test_getlist_begin_end_incr(list_string, output_list):
    assert getlist(list_string) == output_list

@pytest.mark.parametrize(
     'list_str, expected_fixed_list', [
         ('some,items,here', ['some',
                              'items',
                              'here']),
         ('(*,*)', ['(*,*)']),
        ("-type solar_alt -thresh 'ge45' -name solar_altitude_ge_45_mask -input_field 'name=\"TEC\"; level=\"(0,*,*)\"; file_type=NETCDF_NCCF;' -mask_field 'name=\"TEC\"; level=\"(0,*,*)\"; file_type=NETCDF_NCCF;\'",
        ["-type solar_alt -thresh 'ge45' -name solar_altitude_ge_45_mask -input_field 'name=\"TEC\"; level=\"(0,*,*)\"; file_type=NETCDF_NCCF;' -mask_field 'name=\"TEC\"; level=\"(0,*,*)\"; file_type=NETCDF_NCCF;\'"]),
        ("(*,*),'level=\"(0,*,*)\"' -censor_thresh [lt12.3,gt8.8],other", ['(*,*)',
                                                                           "'level=\"(0,*,*)\"' -censor_thresh [lt12.3,gt8.8]",
                                                                           'other']),
     ]
)
def test_fix_list(list_str, expected_fixed_list):
    item_list = list(reader([list_str]))[0]
    fixed_list = _fix_list(item_list)
    print("FIXED LIST:")
    for fixed in fixed_list:
        print(f"ITEM: {fixed}")

    print("EXPECTED LIST")
    for expected in expected_fixed_list:
        print(f"ITEM: {expected}")

    assert(fixed_list == expected_fixed_list)
