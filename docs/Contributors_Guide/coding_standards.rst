.. _codingstandards:

****************
Coding Standards
****************

Guidelines
==========

* Python code style outlined in `PEP8 <https://pep8.org>`_
* `Doxygen <https://www.doxygen.nl/>`_, `Python
  docstrings <https://www.python.org/dev/peps/pep-0257/>`_, and
  `Sphinx <https://www.sphinx-doc.org/en/master/>`_ for documentation
* **NOTE: Please do not use f-strings in the run_metplus.py file so that the Python version check can notify the user of the incorrect version. Using Python 3.5 or earlier will output the SyntaxError from the f-string instead of the useful error message.**

Python code analysis tools like **pylint** can be used to check for errors and violations of PEP8 standards.

Python Package Disclaimer
=========================

Any external Python packages used in the METplus components are defined in the
requirements.txt file and, if applicable, nco_requirements.txt file in the top
level of the code repositories. It is important that the METplus components only
require Python packages that are allowed on operational high performance
computers (HPCs). The process of approval for some HPCs can take months and
some packages have been denied.

Where a new Python package is listed depends on where it is used:

  * **METplus wrappers code** (under *metplus/*): add the package to
    requirements.txt and to the :ref:`metplus_components_python_packages`
    table in Appendix A.
  * **A use case** (under *parm/use_cases/model_applications/*): add the
    package to the :ref:`metplus_components_python_packages` table in
    Appendix A, but do **not** add it to requirements.txt. Use cases can
    require packages that the METplus wrappers do not.

Proceed with caution and request approval before starting development with a
new Python package. Some general guidelines to consider when choosing new
potential Python packages are:

  * The package would ideally have a version number of 1 or greater.
  * Ensure that the package is regularly being maintained.
