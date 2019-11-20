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
import sys
sys.path.insert(0, os.path.abspath('../ush'))
sys.path.append(os.path.abspath("./_ext"))
print(sys.path)


# -- Project information -----------------------------------------------------

project = 'METplus'
copyright = '2019, NCAR'
author = 'NCAR'

# The full version, including alpha/beta/rc tags
release = '3.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
#extensions = ['sphinx.ext.autodoc','sphinx_gallery.gen_gallery','sphinx.ext.intersphinx']
extensions = ['sphinx.ext.autodoc','sphinx.ext.intersphinx','sphinx_gallery.gen_gallery']
#extensions = ['sphinx.ext.autodoc','sphinx_gallery.gen_gallery']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'Users_Guide/METplus_*.rst']

# Suppress certain warning messages
suppress_warnings = ['ref.citation']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
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
      'examples_dirs': ['../parm/use_cases/template','../parm/use_cases/met_tool_wrapper','../parm/use_cases/model_applications'],
      'gallery_dirs': ['Users_Guide/template','Users_Guide/met_tool_wrapper','Users_Guide/model_applications'],
      'default_thumb_file'     : '_static/METplus_logo.png',
      'download_all_examples' : False,
      'log_level' : {'debug','info','warning','backreference_missing','error'},
      'filename_pattern' : '.py',
      'backreferences_dir': 'gen_modules/backreferences'
}

# -- Intersphinx control ---------------------------------------------------------------
intersphinx_mapping = {'numpy':("https://docs.scipy.org/doc/numpy/", None)}
