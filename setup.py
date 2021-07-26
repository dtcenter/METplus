from setuptools import setup, find_packages
from distutils.util import convert_path
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("metplus/VERSION", "r") as fh:
    version = fh.read().strip()

with open("metplus/PYTHON_VERSION", "r") as fh:
    python_version = fh.read().strip()

# get list of additional files needed to add to package
data_files = []
# add version and release date files
data_files.append(('metplus',
                  ['metplus/VERSION',
                   'metplus/RELEASE_DATE',
                   'metplus/PYTHON_VERSION',
                  ]))

for root, _, files in os.walk('parm'):
    parm_files = []
    for filename in files:
        filepath = os.path.join(root, filename)
        # skip README, tilda, and pycache files
        if ('__pycache__' in filepath or
                'README' in filepath or
                filepath.endswith('~')):
            continue
        parm_files.append(filepath)
    if parm_files:
        data_files.append((root, parm_files))

setup(
    name="metplus",
    version=version,
    author="METplus",
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
    python_requires=f'>={python_version}',
    data_files=data_files,
    zip_safe=False,
)
