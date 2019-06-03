#!/usr/bin/env python

from __future__ import print_function

import pytest
from string_template_substitution import StringSub
from string_template_substitution import StringExtract
import logging
import datetime

# def test_create_cyclone_regex():
#     # Test that the regex created from a template is what is expected
#     logger = logging.getLogger("test")
#     # templ = '/d1/METplus_TC/bdeck/{date?fmt=%s}/b{region?fmt=%s}' \
#     #         '{cyclone?fmt=%s}{misc?fmt=%s}.dat'
#     templ = '/d1/METplus_Data/cyclone_track_feature/atcf_track_data/b{region?fmt=%s}' \
#             '{cyclone?fmt=%s}{misc?fmt=%s}.dat'
#     date_str = '201708'
#     region_str = 'al'
#     cyclone_str = '05'
#     year_str = '2017'
#     ss = StringSub(logger, templ, date=date_str, region=region_str,
#                    cyclone=cyclone_str, misc=year_str)
#     actual_regex = ss.create_cyclone_regex()
#     # expected_regex = '/d1/METplus_TC/bdeck/([0-9]{4,10})/b([a-zA-Z]{2})([0-9]' \
#     #                  '{2,3})([a-zA-Z0-9-_.]+).dat'
#     expected_regex = '/d1/METplus_Data/cyclone_track_feature/atcf_track_data/b([a-zA-Z]{2})([0-9]' \
#                      '{2,3})([a-zA-Z0-9-_.]+).dat'
#     assert actual_regex == expected_regex


def test_crow_variable_hour():
    # Test that StringSub's doStringSub() correctly creates the valid hour
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
    templ = 'pgbf{lead?fmt=%H}.gfs.{valid?fmt=%Y%m%d%H}'
    ss_1 = StringSub(logger, templ, valid=valid_1, lead=lead_1)
    ss_2 = StringSub(logger, templ, valid=valid_2, lead=lead_2)
    ss_3 = StringSub(logger, templ, valid=valid_3, lead=lead_3)
    crow_1_output = ss_1.doStringSub()
    crow_2_output = ss_2.doStringSub()
    crow_3_output = ss_3.doStringSub()
    print("crow_1 output: ", crow_1_output)
    print("crow_2 output: ", crow_2_output)
    print("crow_3 output: ", crow_3_output)
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
    filename = ss.doStringSub()
    assert(filename == expected_filename)

def test_multiple_valid_substitution_init():
    init_string = datetime.datetime.strptime("2017060400", '%Y%m%d%H')
    lead_string = 0
    logger = logging.getLogger("testing")
    templ = "{init?fmt=%Y%m%d%H}/gfs.t{init?fmt=%H}z.pgrb2.0p25.f{lead?fmt=%.2H}"
    expected_filename = "2017060400/gfs.t00z.pgrb2.0p25.f00"
    ss = StringSub(logger, templ, init=init_string, lead=lead_string)
    filename = ss.doStringSub()
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
    filename = ss.doStringSub()
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
    filename = ss.doStringSub()
    assert(filename == expected_filename)

def test_multiple_valid_substitution_init_complex():
    init_string = datetime.datetime.strptime("2016061018", '%Y%m%d%H')
    lead_string = int("6") * 3600
    logger = logging.getLogger("testing")
    templ = "ncar.ral.CoSPA.HRRR.{init?fmt=%Y-%m-%dT%H:%M:%S}.PT{lead?fmt=%.2H}:00.nc"
    expected_filename = "ncar.ral.CoSPA.HRRR.2016-06-10T18:00:00.PT06:00.nc"
    ss = StringSub(logger, templ, init=init_string, lead=lead_string)
    filename = ss.doStringSub()
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
    filename = ss.doStringSub()
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
    filename = ss.doStringSub()
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
    filename = ss.doStringSub()
    assert(filename == expected_filename)

def test_shift_time_extract():
    valid_dt = datetime.datetime.strptime("2017060406", '%Y%m%d%H')
    logger = logging.getLogger("testing")
    templ = "{valid?fmt=%Y%m%d%H?shift=-21600}"
    filename = "2017060400"
    se = StringExtract(logger, templ, filename)
    dt = se.parseTemplate()['valid']
    assert(dt.strftime('%Y%m%d%H') == valid_dt.strftime('%Y%m%d%H'))

def test_ccpa_template():
    passed = True
    valid_string = datetime.datetime.strptime("2019022403", '%Y%m%d%H')
    lead_string = 10800
    logger = logging.getLogger("testing")
    templ = "ccpa.{valid?fmt=%Y%m%d}/06/ccpa.t{valid?fmt=%H}z.{lead?fmt=%.2H}h.hrap.conus.gb2"
    expected_filename = "ccpa.20190224/06/ccpa.t03z.03h.hrap.conus.gb2"
    ss = StringSub(logger, templ, valid=valid_string, lead=lead_string)
    filename = ss.doStringSub()
    if filename != expected_filename:
        passed = False

    valid_string = datetime.datetime.strptime("2019022406", '%Y%m%d%H')
    lead_string = int("6") * 3600
    expected_filename = "ccpa.20190224/06/ccpa.t06z.06h.hrap.conus.gb2"
    ss = StringSub(logger, templ, valid=valid_string, lead=lead_string)
    filename = ss.doStringSub()
    if filename == expected_filename:
        passed = False

    return passed

def test_filename_matches_template():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_dog_A{lead?fmt=%HH}h"
    filepath = "1987020103_dog_A03h"
    se = StringExtract(logger, template, filepath)
    out = se.parseTemplate()
    ftime = out['valid'].strftime('%Y%m%d%H%M')
    assert(ftime == "198702010600")

def test_filename_does_not_match_template():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_dog_A{lead?fmt=%HH}h"
    filepath = "1987020103_cat_A03h"
    se = StringExtract(logger, template, filepath)
    out = se.parseTemplate()
    assert(out == None)

def test_filename_does_not_match_template_end():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_dog_A{lead?fmt=%HH}h"
    filepath = "1987020103_dog_A03d"
    se = StringExtract(logger, template, filepath)
    out = se.parseTemplate()
    assert(out == None)
