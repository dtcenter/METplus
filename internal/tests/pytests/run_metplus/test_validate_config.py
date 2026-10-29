#!/usr/bin/env python3

import pytest
from unittest import mock

from pathlib import Path
import importlib.util
import sys
import os

# get METplus directory relative to this file
# from this script's directory, go up 4 directories
METPLUS_DIR = str(Path(__file__).parents[4])
USH_DIR = os.path.join(METPLUS_DIR, 'ush')
VALIDATE_CONFIG = os.path.join(USH_DIR, 'validate_config.py')


def import_validate_config():
    # validate_config.py imports run_metplus from the ush directory
    if USH_DIR not in sys.path:
        sys.path.insert(0, USH_DIR)
    spec = importlib.util.spec_from_file_location('validate_config',
                                                  VALIDATE_CONFIG)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    'config, is_ok, sed_commands, expected_result', [
        # config could not be parsed
        (None, None, None, False),
        # validation passed
        ('config', True, [], True),
        # validation failed without suggested changes
        ('config', False, [], False),
        # validation failed with suggested changes
        ('config', False, ['sed -i s/A/B/g file.conf'], False),
    ]
)
@pytest.mark.run_metplus
def test_validate_config_main(config, is_ok, sed_commands, expected_result):
    """! Check that main returns False if the configuration fails validation
    so that the script exits with a non-zero return code
    """
    validate_config = import_validate_config()
    with mock.patch.object(validate_config,
                           'get_config_inputs_from_command_line',
                           return_value=[]), \
         mock.patch.object(validate_config.config_metplus, 'setup',
                           return_value=config), \
         mock.patch.object(validate_config, 'validate_config_variables',
                           return_value=(is_ok, sed_commands)), \
         mock.patch.object(validate_config,
                           '_prompt_sed_commands') as mock_prompt:
        assert validate_config.main() == expected_result

    if config and not is_ok:
        mock_prompt.assert_called_once_with(sed_commands)
    else:
        mock_prompt.assert_not_called()
