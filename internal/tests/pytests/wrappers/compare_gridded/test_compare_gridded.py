#!/usr/bin/env python3

import pytest

from metplus.wrappers.compare_gridded_wrapper import CompareGriddedWrapper


def compare_gridded_wrapper(metplus_config):
    """! Returns a default GridStatWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    config = metplus_config
    return CompareGriddedWrapper(config)


@pytest.mark.parametrize(
    'key, value', [
        # forecast name and level
        (['NAME', 'L0', [], '', 'FCST'],
         ['{ name="NAME"; level="L0"; }']),

        # forecast name only
        (['NAME', '', [], '', 'FCST'],
         ['{ name="NAME"; }']),

        # forecast name level thresh
        (['NAME', 'L0', ['gt3', '<=5'], '', 'FCST'],
         ['{ name="NAME"; level="L0"; cat_thresh=[ gt3,<=5 ]; }']),

        # forecast name level thresh extra
        (['NAME', 'L0', ['gt3', '<=5'], 'extra=val;', 'FCST'],
         ['{ name="NAME"; level="L0"; cat_thresh=[ gt3,<=5 ]; extra=val; }']),

        # forecast name only py script
        (['/some/script/name.py args /path/of/infile.txt', '', [], '', 'FCST'],
         ['{ name="/some/script/name.py args /path/of/infile.txt"; }']),

        # obs name and level
        (['NAME', 'L0', [], '', 'OBS'],
         ['{ name="NAME"; level="L0"; }']),

        # obs name only
        (['NAME', '', [], '', 'OBS'],
         ['{ name="NAME"; }']),

        # obs name level thresh
        (['NAME', 'L0', ['gt3', '<=5'], '', 'OBS'],
         ['{ name="NAME"; level="L0"; cat_thresh=[ gt3,<=5 ]; }']),

        # obs name level thresh extra
        (['NAME', 'L0', ['gt3', '<=5'], 'extra=val;', 'OBS'],
         ['{ name="NAME"; level="L0"; cat_thresh=[ gt3,<=5 ]; extra=val; }']),

        # obs name only py script
        (['/some/script/name.py args /path/of/infile.txt', '', [], '', 'OBS'],
         ['{ name="/some/script/name.py args /path/of/infile.txt"; }']),

        # forecast name with single quotes
        (["'NAME'", "L0", [], '', 'FCST'],
         ['{ name="NAME"; level="L0"; }']),

        # forecast level with single quotes
        (['NAME', "'L0'", [], '', 'FCST'],
         ['{ name="NAME"; level="L0"; }']),

        # forecast name with double quotes
        (['"NAME"', "L0", [], '', 'FCST'],
         ['{ name="NAME"; level="L0"; }']),

        # forecast level with double quotes
        (['NAME', '"L0"', [], '', 'FCST'],
         ['{ name="NAME"; level="L0"; }']),
    ]
)
@pytest.mark.wrapper
def test_get_field_info_no_prob(metplus_config, key, value):
    w = compare_gridded_wrapper(metplus_config)
    w.c_dict['FCST_IS_PROB'] = False

    field_dict = {
        'v_name': key[0],
        'v_level': key[1],
        'v_thresh': key[2],
        'v_extra': key[3],
        'd_type': key[4],
    }

    fields = w.get_field_info(**field_dict)
    assert fields == value


@pytest.mark.parametrize(
    'prob_in_grib_pds, key, value', [
        # grib pds True, forecast grib name level thresh
        (True, ['NAME', 'L0', ['gt3', '<=5'], '', 'FCST'],
         ['{ name="PROB"; level="L0"; prob={ name="NAME"; thresh_lo=3.0; } cat_thresh=[ ==0.1 ]; }',
          '{ name="PROB"; level="L0"; prob={ name="NAME"; thresh_hi=5.0; } cat_thresh=[ ==0.1 ]; }']),

        # grib pds True, obs grib name level thresh
        (True, ['NAME', 'L0', ['gt3', '<=5'], '', 'OBS'],
         ['{ name="NAME"; level="L0"; cat_thresh=[ gt3 ]; }',
          '{ name="NAME"; level="L0"; cat_thresh=[ <=5 ]; }']),

        #grib pds True, fcst complex thresh
        (True, ['NAME', 'L0', ['gt3&&lt5'], '', 'FCST'],
         ['{ name="PROB"; level="L0"; prob={ name="NAME"; thresh_lo=3.0; thresh_hi=5.0; } cat_thresh=[ ==0.1 ]; }']),

        # grib pds True, fcst grib name py script
        (True, ['/some/script/name.py args /path/of/infile.txt', '', [], '', 'FCST'],
         ['{ name="/some/script/name.py args /path/of/infile.txt"; prob=TRUE; cat_thresh=[ ==0.1 ]; }']),

        # grib pds True, obs name py script
        (True, ['/some/script/name.py args /path/of/infile.txt', '', [], '', 'OBS'],
         ['{ name="/some/script/name.py args /path/of/infile.txt"; }']),

        # grib pds True, single quotes around field name
        (True, ["'NAME'", 'L0', ['gt3', '<=5'], '', 'FCST'],
         ['{ name="PROB"; level="L0"; prob={ name="NAME"; thresh_lo=3.0; } cat_thresh=[ ==0.1 ]; }',
          '{ name="PROB"; level="L0"; prob={ name="NAME"; thresh_hi=5.0; } cat_thresh=[ ==0.1 ]; }']),

        # grib pds True, double quotes around field name
        (True, ['"NAME"', 'L0', ['gt3', '<=5'], '', 'FCST'],
         ['{ name="PROB"; level="L0"; prob={ name="NAME"; thresh_lo=3.0; } cat_thresh=[ ==0.1 ]; }',
          '{ name="PROB"; level="L0"; prob={ name="NAME"; thresh_hi=5.0; } cat_thresh=[ ==0.1 ]; }']),

        # grib pds True, no thresholds specified - raises ValueError
        (True, ['NAME', 'L0', [], '', 'FCST'],
         ValueError('Must set thresholds if FCST_PROB_IN_GRIB_PDS=True.')),

        # grib pds False, obs grib name level thresh
        (False, ['NAME', 'L0', ['gt3', '<=5'], '', 'OBS'],
         ['{ name="NAME"; level="L0"; cat_thresh=[ gt3 ]; }',
          '{ name="NAME"; level="L0"; cat_thresh=[ <=5 ]; }']),

        # grib pds False, complex thresh (ignored)
        (False, ['NAME', 'L0', ['gt3&&lt5'], '', 'FCST'],
         ['{ name="NAME"; level="L0"; prob=TRUE; cat_thresh=[ ==0.1 ]; }']),

        # grib pds False, fcst grib name py script
        (False, ['/some/script/name.py args /path/of/infile.txt', '', [], '', 'FCST'],
         ['{ name="/some/script/name.py args /path/of/infile.txt"; prob=TRUE; cat_thresh=[ ==0.1 ]; }']),

        # grib pds False, obs name py script
        (False, ['/some/script/name.py args /path/of/infile.txt', '', [], '', 'OBS'],
         ['{ name="/some/script/name.py args /path/of/infile.txt"; }']),

        # grib pds False, single quotes around field name
        (False, ["'NAME'", 'L0', ['gt3', '<=5'], '', 'FCST'],
         ['{ name="NAME"; level="L0"; prob=TRUE; cat_thresh=[ ==0.1 ]; }',
          '{ name="NAME"; level="L0"; prob=TRUE; cat_thresh=[ ==0.1 ]; }']),

        # grib pds False, double quotes around field name
        (False, ['"NAME"', 'L0', ['gt3', '<=5'], '', 'FCST'],
         ['{ name="NAME"; level="L0"; prob=TRUE; cat_thresh=[ ==0.1 ]; }',
          '{ name="NAME"; level="L0"; prob=TRUE; cat_thresh=[ ==0.1 ]; }']),
    ]
)
@pytest.mark.wrapper
def test_get_field_info_fcst_prob_grib(metplus_config, prob_in_grib_pds, key, value):
    w = compare_gridded_wrapper(metplus_config)
    w.c_dict['FCST_IS_PROB'] = True
    w.c_dict['FCST_INPUT_DATATYPE'] = 'GRIB'
    w.c_dict['FCST_PROB_IN_GRIB_PDS'] = prob_in_grib_pds
    w.c_dict['FCST_PROB_THRESH'] = '==0.1'

    field_dict = {
        'v_name': key[0],
        'v_level': key[1],
        'v_thresh': key[2],
        'v_extra': key[3],
        'd_type': key[4],
    }

    try:
        fields = w.get_field_info(**field_dict)
    except ValueError as e:
        assert str(e) == str(value)
    else:
        assert fields == value


@pytest.mark.parametrize(
    'key, value', [

        # forecast netcdf name level
        (['NAME_gt3', 'L0', [], '', 'FCST'],
         ['{ name="NAME_gt3"; level="L0"; prob=TRUE; }']),

        # obs netcdf name level thresh
        (['NAME', 'L0', ['gt3'], '', 'OBS'],
         ['{ name="NAME"; level="L0"; cat_thresh=[ gt3 ]; }']),

        # forecast netcdf name level - single quotes around field name
        (["'NAME_gt3'", 'L0', [], '', 'FCST'],
         ['{ name="NAME_gt3"; level="L0"; prob=TRUE; }']),

        # obs netcdf name level thresh - single quotes around field name
        (["'NAME'", 'L0', ['gt3'], '', 'OBS'],
         ['{ name="NAME"; level="L0"; cat_thresh=[ gt3 ]; }']),

        # forecast netcdf name level - double quotes around field name
        (['"NAME_gt3"', 'L0', [], '', 'FCST'],
         ['{ name="NAME_gt3"; level="L0"; prob=TRUE; }']),

        # obs netcdf name level thresh - double quotes around field name
        (['"NAME"', 'L0', ['gt3'], '', 'OBS'],
         ['{ name="NAME"; level="L0"; cat_thresh=[ gt3 ]; }']),
    ]
)
@pytest.mark.wrapper
def test_get_field_info_fcst_prob_netcdf(metplus_config, key, value):
    w = compare_gridded_wrapper(metplus_config)
    w.c_dict['FCST_IS_PROB'] = True
    w.c_dict['FCST_INPUT_DATATYPE'] = 'NETCDF'

    field_dict = {
        'v_name': key[0],
        'v_level': key[1],
        'v_thresh': key[2],
        'v_extra': key[3],
        'd_type': key[4],
    }
    
    fields = w.get_field_info(**field_dict)
    assert fields == value


@pytest.mark.parametrize(
    'win, app_win, file_win, app_file_win, win_value, file_win_value', [
        ([1, 2, 3, 4, 2, 4]),
        ([1, 2, 3, None, 2, 3]),
        ([1, 2, None, None, 2, 0]),
        ([1, None, None, None, 1, 0]),
        ([None, None, None, None, -5400, 0]),
        ([1, None, 3, 4, 1, 4]),
        ([1, None, 3, 4, 1, 4]),
    ]
)
@pytest.mark.wrapper
def test_handle_window_once(metplus_config, win, app_win, file_win, app_file_win, win_value, file_win_value):
    cgw = compare_gridded_wrapper(metplus_config)
    config = cgw.config

    if win is not None:
        config.set('config', 'OBS_WINDOW_BEGIN', win)

    if app_win is not None:
        config.set('config', 'OBS_APP_NAME_WINDOW_BEGIN', app_win)

    if file_win is not None:
        config.set('config', 'FCST_FILE_WINDOW_BEGIN', file_win)

    if app_file_win is not None:
        config.set('config', 'FCST_APP_NAME_FILE_WINDOW_BEGIN', app_file_win)

    input_list = ['FCST_APP_NAME_FILE_WINDOW_BEGIN',
                  'FCST_FILE_WINDOW_BEGIN',
                  'FILE_WINDOW_BEGIN',
                 ]
    fcst_file_window_begin = cgw._handle_window_once(input_list, 0)

    input_list = ['OBS_APP_NAME_WINDOW_BEGIN',
                  'OBS_WINDOW_BEGIN',
                 ]
    obs_window_begin = cgw._handle_window_once(input_list, -5400)

    assert obs_window_begin == win_value
    assert fcst_file_window_begin == file_win_value
