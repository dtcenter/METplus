.. _codingstandards:

****************
Coding Standards
****************



* Python code style outlined in `PEP8 <https://pep8.org>`_
* Python section of the `NCEP Coding Standards <ftp://ftp.library.noaa.gov/noaa_documents.lib/NWS/NCEP/NCEP_office_notes/NCEP_office_note_492.pdf>`_
* `NCO WCOSS Implementation Standards <https://www.nco.ncep.noaa.gov/idsb/implementation_standards/>`_ for
  directory structure and script naming conventions
* `Doxygen <http://www.doxygen.nl/>`_, `Python
  docstrings <https://www.python.org/dev/peps/pep-0257/>`_, and
  `Sphinx <http://www.sphinx-doc.org/en/master/>`_ for documentation
* **NOTE: Please do not use f-strings in the run_metplus.py file so that the Python version check can notify the user of the incorrect version. Using Python 3.5 or earlier will output the SyntaxError from the f-string instead of the useful error message.**

Python Code Analysis Tools
==========================

Static Tools
------------

pylint
^^^^^^

`pylint <https://pylint.pycqa.org/en/latest/intro.html>`_ is a tool that checks
for errors in Python code, tries to enforce a coding standard and looks for code
smells.

To `install pylint <https://pylint.pycqa.org/en/latest/user_guide/installation.html>`_
the following can be run:

.. code-block:: ini

  pip install pylint

or

.. code-block:: ini

  conda install pylint 


To check for errors as well as PEP-8 style code, run:

.. code-block:: ini

  pylint pep8 <code-to-analyze>

replacing <code-to-analyze> with the name of the file to analyze.


pyflakes
^^^^^^^^

`pyflakes <https://pypi.org/project/pyflakes/>`_ is a simple program which
checks Python source files for errors. Pyflakes analyzes programs and
detects various errors. It works by parsing the source file, not importing
it, so it is safe to use on modules with side effects. It’s also much faster.


To install pyflakes the following can be run:

.. code-block:: ini

  pip install pyflakes

or

.. code-block:: ini

  conda install pyflakes


`flake8 <http://flake8.pycqa.org/en/latest/index.html#quickstart>`_ is wrapper
to pyflakes, performs PEP-8 style checking in addition to error checking.

vulture
^^^^^^^

`vulture <https://pypi.org/project/vulture/>`_ finds unused code in Python
programs and is useful for cleaning up and finding errors in large code bases.
It checks for unused imports, variables, methods, and classes.

To install vulture the following can be run:

.. code-block:: ini

  pip install vulture

or

.. code-block:: ini

  conda install vulture


Dynamic (run-time) Tools
------------------------

Code Coverage Analysis
^^^^^^^^^^^^^^^^^^^^^^

Code coverage analysis tools are useful when running unit tests to determine
whether tests are executing all possible branches, loops, etc.

**Examples:**

`Coverage.py <https://coverage.readthedocs.io/>`_: A free tool for
monitoring the coverage of your Python apps, monitoring every bit of your code
to find what was executed and what was not.

`pytest-cov <https://pypi.org/project/pytest-cov/>`_: A free language plug-in
to produce a coverage report of your app.

`figleaf <https://ctb.github.io/figleaf/doc/>`_: A code coverage analysis
tool intended to be to be a minimal replacement of 'coverage.py' that supports
more configurable coverage gathering and reporting.
