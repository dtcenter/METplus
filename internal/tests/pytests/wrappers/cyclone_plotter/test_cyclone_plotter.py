#!/usr/bin/env python3

import pytest
from unittest import mock

pytest.importorskip('pandas')

from metplus.wrappers import cyclone_plotter_wrapper
from metplus.wrappers.cyclone_plotter_wrapper import CyclonePlotterWrapper

TCST_HEADER = 'AMODEL STORM_ID INIT LEAD VALID ALAT ALON\n'
TCST_LINES = [
    'GFSO ML01 20150301_120000 0 20150301_120000 40.0 -70.0\n',
    'GFSO ML01 20150301_120000 60000 20150301_180000 41.0 -69.0\n',
    # same date, earlier hour
    'GFSO ML02 20150301_060000 0 20150301_060000 30.0 -60.0\n',
    # later date, earlier hour
    'GFSO ML03 20150302_000000 0 20150302_000000 20.0 -50.0\n',
    # later date, later hour
    'GFSO ML04 20150302_180000 0 20150302_180000 10.0 -40.0\n',
    # different model
    'OTHR ML05 20150301_120000 0 20150301_120000 15.0 -45.0\n',
]


def set_minimum_config(config, input_dir='/fake/input'):
    config.set('config', 'PROCESS_LIST', 'CyclonePlotter')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H')
    config.set('config', 'INIT_BEG', '2015030112')
    config.set('config', 'CYCLONE_PLOTTER_INPUT_DIR', input_dir)
    config.set('config', 'CYCLONE_PLOTTER_OUTPUT_DIR', '{OUTPUT_BASE}/cyclone')
    config.set('config', 'CYCLONE_PLOTTER_MODEL', 'GFSO')
    config.set('config', 'CYCLONE_PLOTTER_PLOT_TITLE', 'Title')
    config.set('config', 'CYCLONE_PLOTTER_GENERATE_TRACK_ASCII', False)
    config.set('config', 'CYCLONE_PLOTTER_CIRCLE_MARKER_SIZE', 2)
    config.set('config', 'CYCLONE_PLOTTER_CROSS_MARKER_SIZE', 11)
    config.set('config', 'CYCLONE_PLOTTER_ANNOTATION_FONT_SIZE', 3)
    config.set('config', 'CYCLONE_PLOTTER_LEGEND_FONT_SIZE', 3)
    config.set('config', 'CYCLONE_PLOTTER_RESOLUTION_DPI', 400)
    config.set('config', 'CYCLONE_PLOTTER_GLOBAL_PLOT', True)


def create_wrapper(config):
    # cartopy may not be installed in the test environment, so skip the
    # import check that prevents the wrapper from being initialized
    with mock.patch.object(cyclone_plotter_wrapper, 'WRAPPER_CANNOT_RUN',
                           False):
        return CyclonePlotterWrapper(config)


@pytest.mark.parametrize(
    'missing', [
        'CYCLONE_PLOTTER_WEST_LON',
        'CYCLONE_PLOTTER_EAST_LON',
        'CYCLONE_PLOTTER_SOUTH_LAT',
        'CYCLONE_PLOTTER_NORTH_LAT',
    ]
)
@pytest.mark.wrapper
def test_cyclone_plotter_missing_extent(metplus_config, missing):
    config = metplus_config
    set_minimum_config(config)
    config.set('config', 'CYCLONE_PLOTTER_GLOBAL_PLOT', False)
    extent = {
        'CYCLONE_PLOTTER_WEST_LON': -180,
        'CYCLONE_PLOTTER_EAST_LON': 179,
        'CYCLONE_PLOTTER_SOUTH_LAT': 0,
        'CYCLONE_PLOTTER_NORTH_LAT': 90,
    }
    for key, value in extent.items():
        if key != missing:
            config.set('config', key, value)

    wrapper = create_wrapper(config)
    assert not wrapper.is_ok
    assert not hasattr(wrapper, 'extent_region')
    errors = [call[0][0] for call in wrapper.logger.error.call_args_list]
    assert any(f'Missing {missing}' in err for err in errors)


@pytest.mark.wrapper
def test_cyclone_plotter_extent(metplus_config):
    config = metplus_config
    set_minimum_config(config)
    config.set('config', 'CYCLONE_PLOTTER_GLOBAL_PLOT', False)
    config.set('config', 'CYCLONE_PLOTTER_WEST_LON', -180)
    config.set('config', 'CYCLONE_PLOTTER_EAST_LON', 179)
    config.set('config', 'CYCLONE_PLOTTER_SOUTH_LAT', 0)
    config.set('config', 'CYCLONE_PLOTTER_NORTH_LAT', 90)
    wrapper = create_wrapper(config)
    assert wrapper.is_ok
    assert wrapper.extent_region == [-180.0, 179.0, 0.0, 90.0]


@pytest.mark.parametrize(
    'init_date, init_hr, expected', [
        # 0: date and hour both set
        ('20150301', '12', (20150301, 12)),
        # 1: hour unset, derived from YYYYMMDDHH date
        ('2015030112', '', (20150301, 12)),
        # 2: hour unset, date only - use hour 0
        ('20150301', '', (20150301, 0)),
        # 3: hour unset, template date
        ('{init?fmt=%Y%m%d%H}', None, (20150301, 12)),
        # 4: template date and hour
        ('{init?fmt=%Y%m%d}', '{init?fmt=%H}', (20150301, 12)),
        # 5: invalid date
        ('', '', (None, None)),
    ]
)
@pytest.mark.wrapper
def test_cyclone_plotter_init_date_and_hour(metplus_config, init_date,
                                            init_hr, expected):
    config = metplus_config
    set_minimum_config(config)
    config.set('config', 'CYCLONE_PLOTTER_INIT_DATE', init_date)
    if init_hr is not None:
        config.set('config', 'CYCLONE_PLOTTER_INIT_HR', init_hr)

    wrapper = create_wrapper(config)
    assert wrapper._get_init_date_and_hour() == expected
    if expected[0] is None:
        assert not wrapper.is_ok


@pytest.mark.parametrize(
    'init_date, init_hr, model, expected_storms', [
        # init date and hour are compared separately (date >= INIT_DATE and
        # hour >= INIT_HR) to preserve existing use case output
        # 0: date and hour set
        ('20150301', '12', 'GFSO', ['ML01', 'ML04']),
        # 1: hour derived from date
        ('2015030112', '', 'GFSO', ['ML01', 'ML04']),
        # 2: no hour, all hours on or after date
        ('20150301', '', 'GFSO', ['ML01', 'ML02', 'ML03', 'ML04']),
        # 3: no model filter
        ('20150301', '12', '', ['ML01', 'ML04', 'ML05']),
        # 4: later date
        ('20150302', '00', 'GFSO', ['ML03', 'ML04']),
    ]
)
@pytest.mark.wrapper
def test_cyclone_plotter_retrieve_data(metplus_config, tmp_path,
                                       init_date, init_hr, model,
                                       expected_storms):
    input_dir = tmp_path
    with open(input_dir / 'tracks.tcst', 'w') as file_handle:
        file_handle.write(TCST_HEADER)
        file_handle.writelines(TCST_LINES)

    config = metplus_config
    set_minimum_config(config, input_dir=str(input_dir))
    config.set('config', 'CYCLONE_PLOTTER_INIT_DATE', init_date)
    config.set('config', 'CYCLONE_PLOTTER_INIT_HR', init_hr)
    config.set('config', 'CYCLONE_PLOTTER_MODEL', model)

    wrapper = create_wrapper(config)
    result = wrapper.retrieve_data()
    assert result is not None
    assert sorted(set(result['STORM_ID'])) == expected_storms
