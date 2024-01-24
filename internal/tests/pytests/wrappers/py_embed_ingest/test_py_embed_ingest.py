import os
import datetime
import pytest
from unittest import mock
from metplus.wrappers.py_embed_ingest_wrapper import PyEmbedIngestWrapper
from metplus.wrappers.command_builder import CommandBuilder


time_fmt = "%Y%m%d%H"
run_times = ["2023100600", "2023100612", "2023100700"]
time_info = {
    "loop_by": "init",
    "init": datetime.datetime(2023, 10, 6, 0, 0),
    "now": datetime.datetime(2023, 10, 6, 0, 0),
    "today": "20231010",
    "instance": "",
    "valid": "*",
    "lead": "*",
}

# Helper class for string matching
class MatchSubstring(str):
    def __eq__(self, other):
        return self in other

def mock_get_ingest_items(item_type, index, ingest_script_addons):
    # mock `get_ingest_items` to create a test case for config error log where number of
    # output fields does not the same as number of script.
    if item_type=="OUTPUT_FIELD_NAME":
        return ["field_1", "field_2"]
    else:
        return ["field_1"]

def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set("config", "DO_NOT_RUN_EXE", True)
    config.set("config", "INPUT_MUST_EXIST", False)

    # set process and time config variables
    config.set("config", "PROCESS_LIST", "PyEmbedIngest")
    config.set("config", "LOOP_BY", "INIT")
    config.set("config", "INIT_TIME_FMT", time_fmt)
    config.set("config", "INIT_BEG", run_times[0])
    config.set("config", "INIT_END", run_times[-1])
    config.set("config", "INIT_INCREMENT", "12H")
    config.set("config", "LEAD_SEQ", "12H")


@pytest.mark.parametrize(
    'config_overrides, mock_file_check, expected_values, expected_error_numbers', [
        # 0 a case with one index while find_and_check_output_file returns True
        (
            {
                'PY_EMBED_INGEST_1_OUTPUT_DIR': "outdir/",
                "PY_EMBED_INGEST_1_OUTPUT_TEMPLATE": "output_file.nc",
                "PY_EMBED_INGEST_1_SCRIPT": "fake_script",
                "PY_EMBED_INGEST_1_TYPE": "NUMPY",
                "PY_EMBED_INGEST_1_OUTPUT_GRID": "fake_grid",
                "PY_EMBED_INGEST_1_OUTPUT_FIELD_NAME": "fake_filed"
            },
            True,
            [
                {
                    "output_dir": "outdir/",
                    "output_template": "output_file.nc",
                    "output_field_names": ["fake_filed"],
                    "scripts": ["fake_script"],
                    "input_type": "NUMPY",
                    "output_grid": "fake_grid",
                    "index": "1",
                }
            ],
            1,
        ),
         # 1 a case with one index while find_and_check_output_file returns False
        (
            {
                'PY_EMBED_INGEST_1_OUTPUT_DIR': "outdir/",
                "PY_EMBED_INGEST_1_OUTPUT_TEMPLATE": "output_file.nc",
                "PY_EMBED_INGEST_1_SCRIPT": "fake_script",
                "PY_EMBED_INGEST_1_TYPE": "NUMPY",
                "PY_EMBED_INGEST_1_OUTPUT_GRID": "fake_grid",
                "PY_EMBED_INGEST_1_OUTPUT_FIELD_NAME": "fake_filed"
            },
            False,
            [{
                "output_dir": "outdir/",
                "output_template": "output_file.nc",
                "output_field_names": ["fake_filed"],
                "scripts": ["fake_script"],
                "input_type": "NUMPY",
                "output_grid": "fake_grid",
                "index": "1",
            }],
            0,
        ),
         # 2 a case with two indices while find_and_check_output_file returns True
        (
            {
                'PY_EMBED_INGEST_1_OUTPUT_DIR': "outdir/",
                "PY_EMBED_INGEST_1_OUTPUT_TEMPLATE": "first_output_file.nc",
                "PY_EMBED_INGEST_1_SCRIPT": "first_fake_script",
                "PY_EMBED_INGEST_1_TYPE": "NUMPY",
                "PY_EMBED_INGEST_1_OUTPUT_GRID": "first_fake_grid",
                "PY_EMBED_INGEST_1_OUTPUT_FIELD_NAME": "first_fake_filed",
                'PY_EMBED_INGEST_2_OUTPUT_DIR': "outdir/",
                "PY_EMBED_INGEST_2_OUTPUT_TEMPLATE": "second_output_file.nc",
                "PY_EMBED_INGEST_2_SCRIPT": "second_fake_script",
                "PY_EMBED_INGEST_2_TYPE": "NUMPY",
                "PY_EMBED_INGEST_2_OUTPUT_GRID": "second_fake_grid",
                "PY_EMBED_INGEST_2_OUTPUT_FIELD_NAME": "second_fake_filed",
            },
            True,
            [
                {
                    "output_dir": "outdir/",
                    "output_template": "first_output_file.nc",
                    "output_field_names": ["first_fake_filed"],
                    "scripts": ["first_fake_script"],
                    "input_type": "NUMPY",
                    "output_grid": "first_fake_grid",
                    "index": "1",
                },
                {
                    "output_dir": "outdir/",
                    "output_template": "second_output_file.nc",
                    "output_field_names": ["second_fake_filed"],
                    "scripts": ["second_fake_script"],
                    "input_type": "NUMPY",
                    "output_grid": "second_fake_grid",
                    "index": "2",
                },
            ],
            2,
        ),
    ]
)
@pytest.mark.wrapper_b
def test_required_job_template(
    metplus_config,
    mock_file_check,
    config_overrides,
    expected_values,
    expected_error_numbers
):
    config = metplus_config

    set_minimum_config_settings(config)
    with mock.patch.object(CommandBuilder, "build", return_value=False):
        with mock.patch.object(
            CommandBuilder, "find_and_check_output_file", return_value=mock_file_check
        ):
            # set config variable overrides
            for key, value in config_overrides.items():
                config.set('config', key, value)

            wrapper = PyEmbedIngestWrapper(config)
            assert wrapper.isOK
            assert wrapper.c_dict["INGESTERS"] == expected_values
            assert wrapper.run_at_time_once(time_info) == True
            assert wrapper.errors == expected_error_numbers

@pytest.mark.wrapper
def test_conf_error_log(metplus_config, monkeypatch):
    '''Check correct error messages are logged'''
    config = metplus_config
    set_minimum_config_settings(config)

    config_overrides = {
            'PY_EMBED_INGEST_1_OUTPUT_DIR': "outdir/",
            "PY_EMBED_INGEST_1_OUTPUT_TEMPLATE": "output_file.nc",
            "PY_EMBED_INGEST_1_SCRIPT": "fake_script xv mv",
            "PY_EMBED_INGEST_1_TYPE": "PANDAS",
            "PY_EMBED_INGEST_1_OUTPUT_GRID": "fake_grid",
            "PY_EMBED_INGEST_1_OUTPUT_FIELD_NAME": "fake_filed",
            'PY_EMBED_INGEST_2_OUTPUT_DIR': "outdir/",
            "PY_EMBED_INGEST_2_OUTPUT_TEMPLATE": "output_file.nc",
            "PY_EMBED_INGEST_2_SCRIPT": "fake_script",
            "PY_EMBED_INGEST_2_TYPE": "FAKE",
            "PY_EMBED_INGEST_2_OUTPUT_GRID": "",
            "PY_EMBED_INGEST_2_OUTPUT_FIELD_NAME": "fake_filed",
            "PY_EMBED_INGEST_2_OUTPUT_FIELD_NAME_2": "fake_filed2"
        }
    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)
    wrapper = PyEmbedIngestWrapper(config)
    expected_error = [
        'Running PyEmbedIngester on pandas data not yet implemented',
        'PY_EMBED_INGEST_2_TYPE (FAKE) not valid. Valid types are NUMPY, XARRAY, PANDAS',
        'Must set PY_EMBED_INGEST_2_OUTPUT_GRID',
        "If using PY_EMBED_INGEST_1_OUTPUT_FIELD_NAME*, the number of output names must"
        " match the number of PY_EMBED_INGEST_1_SCRIPT* values"
    ]
    with mock.patch.object(wrapper, "get_ingest_items", mock_get_ingest_items):
        wrapper.create_c_dict()
    
    for msg in expected_error:
        wrapper.logger.error.assert_any_call(MatchSubstring(msg))
