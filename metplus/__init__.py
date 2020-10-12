import os

def get_metplus_version():
    version_file = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                os.pardir,
                                                'docs',
                                                'version'))
    with open(version_file, 'r') as file_handle:
        version = file_handle.read().strip()
        return version

__version__ = get_metplus_version()
