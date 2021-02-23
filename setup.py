from setuptools import setup, find_packages
from distutils.util import convert_path
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("metplus/VERSION", "r") as fh:
    version = fh.read()

# get parm files needed to run
met_config_dir = 'parm/met_config'
metplus_config_dir = 'parm/metplus_config'
met_config_files = [os.path.join(met_config_dir, item) for
                    item in os.listdir(met_config_dir)]
metplus_config_files = [os.path.join(metplus_config_dir, item) for
                        item in os.listdir(metplus_config_dir)]

setup(
    name="metplus",
    version=version,
    author="METplus",
    author_email="met_help@ucar.edu",
    description="METplus Wrappers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dtcenter/METplus",
    packages=find_packages(),
    classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License", 
         "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    data_files=[('metplus', ['metplus/VERSION',
                             'metplus/RELEASE_DATE',
                            ]),
                (met_config_dir, met_config_files),
                (metplus_config_dir, metplus_config_files),
               ],
)
