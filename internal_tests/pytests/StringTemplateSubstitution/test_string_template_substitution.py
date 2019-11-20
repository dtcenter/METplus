#!/usr/bin/env python

import pytest
from string_template_substitution import StringSub
from string_template_substitution import StringExtract
from string_template_substitution import get_tags
from string_template_substitution import format_one_time_item
from string_template_substitution import format_hms
import logging
import datetime

def test_cycle_hour():
    cycle_string = 0
    valid_string = datetime.datetime.strptime("20180103", '%Y%m%d')
    logger = logging.getLogger("dummy")
    templ = "prefix.{valid?fmt=%Y%m%d}.tm{cycle?fmt=%2H}"
    expected_filename = "prefix.20180103.tm00"
    ss = StringSub(logger, templ, valid=valid_string, cycle=cycle_string)
    filename = ss.do_string_sub()
    assert(filename == expected_filename)


def test_offset_hour():
    logger = logging.getLogger("dummy")
    expected_hour = "03"
    offset = 10800
    templ = "{offset?fmt=%2H}"
    ss = StringSub(logger, templ, offset=offset)
    offset_hour = ss.do_string_sub()
    assert (offset_hour == expected_hour)


@pytest.mark.parametrize(
    'key, value', [
        ('00', '20180103060000'),
        ('03', '20180103030000'),
        ('06', '20180103000000'),
        ('72', '20171231060000')
    ]
)

def test_calc_valid_for_prepbufr(key, value):
    pytest.skip('deprecated function')
    # Verify that the previous day is correctly calculated when
    # the negative_offset_hour > cycle_hour
    cycle_hour = "00"
    init_string = "2018010306"
    logger = logging.getLogger("dummy")
    templ = "prefix.{valid?fmt=%Y%m%d%H}.tm{cycle?fmt=%H}z.tm{" \
        "offset?fmt=%H}.nc"

    ss = StringSub(logger, templ, init=init_string, cycle=cycle_hour,
               offset=key)
    valid_time = ss.calc_valid_for_prepbufr()
    assert (valid_time == value)


def test_gdas_substitution():
    # Test that the string template substitution works correctly for GDAS
    # prepbufr files, which do not make use of the cycle hour or the offset
    # to generate the valid time.
    valid_string = "2018010411"
    valid_obj = datetime.datetime.strptime(valid_string, '%Y%m%d%H')
    logger = logging.getLogger("testing")
    templ = "prepbufr.gdas.{valid?fmt=%Y%m%d%H}.nc"
    expected_filename = 'prepbufr.gdas.' + valid_string + '.nc'
    ss = StringSub(logger, templ, valid=valid_obj)
    filename = ss.do_string_sub()
    assert(filename == expected_filename)

@pytest.mark.parametrize(
    'key, value', [
        (136800, 'prepbufr.nam.2018010311.t38z.tm03.nc'),
        (1368000, 'prepbufr.nam.2018011717.t380z.tm03.nc')
#        ('38', 'prepbufr.nam.2018010311.t38z.tm03.nc'),
#        ('380', 'prepbufr.nam.2018011717.t380z.tm03.nc')

    ]
)
def test_nam_substitution_HH(key, value):
    pytest.skip('time offsets no longer computed in StringSub')
    # Test that the substitution works correctly when given an init time,
    # cycle hour, and negative offset hour.
    init_string = datetime.datetime.strptime("20180102", '%Y%m%d')
    cycle_string = key
    offset_string = 10800 #'03'
    expected_filename = value
    logger = logging.getLogger("test")
    templ = \
        'prepbufr.nam.{valid?fmt=%Y%m%d%H}.t{cycle?fmt=%HH}z.tm{' \
        'offset?fmt=%HH}.nc'
    ss = StringSub(logger, templ, init=init_string, cycle=cycle_string,
                   offset=offset_string)
    filename = ss.do_string_sub()
    # print('nam filename: ', filename)
    assert (filename == expected_filename)


@pytest.mark.parametrize(
    'key, value', [
        (64800, 'prepbufr.nam.2018010215.t018z.tm03.nc'),
        (10800, 'prepbufr.nam.2018010200.t003z.tm03.nc'),
#        ('18', 'prepbufr.nam.2018010215.t018z.tm03.nc'),
#        ('03', 'prepbufr.nam.2018010200.t003z.tm03.nc'),

    ]
)
def test_nam_substitution_HHH(key, value):
    pytest.skip('time offsets no longer computed in StringSub')
    # Test that the substitution works correctly when given an init time,
    # cycle hour, and negative offset hour.
    init_string = datetime.datetime.strptime("20180102", '%Y%m%d')
    cycle_string = key
    offset_string = int('03') * 3600
    expected_filename = value
    logger = logging.getLogger("test")
    templ = \
        'prepbufr.nam.{valid?fmt=%Y%m%d%H}.t{cycle?fmt=%HHH}z.tm{' \
        'offset?fmt=%HH}.nc'
    ss = StringSub(logger, templ, init=init_string, cycle=cycle_string,
                   offset=offset_string)
    filename = ss.do_string_sub()
    # print('nam filename: ', filename)
    assert (filename == expected_filename)


@pytest.mark.parametrize(
    'key, value', [
        ('38', 'prepbufr.nam.2018010311.t01_13_59_59z.tm03.nc'),
        ('380', 'prepbufr.nam.2018011717.t15_20_00_00z.tm03.nc')
    ]
)
def test_nam_substitution_dHMS(key, value):
        pytest.skip('time offsets no longer computed in StringSub')
        # Test that the substitution works correctly when given an init time,
        # cycle hour, and negative offset hour.
        init_string = datetime.datetime.strptime("20180102", '%Y%m%d')
        cycle_string = int(key) * 3600
        offset_string = int('03') * 3600
        expected_filename = value
        logger = logging.getLogger("test")
        templ = \
            'prepbufr.nam.{valid?fmt=%Y%m%d%H}.t{cycle?fmt=%dd%HH%M%S}z.tm{' \
            'offset?fmt=%HH}.nc'
        ss = StringSub(logger, templ, init=init_string, cycle=cycle_string,
                       offset=offset_string)
        filename = ss.do_string_sub()
        # print('nam filename: ', filename)
        assert (filename == expected_filename)


def test_hh_lead():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%HH}h"
    filepath = "1987020103_A03h"
    se = StringExtract(logger, template,
                           filepath)
    out = se.parse_template()
    ftime = out['valid'].strftime('%Y%m%d%H%M')
    assert(ftime == "198702010600")


def test_hhh_lead():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%HHH}h"
    filepath = "1987020103_A003h"
    se = StringExtract(logger, template,
                           filepath)
    out = se.parse_template()
    ftime = out['valid'].strftime('%Y%m%d%H%M')
    assert(ftime == "198702010600")


def test_2h_lead():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%.2H}h"
    filepath = "1987020103_A03h"
    se = StringExtract(logger, template,
                           filepath)
    out = se.parse_template()
    ftime = out['valid'].strftime('%Y%m%d%H%M')
    assert(ftime == "198702010600")


def test_3h_lead():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%.3H}h"
    filepath = "1987020103_A003h"
    se = StringExtract(logger, template,
                           filepath)
    out = se.parse_template()
    ftime = out['valid'].strftime('%Y%m%d%H%M')
    assert(ftime == "198702010600")


def test_h_lead_no_pad_1_digit():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%1H}h"
    filepath = "1987020103_A3h"
    se = StringExtract(logger, template,
                           filepath)
    out = se.parse_template()
    ftime = out['valid'].strftime('%Y%m%d%H%M')
    assert(ftime == "198702010600")


def test_h_lead_no_pad_2_digit():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%H}h"
    filepath = "1987020103_A12h"
    se = StringExtract(logger, template,
                           filepath)
    out = se.parse_template()
    ftime = out['valid'].strftime('%Y%m%d%H%M')
    assert(ftime == "198702011500")


def test_h_lead_no_pad_3_digit():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%H}h"
    filepath = "1987020103_A102h"
    se = StringExtract(logger, template,
                           filepath)
    out = se.parse_template()
    ftime = out['valid'].strftime('%Y%m%d%H%M')
    assert(ftime == "198702050900")


def test_h_lead_no_pad_1_digit_sub():
    logger = logging.getLogger("test")
    file_template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%1H}h"
    init_time = datetime.datetime.strptime("1987020103", '%Y%m%d%H')
    lead_time = int("3") * 3600
    fSts = StringSub(logger,
                     file_template,
                     init=init_time,
                     lead=lead_time)
    out_string = fSts.do_string_sub()
    assert(out_string == "1987020103_A3h")


def test_h_lead_no_pad_2_digit_sub():
    logger = logging.getLogger("test")
    file_template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%1H}h"
    init_time = datetime.datetime.strptime("1987020103", '%Y%m%d%H')
    lead_time = int("12") * 3600
    fSts = StringSub(logger,
                     file_template,
                     init=init_time,
                     lead=lead_time)
    out_string = fSts.do_string_sub()
    assert(out_string == "1987020103_A12h")


def test_h_lead_no_pad_3_digit_sub():
    logger = logging.getLogger("test")
    file_template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%1H}h"
    init_time = datetime.datetime.strptime("1987020103", '%Y%m%d%H')
    lead_time = int("102") * 3600
    fSts = StringSub(logger,
                     file_template,
                     init=init_time,
                     lead=lead_time)
    out_string = fSts.do_string_sub()
    assert(out_string == "1987020103_A102h")


def test_h_lead_pad_1_digit_sub():
    logger = logging.getLogger("test")
    file_template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%.1H}h"
    init_time = datetime.datetime.strptime("1987020103", '%Y%m%d%H')
    lead_time = int("3") * 3600
    fSts = StringSub(logger,
                     file_template,
                     init=init_time,
                     lead=lead_time)
    out_string = fSts.do_string_sub()
    assert(out_string == "1987020103_A3h")


def test_h_lead_pad_2_digit_sub():
    logger = logging.getLogger("test")
    file_template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%.2H}h"
    init_time = datetime.datetime.strptime("1987020103", '%Y%m%d%H')
    lead_time = int("3") * 3600
    fSts = StringSub(logger,
                     file_template,
                     init=init_time,
                     lead=lead_time)
    out_string = fSts.do_string_sub()
    assert(out_string == "1987020103_A03h")


def test_h_lead_pad_2_digit_sub():
    logger = logging.getLogger("test")
    file_template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%.3H}h"
    init_time = datetime.datetime.strptime("1987020103", '%Y%m%d%H')
    lead_time = int("3") * 3600
    fSts = StringSub(logger,
                     file_template,
                     init=init_time,
                     lead=lead_time)
    out_string = fSts.do_string_sub()
    assert(out_string == "1987020103_A003h")


def test_ym_date_dir_init():
    # Test that the ym directory can be read in and does substitution correctly
    logger = logging.getLogger("test")
    # e.g. /d1/METplus_TC/adeck_orig/201708/atcfunix.gfs.2017080100
    init_str = datetime.datetime.strptime("2017080100", '%Y%m%d%H')
    date_str = '201708'
    templ = '/d1/METplus_TC/adeck_orig/{date?fmt=%s}/' \
            'atcfunix.gfs.{init?fmt=%Y%m%d%H}.dat'
    ss = StringSub(logger, templ, date=date_str, init=init_str)
    filename = ss.do_string_sub()
    expected_filename = '/d1/METplus_TC/adeck_orig/201708/' \
                        'atcfunix.gfs.2017080100.dat'
    assert filename == expected_filename


def test_ym_date_dir():
    # Test that the ym directory can be read in and does substitution correctly
    logger = logging.getLogger("test")
    # e.g. /d1/METplus_TC/adeck_orig/201708/atcfunix.gfs.2017080100
    date_str = '201708'
    templ = '/d1/METplus_TC/adeck_orig/{date?fmt=%s}/' \
            'atcfunix.gfs.2017080100.dat'
    ss = StringSub(logger, templ, date=date_str)
    filename = ss.do_string_sub()
    expected_filename = '/d1/METplus_TC/adeck_orig/201708/' \
                        'atcfunix.gfs.2017080100.dat'
    assert filename == expected_filename


def test_ymd_date_dir():
    # Test that the ymd directory can be read in and does substitution correctly
    logger = logging.getLogger("test")
    # e.g. /d1/METplus_TC/adeck_orig/20170811/atcfunix.gfs.2017080100
    init_str = datetime.datetime.strptime('2017081118', '%Y%m%d%H')
    date_str = '20170811'
    templ = '/d1/METplus_TC/adeck_orig/{date?fmt=%s}/atcfunix.gfs.' \
            '{init?fmt=%Y%m%d%H}.dat'
    ss = StringSub(logger, templ, date=date_str, init=init_str)
    filename = ss.do_string_sub()
    expected_filename = '/d1/METplus_TC/adeck_orig/20170811/' \
                        'atcfunix.gfs.2017081118.dat'
    assert filename == expected_filename


def test_ymd_region_cyclone():
    # Test that we can recreate the full file path with a date,
    # region, and cyclone
    logger = logging.getLogger("test")
    # /d1/METplus_TC/bdeck_orig/20170811/bal052017.dat
    date_str = '201708'
    region_str = 'al'
    cyclone_str = '05'
    year_str = '2017'
    # templ = '/d1/METplus_TC/bdeck/{date?fmt=%Y%m}/bal{region?fmt=%s}.dat'
    templ = '/d1/METplus_TC/bdeck/{date?fmt=%s}/b{region?fmt=%s}' \
            '{cyclone?fmt=%s}{misc?fmt=%s}.dat'
    ss = StringSub(logger, templ, date=date_str, region=region_str,
                   cyclone=cyclone_str, misc=year_str)
    full_file = ss.do_string_sub()
    expected_full_file = '/d1/METplus_TC/bdeck/201708/bal052017.dat'
    assert full_file == expected_full_file


def test_create_cyclone_regex():
    pytest.skip('deprecated function')
    # Test that the regex created from a template is what is expected
    logger = logging.getLogger("test")
    templ = '/d1/METplus_TC/bdeck/{date?fmt=%s}/b{region?fmt=%s}' \
            '{cyclone?fmt=%s}{misc?fmt=%s}.dat'
    date_str = '201708'
    region_str = 'al'
    cyclone_str = '05'
    year_str = '2017'
    ss = StringSub(logger, templ, date=date_str, region=region_str,
                   cyclone=cyclone_str, misc=year_str)
    actual_regex = ss.create_cyclone_regex()
    expected_regex = '/d1/METplus_TC/bdeck/([0-9]{4,10})/b([a-zA-Z]{2})([0-9]' \
                     '{2,3})([a-zA-Z0-9-_.]+).dat'
    assert actual_regex == expected_regex

def test_crow_variable_hour():
    # Test that StringSub's do_string_sub() correctly creates the valid hour
    # without any zero-padding when given the following as input:
    # pgbf{lead?fmt=%H}.gfs.{valid?fmt=%Y%M%D%H}
    # pgbf([0-9]{1,3}).gfs.(2[0-9]{9})
    logger = logging.getLogger("crow_data")

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
    ss_1 = StringSub(logger, templ, valid=valid_1, lead=lead_1)
    ss_2 = StringSub(logger, templ, valid=valid_2, lead=lead_2)
    ss_3 = StringSub(logger, templ, valid=valid_3, lead=lead_3)
    crow_1_output = ss_1.do_string_sub()
    crow_2_output = ss_2.do_string_sub()
    crow_3_output = ss_3.do_string_sub()
    # print("crow_1 output: ", crow_1_output)
    # print("crow_2 output: ", crow_2_output)
    # print("crow_3 output: ", crow_3_output)

    assert(crow_1_output == crow_input_file_1 and
           crow_2_output == crow_input_file_2 and
           crow_3_output == crow_input_file_3)




def test_multiple_valid_substitution_valid():
    valid_string = datetime.datetime.strptime("2018020112", '%Y%m%d%H')
    lead_string = int("123") * 3600
    logger = logging.getLogger("testing")
    templ = "{valid?fmt=%Y%m%d%H}/gfs.t{valid?fmt=%H}.pgrb2.0p25.{lead?fmt=%HHH}"
    expected_filename = "2018020112/gfs.t12.pgrb2.0p25.123"
    ss = StringSub(logger, templ, valid=valid_string, lead=lead_string)
    filename = ss.do_string_sub()
    assert(filename == expected_filename)

def test_multiple_valid_substitution_init():
    init_string = datetime.datetime.strptime("2017060400", '%Y%m%d%H')
    lead_string = 0
    logger = logging.getLogger("testing")
    templ = "{init?fmt=%Y%m%d%H}/gfs.t{init?fmt=%H}z.pgrb2.0p25.f{lead?fmt=%.2H}"
    expected_filename = "2017060400/gfs.t00z.pgrb2.0p25.f00"
    ss = StringSub(logger, templ, init=init_string, lead=lead_string)
    filename = ss.do_string_sub()
    assert(filename == expected_filename)


def test_multiple_valid_substitution_init_and_valid():
    init_string = datetime.datetime.strptime("2017060400", '%Y%m%d%H')
    valid_string = init_string
    lead_string = 0
    logger = logging.getLogger("testing")
    templ = "{valid?fmt=%Y%m%d%H}/gfs.t{init?fmt=%H}z.pgrb2.0p25.f{lead?fmt=%.2H}"
    expected_filename = "2017060400/gfs.t00z.pgrb2.0p25.f00"
    ss = StringSub(logger, templ, init=init_string,
                   lead=lead_string, valid=valid_string)
    filename = ss.do_string_sub()
    assert(filename == expected_filename)

def test_multiple_valid_substitution_init_and_valid_w_lead():
    init_string = datetime.datetime.strptime("2017060400", '%Y%m%d%H')
    valid_string = datetime.datetime.strptime("2017060500", '%Y%m%d%H')
    lead_string = int("24") * 3600
    logger = logging.getLogger("testing")
    templ = "{valid?fmt=%Y%m%d%H}/gfs.t{init?fmt=%H}z.pgrb2.0p25.f{lead?fmt=%.2H}"
    expected_filename = "2017060500/gfs.t00z.pgrb2.0p25.f24"
    ss = StringSub(logger, templ, init=init_string,
                   lead=lead_string, valid=valid_string)
    filename = ss.do_string_sub()
    assert(filename == expected_filename)

def test_multiple_valid_substitution_init_complex():
    init_string = datetime.datetime.strptime("2016061018", '%Y%m%d%H')
    lead_string = int("6") * 3600
    logger = logging.getLogger("testing")
    templ = "ncar.ral.CoSPA.HRRR.{init?fmt=%Y-%m-%dT%H:%M:%S}.PT{lead?fmt=%.2H}:00.nc"
    expected_filename = "ncar.ral.CoSPA.HRRR.2016-06-10T18:00:00.PT06:00.nc"
    ss = StringSub(logger, templ, init=init_string, lead=lead_string)
    filename = ss.do_string_sub()
    assert(filename == expected_filename)

# NOTE: this test has a shift in init time, which may not be supported
#  StringExtract will currently error out if it finds a shift that is not
#  on valid time
def test_shift_time():
    init_string = datetime.datetime.strptime("2017060400", '%Y%m%d%H')
    logger = logging.getLogger("testing")
    templ = "{init?fmt=%Y%m%d%H?shift=86400}"
    expected_filename = "2017060500"
    ss = StringSub(logger, templ, init=init_string)
    filename = ss.do_string_sub()
    assert(filename == expected_filename)

# NOTE: this test has a shift in init time, which may not be supported
#  StringExtract will currently error out if it finds a shift that is not
#  on valid time
def test_shift_time_negative():
    init_string = datetime.datetime.strptime("2017060400", '%Y%m%d%H')
    logger = logging.getLogger("testing")
    templ = "{init?fmt=%Y%m%d%H?shift=-86400}"
    expected_filename = "2017060300"
    ss = StringSub(logger, templ, init=init_string)
    filename = ss.do_string_sub()
    assert(filename == expected_filename)

# NOTE: this test has a shift in lead time, which may not be supported
#  StringExtract will currently error out if it finds a shift that is not
#  on valid time
def test_shift_time_lead_negative():
    init_string = datetime.datetime.strptime("2019020700", '%Y%m%d%H')
    lead_string = int("60") * 3600
    logger = logging.getLogger("testing")
    templ = "dwd_{init?fmt=%Y%m%d%H}_{lead?fmt=%.3H?shift=-86400}_{lead?fmt=%.3H}"
    expected_filename = "dwd_2019020700_036_060"
    ss = StringSub(logger, templ, init=init_string, lead=lead_string)
    filename = ss.do_string_sub()
    assert(filename == expected_filename)

def test_shift_time_extract():
    valid_dt = datetime.datetime.strptime("2017060406", '%Y%m%d%H')
    logger = logging.getLogger("testing")
    templ = "{valid?fmt=%Y%m%d%H?shift=-21600}"
    filename = "2017060400"
    se = StringExtract(logger, templ, filename)
    dt = se.parse_template()['valid']
    assert(dt.strftime('%Y%m%d%H') == valid_dt.strftime('%Y%m%d%H'))

def test_ccpa_template():
    passed = True
    valid_string = datetime.datetime.strptime("2019022403", '%Y%m%d%H')
    lead_string = 10800
    logger = logging.getLogger("testing")
    templ = "ccpa.{valid?fmt=%Y%m%d}/06/ccpa.t{valid?fmt=%H}z.{lead?fmt=%.2H}h.hrap.conus.gb2"
    expected_filename = "ccpa.20190224/06/ccpa.t03z.03h.hrap.conus.gb2"
    ss = StringSub(logger, templ, valid=valid_string, lead=lead_string)
    filename = ss.do_string_sub()
    if filename != expected_filename:
        passed = False

    valid_string = datetime.datetime.strptime("2019022406", '%Y%m%d%H')
    lead_string = int("6") * 3600
    expected_filename = "ccpa.20190224/06/ccpa.t06z.06h.hrap.conus.gb2"
    ss = StringSub(logger, templ, valid=valid_string, lead=lead_string)
    filename = ss.do_string_sub()
    if filename == expected_filename:
        passed = False

    return passed

def test_filename_matches_template():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_dog_A{lead?fmt=%HH}h"
    filepath = "1987020103_dog_A03h"
    se = StringExtract(logger, template, filepath)
    out = se.parse_template()
    ftime = out['valid'].strftime('%Y%m%d%H%M')
    assert(ftime == "198702010600")

def test_filename_does_not_match_template():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_dog_A{lead?fmt=%HH}h"
    filepath = "1987020103_cat_A03h"
    se = StringExtract(logger, template, filepath)
    out = se.parse_template()
    assert(out == None)

def test_filename_does_not_match_template_end():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_dog_A{lead?fmt=%HH}h"
    filepath = "1987020103_dog_A03d"
    se = StringExtract(logger, template, filepath)
    out = se.parse_template()
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
