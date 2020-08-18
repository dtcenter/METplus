import os
import pytest

from metplus.util import config_metplus

@pytest.fixture(scope='function')
def metplus_config():
    """! Create a METplus configuration object that can be
    manipulated/modified to
         reflect different paths, directories, values, etc. for individual
         tests.
    """
    def read_configs(extra_configs=[]):
        # Read in minimum pytest config file and any other extra configs
        script_dir = os.path.dirname(__file__)
        minimum_conf = os.path.join(script_dir, 'minimum_pytest.conf')
        args = [minimum_conf]
        if extra_configs:
            args.extend(extra_configs)

        config = config_metplus.setup(args)
        return config

    return read_configs
