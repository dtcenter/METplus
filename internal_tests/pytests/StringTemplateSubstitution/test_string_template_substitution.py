#!/usr/bin/env python

import pytest
import logging
import datetime

from metplus.util import do_string_sub, parse_template
from metplus.util import get_tags,format_one_time_item, format_hms
from metplus.util import add_to_dict, populate_match_dict, get_fmt_info

def test_cycle_hour():
    cycle_string = 0
    valid_string = datetime.datetime.strptime("20180103", '%Y%m%d')
    templ = "prefix.{valid?fmt=%Y%m%d}.tm{cycle?fmt=%2H}"
    expected_filename = "prefix.20180103.tm00"
    filename = do_string_sub(templ, valid=valid_string, cycle=cycle_string)
    assert(filename == expected_filename)


def test_offset_hour():
    expected_hour = "03"
    offset = 10800
    templ = "{offset?fmt=%2H}"
    offset_hour = do_string_sub(templ, offset=offset)
    assert (offset_hour == expected_hour)

def test_gdas_substitution():
    # Test that the string template substitution works correctly for GDAS
    # prepbufr files, which do not make use of the cycle hour or the offset
    # to generate the valid time.
    valid_string = "2018010411"
    valid_obj = datetime.datetime.strptime(valid_string, '%Y%m%d%H')
    templ = "prepbufr.gdas.{valid?fmt=%Y%m%d%H}.nc"
    expected_filename = 'prepbufr.gdas.' + valid_string + '.nc'
    filename = do_string_sub(templ, valid=valid_obj)
    assert(filename == expected_filename)

def test_hh_lead():
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%HH}h"
    filepath = "1987020103_A03h"
    out = parse_template(template,
                         filepath)
    ftime = out['valid'].strftime('%Y%m%d%H%M')
    assert(ftime == "198702010600")


def test_hhh_lead():
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%HHH}h"
    filepath = "1987020103_A003h"
    out = parse_template(template,
                         filepath)
    ftime = out['valid'].strftime('%Y%m%d%H%M')
    assert(ftime == "198702010600")


def test_2h_lead():
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%.2H}h"
    filepath = "1987020103_A03h"
    out = parse_template(template,
                         filepath)
    ftime = out['valid'].strftime('%Y%m%d%H%M')
    assert(ftime == "198702010600")


def test_3h_lead():
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%.3H}h"
    filepath = "1987020103_A003h"
    out = parse_template(template,
                         filepath)
    ftime = out['valid'].strftime('%Y%m%d%H%M')
    assert(ftime == "198702010600")


def test_h_lead_no_pad_1_digit():
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%1H}h"
    filepath = "1987020103_A3h"
    out = parse_template(template,
                         filepath)
    ftime = out['valid'].strftime('%Y%m%d%H%M')
    assert(ftime == "198702010600")


def test_h_lead_no_pad_2_digit():
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%H}h"
    filepath = "1987020103_A12h"
    out = parse_template(template,
                         filepath)
    ftime = out['valid'].strftime('%Y%m%d%H%M')
    assert(ftime == "198702011500")


def test_h_lead_no_pad_3_digit():
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%H}h"
    filepath = "1987020103_A102h"
    out = parse_template(template,
                         filepath)
    ftime = out['valid'].strftime('%Y%m%d%H%M')
    assert(ftime == "198702050900")


def test_h_lead_no_pad_1_digit_sub():
    file_template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%1H}h"
    init_time = datetime.datetime.strptime("1987020103", '%Y%m%d%H')
    lead_time = int("3") * 3600
    out_string = do_string_sub(file_template,
                               init=init_time,
                               lead=lead_time)
    assert(out_string == "1987020103_A3h")


def test_h_lead_no_pad_2_digit_sub():
    file_template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%1H}h"
    init_time = datetime.datetime.strptime("1987020103", '%Y%m%d%H')
    lead_time = int("12") * 3600
    out_string = do_string_sub(file_template,
                               init=init_time,
                               lead=lead_time)
    assert(out_string == "1987020103_A12h")


def test_h_lead_no_pad_3_digit_sub():
    file_template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%1H}h"
    init_time = datetime.datetime.strptime("1987020103", '%Y%m%d%H')
    lead_time = int("102") * 3600
    out_string = do_string_sub(file_template,
                               init=init_time,
                               lead=lead_time)
    assert(out_string == "1987020103_A102h")


def test_h_lead_pad_1_digit_sub():
    file_template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%.1H}h"
    init_time = datetime.datetime.strptime("1987020103", '%Y%m%d%H')
    lead_time = int("3") * 3600
    out_string = do_string_sub(file_template,
                               init=init_time,
                               lead=lead_time)
    assert(out_string == "1987020103_A3h")


def test_h_lead_pad_2_digit_sub():
    file_template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%.2H}h"
    init_time = datetime.datetime.strptime("1987020103", '%Y%m%d%H')
    lead_time = int("3") * 3600
    out_string = do_string_sub(file_template,
                               init=init_time,
                               lead=lead_time)
    assert(out_string == "1987020103_A03h")


def test_h_lead_pad_2_digit_sub():
    file_template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%.3H}h"
    init_time = datetime.datetime.strptime("1987020103", '%Y%m%d%H')
    lead_time = int("3") * 3600
    out_string = do_string_sub(file_template,
                               init=init_time,
                               lead=lead_time)
    assert(out_string == "1987020103_A003h")


def test_ym_date_dir_init():
    # Test that the ym directory can be read in and does substitution correctly
    # e.g. /d1/METplus_TC/adeck_orig/201708/atcfunix.gfs.2017080100
    init_str = datetime.datetime.strptime("2017080100", '%Y%m%d%H')
    date_str = '201708'
    templ = '/d1/METplus_TC/adeck_orig/{date?fmt=%s}/' \
            'atcfunix.gfs.{init?fmt=%Y%m%d%H}.dat'
    filename = do_string_sub(templ, date=date_str, init=init_str)
    expected_filename = '/d1/METplus_TC/adeck_orig/201708/' \
                        'atcfunix.gfs.2017080100.dat'
    assert filename == expected_filename


def test_ym_date_dir():
    # Test that the ym directory can be read in and does substitution correctly
    # e.g. /d1/METplus_TC/adeck_orig/201708/atcfunix.gfs.2017080100
    date_str = '201708'
    templ = '/d1/METplus_TC/adeck_orig/{date?fmt=%s}/' \
            'atcfunix.gfs.2017080100.dat'
    filename = do_string_sub(templ, date=date_str)
    expected_filename = '/d1/METplus_TC/adeck_orig/201708/' \
                        'atcfunix.gfs.2017080100.dat'
    assert filename == expected_filename


def test_ymd_date_dir():
    # Test that the ymd directory can be read in and does substitution correctly
    # e.g. /d1/METplus_TC/adeck_orig/20170811/atcfunix.gfs.2017080100
    init_str = datetime.datetime.strptime('2017081118', '%Y%m%d%H')
    date_str = '20170811'
    templ = '/d1/METplus_TC/adeck_orig/{date?fmt=%s}/atcfunix.gfs.' \
            '{init?fmt=%Y%m%d%H}.dat'
    filename = do_string_sub(templ, date=date_str, init=init_str)
    expected_filename = '/d1/METplus_TC/adeck_orig/20170811/' \
                        'atcfunix.gfs.2017081118.dat'
    assert filename == expected_filename


def test_ymd_region_cyclone():
    # Test that we can recreate the full file path with a date,
    # region, and cyclone
    # /d1/METplus_TC/bdeck_orig/20170811/bal052017.dat
    date_str = '201708'
    region_str = 'al'
    cyclone_str = '05'
    year_str = '2017'
    # templ = '/d1/METplus_TC/bdeck/{date?fmt=%Y%m}/bal{region?fmt=%s}.dat'
    templ = '/d1/METplus_TC/bdeck/{date?fmt=%s}/b{region?fmt=%s}' \
            '{cyclone?fmt=%s}{misc?fmt=%s}.dat'
    full_file = do_string_sub(templ, date=date_str, region=region_str,
                              cyclone=cyclone_str, misc=year_str)
    expected_full_file = '/d1/METplus_TC/bdeck/201708/bal052017.dat'
    assert full_file == expected_full_file

def test_crow_variable_hour():
    # Test that do_string_sub() correctly creates the valid hour
    # without any zero-padding when given the following as input:
    # pgbf{lead?fmt=%H}.gfs.{valid?fmt=%Y%M%D%H}
    # pgbf([0-9]{1,3}).gfs.(2[0-9]{9})

    # crow input files with 3, 2, and 1-digit lead times:
    crow_input_file_3 = 'pgbf219.gfs.2017060418'
    crow_input_file_2 = 'pgbf18.gfs.2017062000'
    crow_input_file_1 = 'pgbf3.gfs.2017060418'
    lead_1 = int('3') * 3600
    lead_2 = int('18') * 3600
    lead_3 = int('219') * 3600
    valid_2 = datetime.datetime.strptime('2017062000', '%Y%m%d%H')
    valid_1 = valid_3 = datetime.datetime.strptime('2017060418', '%Y%m%d%H')
    templ = 'pgbf{lead?fmt=%1H}.gfs.{valid?fmt=%Y%m%d%H}'
    crow_1_output = do_string_sub(templ, valid=valid_1, lead=lead_1)
    crow_2_output = do_string_sub(templ, valid=valid_2, lead=lead_2)
    crow_3_output = do_string_sub(templ, valid=valid_3, lead=lead_3)
    # print("crow_1 output: ", crow_1_output)
    # print("crow_2 output: ", crow_2_output)
    # print("crow_3 output: ", crow_3_output)

    assert(crow_1_output == crow_input_file_1 and
           crow_2_output == crow_input_file_2 and
           crow_3_output == crow_input_file_3)




def test_multiple_valid_substitution_valid():
    valid_string = datetime.datetime.strptime("2018020112", '%Y%m%d%H')
    lead_string = int("123") * 3600
    templ = "{valid?fmt=%Y%m%d%H}/gfs.t{valid?fmt=%H}.pgrb2.0p25.{lead?fmt=%HHH}"
    expected_filename = "2018020112/gfs.t12.pgrb2.0p25.123"
    filename = do_string_sub(templ, valid=valid_string, lead=lead_string)
    assert(filename == expected_filename)

def test_multiple_valid_substitution_init():
    init_string = datetime.datetime.strptime("2017060400", '%Y%m%d%H')
    lead_string = 0
    templ = "{init?fmt=%Y%m%d%H}/gfs.t{init?fmt=%H}z.pgrb2.0p25.f{lead?fmt=%.2H}"
    expected_filename = "2017060400/gfs.t00z.pgrb2.0p25.f00"
    filename = do_string_sub(templ, init=init_string, lead=lead_string)
    assert(filename == expected_filename)


def test_multiple_valid_substitution_init_and_valid():
    init_string = datetime.datetime.strptime("2017060400", '%Y%m%d%H')
    valid_string = init_string
    lead_string = 0
    templ = "{valid?fmt=%Y%m%d%H}/gfs.t{init?fmt=%H}z.pgrb2.0p25.f{lead?fmt=%.2H}"
    expected_filename = "2017060400/gfs.t00z.pgrb2.0p25.f00"
    filename = do_string_sub(templ, init=init_string,
                             lead=lead_string, valid=valid_string)
    assert(filename == expected_filename)

def test_multiple_valid_substitution_init_and_valid_w_lead():
    init_string = datetime.datetime.strptime("2017060400", '%Y%m%d%H')
    valid_string = datetime.datetime.strptime("2017060500", '%Y%m%d%H')
    lead_string = int("24") * 3600
    templ = "{valid?fmt=%Y%m%d%H}/gfs.t{init?fmt=%H}z.pgrb2.0p25.f{lead?fmt=%.2H}"
    expected_filename = "2017060500/gfs.t00z.pgrb2.0p25.f24"
    filename = do_string_sub(templ, init=init_string,
                             lead=lead_string, valid=valid_string)
    assert(filename == expected_filename)

def test_multiple_valid_substitution_init_complex():
    init_string = datetime.datetime.strptime("2016061018", '%Y%m%d%H')
    lead_string = int("6") * 3600
    templ = "ncar.ral.CoSPA.HRRR.{init?fmt=%Y-%m-%dT%H:%M:%S}.PT{lead?fmt=%.2H}:00.nc"
    expected_filename = "ncar.ral.CoSPA.HRRR.2016-06-10T18:00:00.PT06:00.nc"
    filename = do_string_sub(templ, init=init_string, lead=lead_string)
    assert(filename == expected_filename)

# NOTE: this test has a shift in init time, which may not be supported
#  parse_template will currently error out if it finds a shift that is not
#  on valid time
def test_shift_time():
    init_string = datetime.datetime.strptime("2017060400", '%Y%m%d%H')
    templ = "{init?fmt=%Y%m%d%H?shift=86400}"
    expected_filename = "2017060500"
    filename = do_string_sub(templ, init=init_string)
    assert(filename == expected_filename)

# NOTE: this test has a shift in init time, which may not be supported
#  parse_template will currently error out if it finds a shift that is not
#  on valid time
def test_shift_time_negative():
    init_string = datetime.datetime.strptime("2017060400", '%Y%m%d%H')
    templ = "{init?fmt=%Y%m%d%H?shift=-86400}"
    expected_filename = "2017060300"
    filename = do_string_sub(templ, init=init_string)
    assert(filename == expected_filename)

# NOTE: this test has a shift in lead time, which may not be supported
#  parse_template will currently error out if it finds a shift that is not
#  on valid time
def test_shift_time_lead_negative():
    init_string = datetime.datetime.strptime("2019020700", '%Y%m%d%H')
    lead_string = int("60") * 3600
    templ = "dwd_{init?fmt=%Y%m%d%H}_{lead?fmt=%.3H?shift=-86400}_{lead?fmt=%.3H}"
    expected_filename = "dwd_2019020700_036_060"
    filename = do_string_sub(templ, init=init_string, lead=lead_string)
    assert(filename == expected_filename)

def test_shift_time_extract():
    valid_dt = datetime.datetime.strptime("2017060406", '%Y%m%d%H')
    templ = "{valid?fmt=%Y%m%d%H?shift=-21600}"
    filename = "2017060400"
    dt = parse_template(templ, filename)['valid']
    assert(dt.strftime('%Y%m%d%H') == valid_dt.strftime('%Y%m%d%H'))

def test_ccpa_template():
    passed = True
    valid_string = datetime.datetime.strptime("2019022403", '%Y%m%d%H')
    lead_string = 10800
    templ = "ccpa.{valid?fmt=%Y%m%d}/06/ccpa.t{valid?fmt=%H}z.{lead?fmt=%.2H}h.hrap.conus.gb2"
    expected_filename = "ccpa.20190224/06/ccpa.t03z.03h.hrap.conus.gb2"
    filename = do_string_sub(templ, valid=valid_string, lead=lead_string)
    if filename != expected_filename:
        passed = False

    valid_string = datetime.datetime.strptime("2019022406", '%Y%m%d%H')
    lead_string = int("6") * 3600
    expected_filename = "ccpa.20190224/06/ccpa.t06z.06h.hrap.conus.gb2"
    filename = do_string_sub(templ, valid=valid_string, lead=lead_string)
    if filename == expected_filename:
        passed = False

    return passed

def test_filename_matches_template():
    template = "{init?fmt=%Y%m%d%H}_dog_A{lead?fmt=%HH}h"
    filepath = "1987020103_dog_A03h"
    out = parse_template(template, filepath)
    ftime = out['valid'].strftime('%Y%m%d%H%M')
    assert(ftime == "198702010600")

def test_filename_does_not_match_template():
    template = "{init?fmt=%Y%m%d%H}_dog_A{lead?fmt=%HH}h"
    filepath = "1987020103_cat_A03h"
    out = parse_template(template, filepath)
    assert(out == None)

def test_filename_does_not_match_template_end():
    template = "{init?fmt=%Y%m%d%H}_dog_A{lead?fmt=%HH}h"
    filepath = "1987020103_dog_A03d"
    out = parse_template(template, filepath)
    assert(out == None)

def test_get_tags():
    template = '*{basin?fmt=%s}_some_stuff_{cyclone?fmt=%02d}_{date?fmt=%Y%m}'
    tags = get_tags(template)

    assert( tags[0] == '*' and tags[1] == 'basin' and tags[2] == 'cyclone' and tags[3] == 'date')

# format should be something like H 2H 3H 2M etc
# key is the time value integer to convert, like 1 or 60
# value is the formatted output string, like 01
# ttype is the unit to check, i.e. 'H', 'M', 'S', 'd', 's'
@pytest.mark.parametrize(
    'format, key, value, ttype', [
        ('H', 1, '01', 'H'),
        ('1H', 1, '1', 'H'),
        ('2H', 1, '01', 'H'),
        ('3H', 1, '001', 'H'),
        ('S', 1, '01', 'S'),
        ('1S', 1, '1', 'S'),
        ('2S', 1, '01', 'S'),
        ('3S', 1, '001', 'S'),
        ('M', 1, '01', 'M'),
        ('1M', 1, '1', 'M'),
        ('2M', 1, '01', 'M'),
        ('3M', 1, '001', 'M'),
        ('s', 1, '1', 's'),
        ('1s', 1, '1', 's'),
        ('2s', 1, '01', 's'),
        ('3s', 1, '001', 's'),
        ('d', 1, '01', 'd'),
        ('1d', 1, '1', 'd'),
        ('2d', 1, '01', 'd'),
        ('3d', 1, '001', 'd'),
        ('.1H', 1, '1', 'H'),
        ('.2H', 1, '01', 'H'),
        ('.3H', 1, '001', 'H'),
        ('.1S', 1, '1', 'S'),
        ('.2S', 1, '01', 'S'),
        ('.3S', 1, '001', 'S'),
        ('.1M', 1, '1', 'M'),
        ('.2M', 1, '01', 'M'),
        ('.3M', 1, '001', 'M'),
        ('.1s', 1, '1', 's'),
        ('.2s', 1, '01', 's'),
        ('.3s', 1, '001', 's'),
        ('.1d', 1, '1', 'd'),
        ('.2d', 1, '01', 'd'),
        ('.3d', 1, '001', 'd'),
    ]
)

def test_format_one_time_item(format, key ,value, ttype):
    assert(format_one_time_item(format, key, ttype) == value)

# format is the time format to use, like, %M or %H%M
# seconds is the integer number of seconds of the offset to use, i.e. 3601
# value is the formatted output string, like 010001
@pytest.mark.parametrize(
    'format, seconds, value', [
        ('%H', 1, '00'),
        ('%M', 1, '00'),
        ('%S', 1, '01'),
        ('%H', 3600, '01'),
        ('%M', 5400, '90'),
        ('%H%M', 5400, '0130'),
        ('%3H%M', 5400, '00130'),
        ('%H%3M', 5400, '01030'),
        ('%S', 5400, '5400'),
        ('%H%M%S', 5400, '013000'),
        ('%d%H', 90000, '0101'),
        ('%S', 86401, '86401'),
        ('%d%S', 86401, '0101'),
        ('%S', 86401, '86401'),
        ('%M%S', 86401, '144001'),
        ('%H%M%S', 90001, '250001'),
        ('%d%H%M%S', 90001, '01010001'),
        ('%d', 86401, '01'),
    ]
)
def test_format_hms(format, seconds, value):
    # format should be something like %M or %H%M
    assert(format_hms(format, seconds == value))

def test_underscore_in_time_fmt():
    valid_string = datetime.datetime.strptime("20170604010203", '%Y%m%d%H%M%S')
    templ = "{valid?fmt=%Y%m%d_%H%M%S}"
    expected_filename = "20170604_010203"
    filename = do_string_sub(templ, valid=valid_string)
    assert(filename == expected_filename)

@pytest.mark.parametrize(
    'match, match_dict, full_str, new_len, expected_result', [
        ('init+Y', {}, '2019.02.01.12.and.some.more.stuff', 4, True),
        ('init+Y', {'init+Y': '2019'}, '2019.02.01.12.and.some.more.stuff', 4, True),
        ('init+Y', {'init+Y': '2020'}, '2019.02.01.12.and.some.more.stuff', 4, False),
        ('init+Y', {}, '20blah19.02.01.12.and.some.more.stuff', 4, False),
        ('valid+H', {}, '02.01.12.and.some.more.stuff', 2, True),
        ('valid+H', {'valid+H': '2'}, '02.01.12.and.some.more.stuff', 2, True),
        ('valid+H', {'valid+H': '03'}, '02.01.12.and.some.more.stuff', 4, False),
        ('valid+H', {}, 'blah.01.12.and.some.more.stuff', 2, False),
        ('valid+H', {'init+Y': '2019', 'valid+H': '2'}, '02.01.12.and.some.more.stuff', 2, True),
    ]
)
def test_add_to_dict(match, match_dict, full_str, new_len, expected_result):
    assert(add_to_dict(match, match_dict, full_str, new_len) == expected_result)

@pytest.mark.parametrize(
    'template, filepath, expected_match_dict, expected_valid_shift', [
        # test valid time extraction
        ('file.{valid?fmt=%Y%m%d%H}.out',
         'file.2019020112.out',
         {'valid+Y': '2019',
          'valid+m': '02',
          'valid+d': '01',
          'valid+H': '12',},
          0),
        # test init and lead time extraction
        ('file.{init?fmt=%Y%m%d%H}.f{lead?fmt=%H}.out',
         'file.2019020112.f03.out',
         {'init+Y': '2019',
          'init+m': '02',
          'init+d': '01',
          'init+H': '12',
          'lead+H': '03'},
         0),
        # test init and lead time extraction with 3 digit lead
        ('file.{init?fmt=%Y%m%d%H}.f{lead?fmt=%3H}.out',
         'file.2019020112.f003.out',
         {'init+Y': '2019',
          'init+m': '02',
          'init+d': '01',
          'init+H': '12',
          'lead+H': '003'},
         0),
        # test shift is extracted from valid correctly
        ('file.{valid?fmt=%Y%m%d%H?shift=-30}.out',
         'file.2019020112.out',
         {'valid+Y': '2019',
          'valid+m': '02',
          'valid+d': '01',
          'valid+H': '12', },
         -30),
        # test TypeError occurs if shift applied to something other than valid
        ('file.{init?fmt=%Y%m%d%H?shift=-30}.f{lead?fmt=%H}.out',
         'file.2019020112.f03.out',
         None,
         None),
        # TODO: test TypeError if valid time has 2 different shift values
        ('file.{valid?fmt=%Y%m%d%H?shift=-30}.{valid?fmt=%Y?shift=60}.out',
         'file.2019020112.2019.out',
         None,
         None),
    ]
)
def test_populate_match_dict(template, filepath, expected_match_dict, expected_valid_shift):
    try:
        match_dict, valid_shift = populate_match_dict(template, filepath)

        # if expecting match_dict to be None, assert that actual is also None
        if expected_match_dict is None:
            assert(match_dict is None)
        elif match_dict is None:
            # if expected is not None, fail if actual is None
            assert(False)
            return

        num_keys = len(match_dict.keys())
        expected_num_keys = len(expected_match_dict.keys())
        if num_keys != expected_num_keys:
            print(f"Number of match_dict keys do not match. Actual: {num_keys}, Expected: {expected_num_keys}")
            print(f"Found: {match_dict}")
            print(f"Expected: {expected_match_dict}")
            assert(False)

        for key, value in match_dict.items():
            if key not in expected_match_dict:
                print(f"Key {key} not found in expected match_dict: {expected_match_dict}")
                assert(False)

            if value != expected_match_dict[key]:
                print(f"Match dict value from {key} does not match expected value")
                assert(False)

        if valid_shift != expected_valid_shift:
            print(f"Incorrect valid shift. Actual {valid_shift}, Expected: {expected_valid_shift}")
            assert(False)

        assert(True)

    except TypeError:
        assert(expected_match_dict is None and expected_valid_shift is None)
@pytest.mark.parametrize(
    'fmt, filepath, identifier, expected_fmt_len, expected_match_dict', [
        # test valid time extraction
        ('%Y%m%d',
         '20200201.more',
         'valid',
         8,
         {'valid+Y': '2020', 'valid+m': '02', 'valid+d': '01',},),
    ]
)
def test_get_fmt_info(fmt, filepath, identifier, expected_fmt_len, expected_match_dict):
    match_dict = {}
    fmt_len = get_fmt_info(fmt, filepath, match_dict, identifier)
    if fmt_len != expected_fmt_len:
        print(f"FMT length: {fmt_len}, match_dict: {match_dict}")
        assert(False)

    if match_dict != expected_match_dict:
        print(f"Match Dictionary: {match_dict}")
        print(f"Expected Dictionary: {expected_match_dict}")
        assert(False)

    assert(True)

def test_do_string_sub_skip_missing_tags():
    init_string = datetime.datetime.strptime("2017060400", '%Y%m%d%H')
    lead_string = int("6") * 3600
    templ = "{init?fmt=%Y%m%d%H}_{missing_tag?fmt=%H}_f{lead?fmt=%2H}"
    expected_filename = "2017060400_{missing_tag?fmt=%H}_f06"
    filename = do_string_sub(templ, init=init_string, lead=lead_string, skip_missing_tags=True)
    assert(filename == expected_filename)