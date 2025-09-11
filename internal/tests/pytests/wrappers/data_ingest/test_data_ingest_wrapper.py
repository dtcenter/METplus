#!/usr/bin/env python3

import pytest

import os
from datetime import datetime
from pathlib import Path

from metplus.wrappers.data_ingest_wrapper import DataIngestWrapper
from metplus.util import do_string_sub

time_fmt = '%Y%m%d%H'
run_times = ['2022072000', '2022072012']
MADIS_URL_TOP = 'https://madis-data.ncep.noaa.gov/madisPublic/data/archive'
MADIS_URL_REL = '{valid?fmt=%Y/%m/%d}/point/metar/netcdf/{valid?fmt=%Y%m%d_%H%M}.gz'


def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'DataIngest')
    config.set('config', 'LOOP_BY', 'VALID')
    config.set('config', 'VALID_TIME_FMT', time_fmt)
    config.set('config', 'VALID_BEG', run_times[0])
    config.set('config', 'VALID_END', run_times[-1])
    config.set('config', 'VALID_INCREMENT', '12H')
    config.set('config', 'LEAD_SEQ', '0')


@pytest.mark.parametrize(
    'input_dir, input_template, output_path, already_exists, skip_if_exists, is_ok', [
        # successful download
        (MADIS_URL_TOP, MADIS_URL_REL, '{valid?fmt=%Y%m%d_%H%M}.nc', True, False, True),
        # no url specified - not OK
        (None, None, '{valid?fmt=%Y%m%d_%H%M}.nc', False, True, False),
        # file already exists - skip download
        (MADIS_URL_TOP, MADIS_URL_REL, '{valid?fmt=%Y%m%d_%H%M}.nc', True, True, True),
        # bad URL - not OK
        (MADIS_URL_TOP, f"x{MADIS_URL_REL}", '{valid?fmt=%Y%m%d_%H%M}.nc', False, True, False),
    ]
)
@pytest.mark.wrapper_b
def test_grid_stat_missing_inputs(metplus_config, tmp_path_factory,
                                  input_dir, input_template, output_path,
                                  already_exists, skip_if_exists, is_ok):
    out_dir = tmp_path_factory.mktemp('output')

    expected_files = []
    if input_template:
        for run_time in run_times:
            rel_path = do_string_sub(output_path, valid=datetime.strptime(run_time, time_fmt))
            expected_files.append(f"{out_dir}/{rel_path}")

    config = metplus_config
    set_minimum_config_settings(config)
    if input_dir:
        config.set('config', 'DATA_INGEST_1_INPUT_DIR', input_dir)
    if input_template:
        config.set('config', 'DATA_INGEST_1_INPUT_TEMPLATE', input_template)

    config.set('config', 'DATA_INGEST_1_OUTPUT_DIR', out_dir)
    config.set('config', 'DATA_INGEST_1_OUTPUT_TEMPLATE', output_path)
    config.set('config', 'DATA_INGEST_1_USERNAME', 'anonymous')
    config.set('config', 'DATA_INGEST_1_PASSWORD', 'anonymous')
    config.set('config', 'DATA_INGEST_1_SKIP_IF_OUTPUT_EXISTS', skip_if_exists)
    for file_path in expected_files:
        # create file if it should already exist
        if already_exists:
            print(f"Creating file for test: {file_path}")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            Path(file_path).touch()
        # otherwise remove it if it exists
        elif os.path.exists(file_path):
            print(f"Removing file for test: {file_path}")
            os.remove(file_path)

    wrapper = DataIngestWrapper(config)
    if not wrapper.is_ok:
        assert wrapper.is_ok == is_ok
        return

    wrapper.run_all_times()
    assert wrapper.is_ok == is_ok
    if wrapper.is_ok:
        for file_path in expected_files:
            assert os.path.exists(file_path)
