from setuptools import setup, find_packages
from distutils.util import convert_path
from metplus import get_metplus_version

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="metplus",
    version=get_metplus_version(),
    author="METplus",
    author_email="met-help@ucar.edu",
    description="METplus wrappers",
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
)
