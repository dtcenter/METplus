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
        # 2: one string has commas and spaces within quotes
        ('gt2.7, >3.6, eq42, "has some,commas,in,it"',
         ['gt2.7', '>3.6', 'eq42', 'has some,commas,in,it']),
        # 3: empty string
        ('',
         []),
        # 4: string with commas between ()s
        ('name="CLM_NAME"; level="(0,0,*,*)"',
         ['name="CLM_NAME"; level="(0,0,*,*)"']),
        # 5: string with commas between ()s and commas not between ()s
        ('name="CLM_NAME"; level="(0,0,*,*)";, name="OTHER"; level="A06"',
         ['name="CLM_NAME"; level="(0,0,*,*)";', 'name="OTHER"; level="A06"']),
        # 6: string with commas between ()s within {}s
        ('{name="CLM_NAME"; level="(0,0,*,*)";}',
         ['{name="CLM_NAME"; level="(0,0,*,*)";}']),
        # 7: multiple {}s with string with commas between ()s
        ('{name="CLM_NAME"; level="(0,0,*,*)";},{name="CLM_NAME"; level="(0,0,*,*)";}',
         ['{name="CLM_NAME"; level="(0,0,*,*)";}',
          '{name="CLM_NAME"; level="(0,0,*,*)";}']),
        # 8: read example with commas beween ()s
        ('-input_field \'name="TEC"; level="({valid?fmt=%Y%m%d_%H%M%S},*,*)"; file_type=NETCDF_NCCF;\'',
         ['-input_field \'name="TEC"; level="({valid?fmt=%Y%m%d_%H%M%S},*,*)"; file_type=NETCDF_NCCF;\'']),
        # 9: read example commas separating quotes within []s
        ('{name="UGRD"; level=["P850","P500","P250"];}',
         ['{name="UGRD"; level=["P850","P500","P250"];}']),
        # 10: multiples {}s with commas separating quotes within []s
        ('{name="UGRD"; level=["P850","P500","P250"];}, {name="UGRD"; level=["P750","P600"];}',
         ['{name="UGRD"; level=["P850","P500","P250"];}', '{name="UGRD"; level=["P750","P600"];}']),
        # 11: list with square braces and ending semi-colon (MET format)
        ('["{ENV[MET_BUILD_BASE]}/share/met/poly/CAR.poly", "{ENV[MET_BUILD_BASE]}/share/met/poly/GLF.poly"];',
         ["{ENV[MET_BUILD_BASE]}/share/met/poly/CAR.poly", "{ENV[MET_BUILD_BASE]}/share/met/poly/GLF.poly"]),
        # 12: list with square braces and ending semi-colon (MET format) no quotes
        ('[MET_BASE/poly/LMV.poly];',
         ["MET_BASE/poly/LMV.poly"]),
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
