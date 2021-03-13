# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
from datetime import datetime
import sys
import shlex
import shutil
import subprocess
import re
import importlib.util

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                os.pardir)))
sys.path.append(os.path.abspath("./_ext"))
print(sys.path)

from metplus import __version__, __release_date__

# docs directory                                                                                                                                                   
# docs_dir will be set to the directory that this script is in                                                                                                     
# __file__ is a variable that contains the path to the module that is                                                                                              
# currently being imported                                                                                                                                         
docs_dir = os.path.abspath(os.path.dirname(__file__))
package_dir = os.path.join(docs_dir,
                           os.pardir,
                           'metplus')

# -- run_command -----------------------------------------------------

def run_command(command, dir_to_run=None):
    log_text = f"Running {command}"
    if dir_to_run:
        log_text += f" under {dir_to_run}"

    command_out = subprocess.run(shlex.split(command),
                                 cwd=dir_to_run)
    if command_out.returncode != 0:
        error_text = f"Command failed: {command}"
        if dir_to_run:
            error_text += f" (in {dir_to_run})"
        print(error_text)

# -- Doxygen ---------------------------------------------------------------                                                                                           

# Skip doxygen if skip_doxygen is set to 1                                                                                                                            
skip_doxygen = 0
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'


if not skip_doxygen:
    # directory where doxygen Makefile exists                                                                                                                         
    doxygen_dir = os.path.join(docs_dir,
                               'doxygen',
                               'run')

    # build the doxygen documentation                                                                                                                                 
    if on_rtd:
        os.chdir(doxygen_dir)
        from subprocess import call 
        call('doxygen')
        del call
        os.chdir(docs_dir)
    else: 
        run_command("make clean all",                                                                                                                                                     doxygen_dir)                                                                                                                                      

    # copy doxygen documentation into _build/html/doxygen                                                                                                             
    doxygen_generated = os.path.join(docs_dir,
                                     'generated',
                                     'doxygen',
                                     'html')
    doxygen_output = os.path.join(docs_dir,
                                  '_build',
                                  'html',
                                  'doxygen')

    # make doxygen output dir if it does not exist                                                                                                                    
    if os.path.exists(doxygen_output):
        print(f"Removing {doxygen_output}")
        os.rmtree(doxygen_output)

    print(f"Copying doxygen files from {doxygen_generated} to {doxygen_output}")
    shutil.copytree(doxygen_generated, doxygen_output)


# -- Project information -----------------------------------------------------

project = 'METplus'

author = 'UCAR/NCAR, NOAA, CSU/CIRA, and CU/CIRES'

# The full version, including alpha/beta/rc tags
# i.e. 4.0.0-beta1-dev
release = __version__

# the stable version, displayed on front page of PDF extract X.Y version
# from release by splitting the string into a list
# using - as the delimeter, then getting the 1st item of the list
# if version is beta, rc, and/or dev then set version to develop for
# the documentation built for develop (not release)
if len(release.split('-')) > 1:
    version = 'develop'
else:
    version = f"{release.split('-')[0]}"

verinfo = version

release_date = __release_date__

release_year = release_date[0:4]

copyright = f'{release_year}, {author}'

release_monthyear = datetime.strptime(release_date, '%Y%m%d').strftime('%B %Y')

if version == 'develop':
  release_info = 'development version'
else:
  release_info = f'{release} release ({release_monthyear})'

# if set, adds "Last updated on " followed by
# the date in the specified format
html_last_updated_fmt = '%c'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.intersphinx',
              'sphinx_gallery.gen_gallery',
             ]

# To enable PDF generation, set METPLUS_DOC_PDF environment variable
#  sphinx 2.4.2+ and rst2pdf packages are required
if os.environ.get('METPLUS_DOC_PDF'):
    extensions.append('rst2pdf.pdfbuilder')

# used for generating PDF
pdf_documents = [('index',
                  f'METplus_Users_Guide_v{version}',
                  'METplus User\'s Guide',
                  ('George McCabe\\'
                   'Dan Adriaansen\\'
                   'Minna Win-Gildenmeister\\'
                   'Julie Prestopnik\\'
                   'Jim Frimel\\'
                   'John Opatz\\'
                   'John Halley Gotway\\'
                   'Tara Jensen\\'
                   'Jonathan Vigh\\'
                   'Mallory Row\\'
                   'Christana Kalb\\'
                   'Hank Fisher\\'
                   'Lisa Goodrich\\'
                   'Lindsay Blank\\'
                   'Todd Arbetter\\'
                   )),]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build',
                    'Thumbs.db',
                    '.DS_Store',
                    'Users_Guide/METplus_*.rst',
                    'use_cases',
                    'Release_Guide/release_steps',
                    'Verification_Datasets/datasets/template.rst',
                    'Contributors_Guide/continuous_integration.rst',
                    ]

# Suppress certain warning messages
suppress_warnings = ['ref.citation']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
html_theme_path = ["_themes", ]
html_js_files = ['pop_ver.js']
html_theme_options = {'canonical_url': 'https://dtcenter.github.io/METplus/latest/'}
html_theme_options['versions'] = {'latest': '../latest', 'develop': '../develop'}
html_css_files = ['theme_override.css']

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = os.path.join('_static','METplus_logo.png')

# -- Sphinx Gallery control -----------------------------------------------------------
sphinx_gallery_conf = {
      'examples_dirs': ['use_cases/met_tool_wrapper',
                        'use_cases/model_applications'],
      'gallery_dirs': ['generated/met_tool_wrapper',
                       'generated/model_applications'],
      'default_thumb_file': '_static/METplus_logo.png',
      'log_level': {'backreference_missing': 'warning'},
      'backreferences_dir': 'generated/gen_modules/backreferences',
      'remove_config_comments': True,
}

# -- Intersphinx control ---------------------------------------------------------------
intersphinx_mapping = {'numpy':("https://docs.scipy.org/doc/numpy/", None)}

rst_epilog = f"""
.. |copyright| replace:: {copyright}
.. |release_date| replace:: {release_date}
.. |release_year| replace:: {release_year}
.. |release_info| replace:: {release_info}
"""

