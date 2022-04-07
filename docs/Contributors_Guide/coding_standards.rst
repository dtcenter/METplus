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

Python code analysis tools
==========================

Static:
-------

pylint
^^^^^^

::
   
    pip install pylint or conda install pylint

    pylint.org

    checks for code errors

    pylint pep8 code-to-analyze will check for errors as well as PEP-8 style code

pyflakes
^^^^^^^^

::

    pip install pyflakes or conda install pyflakes

    parses code rather than importing code, therefore OK to use on modules with side-effects

    checks for code errors

    faster than pylint

    https://pypi.python.org/pypi/pyflakes

    flake8 is wrapper to pyflakes, performs PEP-8 style checking in addition to error checking
        http://flake8.pycqa.org/en/latest/index.html#quickstart

vulture
^^^^^^^

::

    checks for unused imports, variables, methods, classed ie "dead code"

    pip install vulture or conda install vulture

    https://pypi.python.org/pypi/vulture

Dynamic (run-time):
-------------------

cpde-coverage analysis
^^^^^^^^^^^^^^^^^^^^^^

Useful when running unit tests to determine whether tests are executing all possible branches, loops, etc.

figleaf
^^^^^^^

http://darcs.idyll.org/~t/projects/figleaf/doc/
Checking for God objects and God methods:

(from Chapter 4 of "How to Make Mistakes in Python", Mike Pirnat)

::

    find . -name "*.py" -exec wc -l {} \; | sort -g -r
        for all Python source files, order by size
        anything over 1000 lines is worth investigating (as general rule of thumb)

    grep "^class " mybigmodule.py |wc -l
        counts the number of classes defined in mybigmodule.py

    grep "\sdef " mybigmodule.py |wc -l

        counts the number of methods defined within a class or other function (ie at some level of indentation) in mybigmodule.py

        try this if the above doesn't work: grep "def " mybigmodule.py |wc -l

    A high ratio of methods to classes warrants investigation (what constitutes a high ratio- 10:1, 5:1???)
