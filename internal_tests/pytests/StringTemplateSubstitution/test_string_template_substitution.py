#!/usr/bin/env python

from __future__ import print_function

import pytest
from string_template_substitution import StringSub
from string_template_substitution import StringExtract
import logging


def test_cycle_hour():
    cycle_string = "00"
    valid_string = "20180103"
    logger = logging.getLogger("dummy")
    templ = "prefix.{valid?fmt=%Y%m%d}.tm{cycle?fmt=%H}"
    ss = StringSub(logger, templ, valid=valid_string, cycle=cycle_string)
    expected_hours = int(0)
    assert (ss.cycle_time_hours == expected_hours)


def test_offset_hour():
    logger = logging.getLogger("dummy")
    expected_hour = int(3)
    offset = "03"
    templ = "prefix.{valid?fmt=%Y%m%d}.tm{offset?fmt=%H}"
    ss = StringSub(logger, templ, offset=offset)
    assert (ss.offset_hour == expected_hour)


@pytest.mark.parametrize(
    'key, value', [
        ('00', '20180103060000'),
        ('03', '20180103030000'),
        ('06', '20180103000000'),
        ('72', '20171231060000')
    ]
)
def test_calc_valid_for_prepbufr(key, value):
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
    logger = logging.getLogger("testing")
    templ = "prepbufr.gdas.{valid?fmt=%Y%m%d%H}.nc"
    expected_filename = 'prepbufr.gdas.' + valid_string + '.nc'
    ss = StringSub(logger, templ, valid=valid_string)
    filename = ss.doStringSub()
    print("expected filename ", expected_filename, " gdas filename: ",
      filename)
    assert(filename == expected_filename)

@pytest.mark.parametrize(
    'key, value', [
        ('38', 'prepbufr.nam.2018010311.t38z.tm03.nc'),
        ('380', 'prepbufr.nam.2018011717.t380z.tm03.nc')

    ]
)
def test_nam_substitution_HH(key, value):
    # Test that the substitution works correctly when given an init time,
    # cycle hour, and negative offset hour.
    init_string = "20180102"
    cycle_string = key
    offset_string = '03'
    expected_filename = value
    logger = logging.getLogger("test")
    templ = \
        'prepbufr.nam.{valid?fmt=%Y%m%d%H}.t{cycle?fmt=%HH}z.tm{' \
        'offset?fmt=%HH}.nc'
    ss = StringSub(logger, templ, init=init_string, cycle=cycle_string,
                   offset=offset_string)
    filename = ss.doStringSub()
    print('nam filename: ', filename)
    assert (filename == expected_filename)


@pytest.mark.parametrize(
    'key, value', [
        ('18', 'prepbufr.nam.2018010215.t018z.tm03.nc'),
        ('03', 'prepbufr.nam.2018010200.t003z.tm03.nc'),

    ]
)
def test_nam_substitution_HHH(key, value):
    # Test that the substitution works correctly when given an init time,
    # cycle hour, and negative offset hour.
    init_string = "20180102"
    cycle_string = key
    offset_string = '03'
    expected_filename = value
    logger = logging.getLogger("test")
    templ = \
        'prepbufr.nam.{valid?fmt=%Y%m%d%H}.t{cycle?fmt=%HHH}z.tm{' \
        'offset?fmt=%HH}.nc'
    ss = StringSub(logger, templ, init=init_string, cycle=cycle_string,
                   offset=offset_string)
    filename = ss.doStringSub()
    print('nam filename: ', filename)
    assert (filename == expected_filename)


@pytest.mark.parametrize(
    'key, value', [
        ('38', 'prepbufr.nam.2018010311.t01_13_59_59z.tm03.nc'),
        ('380', 'prepbufr.nam.2018011717.t15_20_00_00z.tm03.nc')
    ]
)
def test_nam_substitution_dHMS(key, value):
        # Test that the substitution works correctly when given an init time,
        # cycle hour, and negative offset hour.
        init_string = "20180102"
        cycle_string = key
        offset_string = '03'
        expected_filename = value
        logger = logging.getLogger("test")
        templ = \
            'prepbufr.nam.{valid?fmt=%Y%m%d%H}.t{cycle?fmt=%dd%HH%M%S}z.tm{' \
            'offset?fmt=%HH}.nc'
        ss = StringSub(logger, templ, init=init_string, cycle=cycle_string,
                       offset=offset_string)
        filename = ss.doStringSub()
        print('nam filename: ', filename)
        assert (filename == expected_filename)


def test_hh_lead():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%HH}h"
    filepath = "1987020103_A03h"
    se = StringExtract(logger, template,
                           filepath)
    se.parseTemplate()
    ftime = se.getValidTime("%Y%m%d%H%M")
    assert(ftime == "198702010600")


def test_hhh_lead():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%HHH}h"
    filepath = "1987020103_A003h"
    se = StringExtract(logger, template,
                           filepath)
    se.parseTemplate()
    ftime = se.getValidTime("%Y%m%d%H%M")
    assert(ftime == "198702010600")


def test_2h_lead():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%.2H}h"
    filepath = "1987020103_A03h"
    se = StringExtract(logger, template,
                           filepath)
    se.parseTemplate()
    ftime = se.getValidTime("%Y%m%d%H%M")
    assert(ftime == "198702010600")


def test_3h_lead():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%.3H}h"
    filepath = "1987020103_A003h"
    se = StringExtract(logger, template,
                           filepath)
    se.parseTemplate()
    ftime = se.getValidTime("%Y%m%d%H%M")
    assert(ftime == "198702010600")

'''
def test_h_lead_no_pad_1_digit():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%H}h"
    filepath = "1987020103_A3h"
    se = StringExtract(logger, template,
                           filepath)
    se.parseTemplate()
    ftime = se.getValidTime("%Y%m%d%H%M")
    assert(ftime == "198702010600")


def test_h_lead_no_pad_2_digit():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%H}h"
    filepath = "1987020103_A12h"
    se = StringExtract(logger, template,
                           filepath)
    se.parseTemplate()
    ftime = se.getValidTime("%Y%m%d%H%M")
    assert(ftime == "198702011500")


def test_h_lead_no_pad_3_digit():
    logger = logging.getLogger("test")
    template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%H}h"
    filepath = "1987020103_A102h"
    se = StringExtract(logger, template,
                           filepath)
    se.parseTemplate()
    ftime = se.getValidTime("%Y%m%d%H%M")
    assert(ftime == "198702050900")
'''

def test_h_lead_no_pad_1_digit_sub():
    logger = logging.getLogger("test")
    file_template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%H}h"
    init_time = "1987020103"
    lead_time = "3"
    fSts = StringSub(logger,
                     file_template,
                     init=init_time,
                     lead=lead_time)
    out_string = fSts.doStringSub()
    assert(out_string == "1987020103_A3h")


def test_h_lead_no_pad_2_digit_sub():
    logger = logging.getLogger("test")
    file_template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%H}h"
    init_time = "1987020103"
    lead_time = "12"
    fSts = StringSub(logger,
                     file_template,
                     init=init_time,
                     lead=lead_time)
    out_string = fSts.doStringSub()
    assert(out_string == "1987020103_A12h")


def test_h_lead_no_pad_3_digit_sub():
    logger = logging.getLogger("test")
    file_template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%H}h"
    init_time = "1987020103"
    lead_time = "102"
    fSts = StringSub(logger,
                     file_template,
                     init=init_time,
                     lead=lead_time)
    out_string = fSts.doStringSub()
    assert(out_string == "1987020103_A102h")


def test_h_lead_pad_1_digit_sub():
    logger = logging.getLogger("test")
    file_template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%.1H}h"
    init_time = "1987020103"
    lead_time = "3"
    fSts = StringSub(logger,
                     file_template,
                     init=init_time,
                     lead=lead_time)
    out_string = fSts.doStringSub()
    assert(out_string == "1987020103_A3h")


def test_h_lead_pad_2_digit_sub():
    logger = logging.getLogger("test")
    file_template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%.2H}h"
    init_time = "1987020103"
    lead_time = "3"
    fSts = StringSub(logger,
                     file_template,
                     init=init_time,
                     lead=lead_time)
    out_string = fSts.doStringSub()
    assert(out_string == "1987020103_A03h")


def test_h_lead_pad_2_digit_sub():
    logger = logging.getLogger("test")
    file_template = "{init?fmt=%Y%m%d%H}_A{lead?fmt=%.3H}h"
    init_time = "1987020103"
    lead_time = "3"
    fSts = StringSub(logger,
                     file_template,
                     init=init_time,
                     lead=lead_time)
    out_string = fSts.doStringSub()
    assert(out_string == "1987020103_A003h")
