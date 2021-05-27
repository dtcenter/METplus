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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                os.pardir)))
sys.path.append(os.path.abspath("./_ext"))
print(sys.path)

from metplus import __version__, __release_date__

# -- Project information -----------------------------------------------------

project = 'METplus'

author = 'UCAR/NCAR, NOAA, CSU/CIRA, and CU/CIRES'

# list of contributing authors currently involved with the project
# rotate this list of authors for each release
CURRENT_AUTHORS = [
    'Minna Win-Gildenmeister',
    'George McCabe',
    'Julie Prestopnik',
    'John Opatz',
    'John Halley Gotway',
    'Tara Jensen',
    'Jonathan Vigh',
    'Mallory Row',
    'Christina Kalb',
    'Hank Fisher',
    'Lisa Goodrich',
    'Dan Adriaansen',
]

# list of former contributors who are no longer involved with the project
# but still deserve citation credit
FORMER_AUTHORS = [
    'James Frimel',
    'Lindsay Blank',
    'Todd Arbetter',
]

# format citation authors list
formatted_authors = []
for index, author in enumerate(CURRENT_AUTHORS + FORMER_AUTHORS):
    first_name, last_name = author.split(' ', 1)
    first_initial = first_name[0]
    #  first name uses "Last Name, First Initial"
    if index == 0:
        formatted_name = f'{last_name}, {first_initial}.'
    #  the rest uses "First Initial Last Name"
    else:
        formatted_name = f'{first_initial}. {last_name}'
    formatted_authors.append(formatted_name)

# compile string from list of current and former authors separated by comma
author_list = ', '.join(formatted_authors)

# The full version, including alpha/beta/rc tags
# i.e. 4.0.0-beta1-dev
release = __version__

# the stable version, displayed on front page of PDF extract X.Y.Z version
# from release by splitting the string into a list
# using - as the delimeter, then getting the 1st item of the list
# if version is beta, rc, and/or dev then set version to develop for
# the documentation built for develop (not release)
if len(release.split('-')) > 1:
    version = 'develop'
else:
    version = release

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

# document that contains the root toctree directive
root_doc = 'index'
master_doc = 'index'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.intersphinx',
              'sphinx_gallery.gen_gallery',
             ]

# settings for ReadTheDocs PDF creation
latex_engine = 'pdflatex'
latex_theme = 'manual'
latex_logo = os.path.join('_static','METplus_logo.png')
latex_show_pagerefs = True
latex_master_doc = 'Users_Guide/index'

latex_elements = {
   # The paper size ('letterpaper' or 'a4paper').
   #
   'papersize': 'letterpaper',
   'releasename':"{version}",
   'fncychap': '\\usepackage{fncychap}',
   'fontpkg': '\\usepackage{amsmath,amsfonts,amssymb,amsthm}',
                                                     
   'figure_align':'htbp',
   'pointsize': '11pt',
                                        
   'preamble': r'''
       \usepackage{charter}
       \usepackage[defaultsans]{lato}
       \usepackage{inconsolata}
       \setcounter{secnumdepth}{4}
       \setcounter{tocdepth}{4}
    ''',
                                                                            
    'sphinxsetup': \
        'hmargin={0.7in,0.7in}, vmargin={1in,1in}, \
        verbatimwithframe=true, \
        TitleColor={rgb}{0,0,0}, \
        HeaderFamily=\\rmfamily\\bfseries, \
        InnerLinkColor={rgb}{0,0,1}, \
        OuterLinkColor={rgb}{0,0,1}',
        'maketitle': '\\sphinxmaketitle',  
#        'tableofcontents': ' ',
        'printindex': ' '
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (latex_master_doc, 
     'users_guide.tex', 
     'METplus User\'s Guide',
     ' ', 
     'manual')
]
    
# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build',
                    'Thumbs.db',
                    '.DS_Store',
                    'use_cases',
                    'Release_Guide/release_steps',
                    'Verification_Datasets/datasets/template.rst',
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
.. |copyright|    replace:: {copyright}
.. |author_list|  replace:: {author_list}
.. |release_date| replace:: {release_date}
.. |release_year| replace:: {release_year}
.. |release_info| replace:: {release_info}
"""
