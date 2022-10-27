import pytest

from datetime import datetime
from dateutil.relativedelta import relativedelta

from metplus.util.time_looping import *
from metplus.util.time_util import ti_calculate


@pytest.mark.parametrize(
    'run_time, skip_times, expected_result', [
        (datetime(2019, 12, 30), {'%d': ['30', '31']}, True),
        (datetime(2019, 12, 30), {'%d': ['29', '31']}, False),
        (datetime(2019, 2, 27), {'%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}, False),
        (datetime(2019, 3, 30), {'%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}, True),
        (datetime(2019, 3, 30), {'%d': ['30', '31'],
                                          '%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}, True),
        (datetime(2019, 3, 29), {'%d': ['30', '31'],
                                          '%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}, True),
        (datetime(2019, 1, 29), {'%d': ['30', '31'],
                                          '%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}, False),
        (datetime(2020, 10, 31), {'%Y%m%d': ['20201031']}, True),
        (datetime(2020, 3, 31), {'%Y%m%d': ['20201031']}, False),
        (datetime(2020, 10, 30), {'%Y%m%d': ['20201031']}, False),
        (datetime(2019, 10, 31), {'%Y%m%d': ['20201031']}, False),
        (datetime(2020, 10, 31), {'%Y%m%d': ['20201031'],
                                          '%Y': ['2019']}, True),
        (datetime(2019, 10, 31), {'%Y%m%d': ['20201031'],
                                          '%Y': ['2019']}, True),
        (datetime(2019, 1, 13), {'%Y%m%d': ['20201031'],
                                          '%Y': ['2019']}, True),
        (datetime(2018, 10, 31), {'%Y%m%d': ['20201031'],
                                          '%Y': ['2019']}, False),
        (datetime(2019, 12, 30, 12), {'%H': ['12', '18']}, True),
        (datetime(2019, 12, 30, 13), {'%H': ['12', '18']}, False),
    ]
)
@pytest.mark.util
def test_get_skip_time(run_time, skip_times, expected_result):
    time_info = ti_calculate({'valid': run_time})
    assert skip_time(time_info, skip_times) == expected_result


@pytest.mark.util
def test_get_skip_time_no_valid():
    input_dict ={'init': datetime(2019, 1, 29)}
    assert skip_time(input_dict, {'%Y': ['2019']}) == False


@pytest.mark.parametrize(
    'skip_times_conf, expected_dict', [
        ('"%d:30,31"', {'%d': ['30','31']}),
        ('"%m:begin_end_incr(3,11,1)"', {'%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}),
        ('"%d:30,31", "%m:begin_end_incr(3,11,1)"', {'%d': ['30','31'],
                                                     '%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}),
        ('"%Y%m%d:20201031"', {'%Y%m%d': ['20201031']}),
        ('"%Y%m%d:20201031", "%Y:2019"', {'%Y%m%d': ['20201031'],
                                          '%Y': ['2019']}),
    ]
)
@pytest.mark.util
def test_get_skip_times(metplus_config, skip_times_conf, expected_dict):
    conf = metplus_config
    conf.set('config', 'SKIP_TIMES', skip_times_conf)

    assert get_skip_times(conf) == expected_dict


@pytest.mark.parametrize(
    'skip_times_conf, expected_dict', [
        ('"%d:30,31"', {'%d': ['30','31']}),
        ('"%m:begin_end_incr(3,11,1)"', {'%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}),
        ('"%d:30,31", "%m:begin_end_incr(3,11,1)"', {'%d': ['30','31'],
                                                     '%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}),
        ('"%Y%m%d:20201031"', {'%Y%m%d': ['20201031']}),
        ('"%Y%m%d:20201031", "%Y:2019"', {'%Y%m%d': ['20201031'],
                                          '%Y': ['2019']}),
    ]
)
@pytest.mark.util
def test_get_skip_times_wrapper(metplus_config, skip_times_conf, expected_dict):
    conf = metplus_config

    # set wrapper specific skip times, then ensure it is found
    conf.set('config', 'GRID_STAT_SKIP_TIMES', skip_times_conf)

    assert get_skip_times(conf, 'grid_stat') == expected_dict


@pytest.mark.parametrize(
    'skip_times_conf, expected_dict', [
        ('"%d:30,31"', {'%d': ['30','31']}),
        ('"%m:begin_end_incr(3,11,1)"', {'%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}),
        ('"%d:30,31", "%m:begin_end_incr(3,11,1)"', {'%d': ['30','31'],
                                                     '%m': ['3', '4', '5', '6', '7', '8', '9', '10', '11']}),
        ('"%Y%m%d:20201031"', {'%Y%m%d': ['20201031']}),
        ('"%Y%m%d:20201031", "%Y:2019"', {'%Y%m%d': ['20201031'],
                                          '%Y': ['2019']}),
    ]
)
@pytest.mark.util
def test_get_skip_times_wrapper_not_used(metplus_config, skip_times_conf, expected_dict):
    conf = metplus_config

    # set generic SKIP_TIMES, then request grid_stat to ensure it uses generic
    conf.set('config', 'SKIP_TIMES', skip_times_conf)

    assert get_skip_times(conf, 'grid_stat') == expected_dict


@pytest.mark.util
def test_get_start_and_end_times(metplus_config):
    start_time = '2014103109'
    end_time = '2018103109'
    time_format = '%Y%m%d%H'
    for prefix in ['INIT', 'VALID']:
        config = metplus_config
        config.set('config', 'LOOP_BY', prefix)
        config.set('config', f'{prefix}_TIME_FMT', time_format)
        config.set('config', f'{prefix}_BEG', start_time)
        config.set('config', f'{prefix}_END', end_time)
        start_dt, end_dt = get_start_and_end_times(config)
        assert start_dt.strftime(time_format) == start_time
        assert end_dt.strftime(time_format) == end_time


@pytest.mark.util
def test_get_start_and_end_times_now(metplus_config):
    time_format = '%Y%m%d%H%M%S'
    for prefix in ['INIT', 'VALID']:
        config = metplus_config
        config.set('config', 'LOOP_BY', prefix)
        config.set('config', f'{prefix}_TIME_FMT', time_format)
        config.set('config', f'{prefix}_BEG', '{now?fmt=%Y%m%d%H%M%S?shift=-1d}')
        config.set('config', f'{prefix}_END', '{now?fmt=%Y%m%d%H%M%S}')
        start_dt, end_dt = get_start_and_end_times(config)
        expected_end_time = config.getstr('config', 'CLOCK_TIME')
        yesterday_dt = datetime.strptime(expected_end_time, time_format) - relativedelta(days=1)
        expected_start_time = yesterday_dt.strftime(time_format)

        assert start_dt.strftime(time_format) == expected_start_time
        assert end_dt.strftime(time_format) == expected_end_time


@pytest.mark.util
def test_get_start_and_end_times_today(metplus_config):
    time_format = '%Y%m%d'
    for prefix in ['INIT', 'VALID']:
        config = metplus_config
        config.set('config', 'LOOP_BY', prefix)
        config.set('config', f'{prefix}_TIME_FMT', time_format)
        config.set('config', f'{prefix}_BEG', '{today}')
        config.set('config', f'{prefix}_END', '{today}')
        start_dt, end_dt = get_start_and_end_times(config)
        clock_time = config.getstr('config', 'CLOCK_TIME')
        clock_dt = datetime.strptime(clock_time, '%Y%m%d%H%M%S')
        expected_time = clock_dt.strftime(time_format)

        assert start_dt.strftime(time_format) == expected_time
        assert end_dt.strftime(time_format) == expected_time


@pytest.mark.util
def test_time_generator_list(metplus_config):
    for prefix in ['INIT', 'VALID']:
        config = metplus_config
        config.set('config', 'LOOP_BY', prefix)
        config.set('config', f'{prefix}_TIME_FMT', '%Y%m%d%H')
        config.set('config', f'{prefix}_LIST', '2021020104, 2021103121')

        expected_times = [
            datetime.strptime('2021020104', '%Y%m%d%H'),
            datetime.strptime('2021103121', '%Y%m%d%H'),
        ]

        generator = time_generator(config)
        assert next(generator)[prefix.lower()] == expected_times[0]
        assert next(generator)[prefix.lower()] == expected_times[1]
        try:
            next(generator)
            assert False
        except StopIteration:
            assert True


@pytest.mark.util
def test_time_generator_increment(metplus_config):
    for prefix in ['INIT', 'VALID']:
        config = metplus_config
        config.set('config', 'LOOP_BY', prefix)
        config.set('config', f'{prefix}_TIME_FMT', '%Y%m%d%H')
        config.set('config', f'{prefix}_BEG', '2021020104')
        config.set('config', f'{prefix}_END', '2021020106')
        config.set('config', f'{prefix}_INCREMENT', '1H')

        expected_times = [
            datetime.strptime('2021020104', '%Y%m%d%H'),
            datetime.strptime('2021020105', '%Y%m%d%H'),
            datetime.strptime('2021020106', '%Y%m%d%H'),
        ]

        generator = time_generator(config)
        assert next(generator)[prefix.lower()] == expected_times[0]
        assert next(generator)[prefix.lower()] == expected_times[1]
        assert next(generator)[prefix.lower()] == expected_times[2]
        try:
            next(generator)
            assert False
        except StopIteration:
            assert True


@pytest.mark.parametrize(
    'prefix', [
        'INIT', 'VALID',
    ]
)
@pytest.mark.util
def test_time_generator_error_check_list(metplus_config, prefix):
    """! Test that None is returned by the time generator when
    the time looping config variables are not set properly. Tests:
    Missing LOOP_BY,
    Missing [INIT/VALID]_TIME_FMT,
    Empty [INIT/VALID]_LIST (if set),
    List value doesn't match time format,
    _BEG or _END value doesn't match format,
    _INCREMENT is less than 60 seconds,
    _BEG is after _END,
    """
    time_fmt = '%Y%m%d%H'
    config = metplus_config

    # unset LOOP_BY
    assert next(time_generator(config)) is None
    config.set('config', 'LOOP_BY', prefix)

    # unset _TIME_FMT
    assert next(time_generator(config)) is None
    config.set('config', f'{prefix}_TIME_FMT', time_fmt)

    # test [INIT/VALID]_LIST configurations

    #  empty _LIST
    config.set('config', f'{prefix}_LIST', '')
    assert next(time_generator(config)) is None

    # list value doesn't match format
    config.set('config', f'{prefix}_LIST', '202102010412')
    assert next(time_generator(config)) is None

    # 2nd list value doesn't match format
    config.set('config', f'{prefix}_LIST', '2021020104, 202102010412')
    expected_time = datetime.strptime('2021020104', time_fmt)
    generator = time_generator(config)
    assert next(generator)[prefix.lower()] == expected_time
    assert next(generator) is None

    #  good _LIST
    config.set('config', f'{prefix}_LIST', '2021020104')
    assert next(time_generator(config))[prefix.lower()] == expected_time


@pytest.mark.parametrize(
    'prefix', [
        'INIT', 'VALID',
    ]
)
@pytest.mark.util
def test_time_generator_error_check_beg_end(metplus_config, prefix):
    """! Test that None is returned by the time generator when
    the time looping config variables are not set properly. Tests:
    Missing LOOP_BY,
    Missing [INIT/VALID]_TIME_FMT,
    Empty [INIT/VALID]_LIST (if set),
    List value doesn't match time format,
    _BEG or _END value doesn't match format,
    _INCREMENT is less than 60 seconds,
    _BEG is after _END,
    """
    time_fmt = '%Y%m%d%H'
    config = metplus_config
    config.set('config', 'LOOP_BY', prefix)
    config.set('config', f'{prefix}_TIME_FMT', time_fmt)

    # _BEG doesn't match time format (too long)
    config.set('config', f'{prefix}_BEG', '202110311259')
    config.set('config', f'{prefix}_END', '2021112012')

    assert next(time_generator(config)) is None
    config.set('config', f'{prefix}_BEG', '2021103112')

    # unset _END uses _BEG value, so it should succeed
    assert next(time_generator(config)) is not None

    # _END doesn't match time format (too long)
    config.set('config', f'{prefix}_END', '202111201259')

    assert next(time_generator(config)) is None
    config.set('config', f'{prefix}_END', '2021112012')
    assert next(time_generator(config)) is not None

    # _INCREMENT is less than 60 seconds
    config.set('config', f'{prefix}_INCREMENT', '10S')
    assert next(time_generator(config)) is None
    config.set('config', f'{prefix}_INCREMENT', '1d')

    # _END time comes before _BEG time
    config.set('config', f'{prefix}_END', '2020112012')
    assert next(time_generator(config)) is None
