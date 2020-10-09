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
sys.path.insert(0, os.path.abspath('../ush'))
sys.path.append(os.path.abspath("./_ext"))
print(sys.path)


# -- Project information -----------------------------------------------------

project = 'METplus'

author = 'UCAR/NCAR, NOAA, CSU/CIRA, and CU/CIRES'

# the stable version, displayed on front page of PDF
version = '3.1'

# The full version, including alpha/beta/rc tags
release = f'{version}'

release_year = '2020'

release_date = f'{release_year}0810'

copyright = f'{release_year}, {author}'

release_monthyear = datetime.strptime(release_date, '%Y%m%d').strftime('%B %Y')

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
                    ]

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

rst_epilog = """
.. |copyright| replace:: {copyrightstr}
.. |release_date| replace:: {release_datestr}
.. |release_year| replace:: {release_yearstr}
.. |release_monthyear| replace:: {release_monthyearstr}
""".format(copyrightstr=copyright,
           release_datestr=release_date,
           release_yearstr=release_year,
           release_monthyearstr=release_monthyear,
           )
