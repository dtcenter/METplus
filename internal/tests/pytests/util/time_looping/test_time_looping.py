import pytest

from dateutil.relativedelta import relativedelta

from metplus.util.time_looping import *


@pytest.mark.util
def test_get_start_and_end_times(metplus_config):
    start_time = '2014103109'
    end_time = '2018103109'
    time_format = '%Y%m%d%H'
    for prefix in ['INIT', 'VALID']:
        config = metplus_config()
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
        config = metplus_config()
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
        config = metplus_config()
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
        config = metplus_config()
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
        config = metplus_config()
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


@pytest.mark.util
def test_time_generator_error_check(metplus_config):
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
    for prefix in ['INIT', 'VALID']:
        config = metplus_config()

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

        # get a fresh config object to test BEG/END configurations
        config = metplus_config()
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
