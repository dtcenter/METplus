import pytest

from metplus.util.time_looping import *


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
