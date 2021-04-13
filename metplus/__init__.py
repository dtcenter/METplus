import os

def get_metplus_version():
    return get_metplus_info('VERSION')

def get_metplus_release_date():
    return get_metplus_info('RELEASE_DATE')

def get_python_version():
    return get_metplus_info('PYTHON_VERSION')

def get_metplus_info(info_rel_path):
    info_file = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             info_rel_path))
    with open(info_file, 'r') as file_handle:
        info = file_handle.read().strip()
        return info

__version__ = get_metplus_version()
__release_date__ = get_metplus_release_date()

# import util and wrappers
from .util import *
from .wrappers import *
