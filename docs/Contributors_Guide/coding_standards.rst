.. _codingstandards:

Coding Standards
================



* Python code style outlined in `PEP8 <https://pep8.org>`_
* Python section of the `NCEP Coding Standards <ftp://ftp.library.noaa.gov/noaa_documents.lib/NWS/NCEP/NCEP_office_notes/NCEP_office_note_492.pdf>`_
* `NCO WCOSS Implementation Standards <https://www.nco.ncep.noaa.gov/idsb/implementation_standards/>`_ for
  directory structure and script naming conventions
* `Doxygen <http://www.doxygen.nl/>`_, `Python
  docstrings <https://www.python.org/dev/peps/pep-0257/>`_, and
  `Sphinx <http://www.sphinx-doc.org/en/master/>`_ for documentation
* **NOTE: Please do not use f-strings in the master_metplus.py file so that the Python version check can notify the user of the incorrect version. Using Python 3.5 or earlier will output the SyntaxError from the f-string instead of the useful error message.**
