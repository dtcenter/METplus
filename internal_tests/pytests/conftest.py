import sys
import os
import shlex
import subprocess
import pytest
import getpass
from pathlib import Path

# add METplus directory to path so the wrappers and utilities can be found
metplus_dir = str(Path(__file__).parents[2])
sys.path.insert(0, os.path.abspath(metplus_dir))

from metplus.util import config_metplus

# get host from either METPLUS_PYTEST_HOST or from actual host name
# Look for minimum_pytest.<pytest_host>.sh script to source
# error and exit if not found
pytest_host = os.environ.get('METPLUS_PYTEST_HOST')
if pytest_host is None:
    import socket
    pytest_host = socket.gethostname()
    print(f"No hostname provided with METPLUS_PYTEST_HOST, using {pytest_host}")
else:
    print(f"METPLUS_PYTEST_HOST = {pytest_host}")

minimum_pytest_file = os.path.join(os.path.dirname(__file__),
                                   f'minimum_pytest.{pytest_host}.sh')
if not os.path.exists(minimum_pytest_file):
    print(f"ERROR: minimum_pytest.{pytest_host}.sh file must exist in "
          "pytests directory. Set METPLUS_PYTEST_HOST correctly or "
          "create file to run pytests on this host.")
    sys.exit(4)

# source minimum_pytest.<pytest_host>.sh script
current_user = getpass.getuser()
command = shlex.split(f"env -i bash -c 'export USER={current_user} && source {minimum_pytest_file} && env'")
proc = subprocess.Popen(command, stdout=subprocess.PIPE)

for line in proc.stdout:
    line = line.decode(encoding='utf-8', errors='strict').strip()
    key, value = line.split('=')
    os.environ[key] = value

proc.communicate()

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
