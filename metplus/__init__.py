import os

def get_metplus_version():
    return get_metplus_info('version')

def get_metplus_release_date():
    return get_metplus_info('release_date')

def get_metplus_info(info_type):
    version_file = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                os.pardir,
                                                'docs',
                                                info_type))
    with open(version_file, 'r') as file_handle:
        version = file_handle.read().strip()
        return version

__version__ = get_metplus_version()
__release_date__ = get_metplus_release_date()
