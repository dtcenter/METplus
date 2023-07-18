Testing
=======

Test scripts are found in the GitHub repository in the internal/tests
directory.

.. _cg-unit-tests:

Unit Tests
----------

Unit tests are run with pytest.
They are found in the *internal/tests/pytests* directory under the *wrappers*
and *util* directories.
Each tool has its own subdirectory containing its test files.

Pytest Requirements
^^^^^^^^^^^^^^^^^^^

The following Python packages are required to run the tests.

* **pytest**: Runs the tests
* **python-dateutil**: Required to run METplus wrappers
* **netCDF4**: Required for some METplus wrapper functionality
* **pillow**: Only used if running diff utility tests
* **pdf2image**: Only used if running diff utility tests

Running
^^^^^^^

To run the unit tests, set the environment variable
**METPLUS_TEST_OUTPUT_BASE** to a path where the user running has write
permissions, nativate to the METplus directory, then call pytest::

    export METPLUS_TEST_OUTPUT_BASE=/d1/personal/${USER}/pytest
    cd METplus
    pytest internal/tests/pytests

To view verbose test output, add the **-vv** argument::

    pytest internal/tests/pytests -vv

Code Coverage
^^^^^^^^^^^^^

If the *pytest-cov* Python package is installed, the code coverage report can
be generated from the tests by running::

    pytest internal/tests/pytests --cov=metplus --cov-report=term-missing

A report will be output showing which pytest categories failed.

Subsetting Tests by Directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A subset of the unit tests can be run by adjusting the path.
Be sure to include the *--cov-append* argument so the results of the run
are appended to the full code coverage results.
To run only the GridStat unit tests::

    pytest internal/tests/pytests/wrappers/grid_stat --cov=metplus --cov-report=term-missing --cov-append


Subsetting Tests by Marker
^^^^^^^^^^^^^^^^^^^^^^^^^^
Unit tests can include one of the custom markers listed in the
internal/tests/pytests/pytest.ini file. Some examples include:

    * diff
    * run_metplus
    * util
    * wrapper_a
    * wrapper_b
    * wrapper_c
    * wrapper_d
    * wrapper
    * long
    * plotting

To apply a marker to a unit test function, add the following on the line before
the function definition::

    @pytest.mark.<MARKER-NAME>

where <MARKER-NAME> is one of the custom marker strings listed in pytest.ini.

New pytest markers should be added to the pytest.ini file with a brief
description. If they are not added to the markers list, then a warning will
be output when running the tests.

There are many unit tests for METplus and false failures can occur if all of
the are attempted to run at once.
To run only tests with a given marker, run::

    pytest internal/tests/pytests -m <MARKER-NAME>

To run all tests that do not have a given marker, run::

    pytest internal/tests/pytests -m "not <MARKER-NAME>"

For example, if you are running on a system that does not have the additional
dependencies required to run the diff utility tests, you can run all of the
tests except those by running::

    pytest internal/tests/pytests -m "not diff"

Multiple marker groups can be run by using the 'or' keyword::

    pytest internal/tests/pytests -m "<MARKER-NAME1> or <MARKER-NAME2>"

Writing Unit Tests
^^^^^^^^^^^^^^^^^^

metplus_config fixture
""""""""""""""""""""""

Many unit tests utilize a pytest fixture named **metplus_config**.
This is defined in the conftest.py file in internal/tests/pytests.
This is used to create a METplusConfig object that contains the minimum
configurations needed to run METplus, like **OUTPUT_BASE**.
Using this fixture in a pytest will initialize the METplusConfig object to use
in the tests.

This also creates a unique output directory for each test where
logs and output files are written. This directory is created under
**$METPLUS_TEST_OUTPUT_BASE**/test_output and is named with the run ID.
If the test passes, then the output directory is automatically removed.
If the test fails, the output directory will not be removed so the content
can be reviewed to debug the issue.

To use it, add **metplus_config** as an argument to the test function::

    def test_something(metplus_config)

then set a variable called **config** using the fixture name::

    config = metplus_config

Additional configuration variables can be set by using the set method::

    config.set('config', key, value)
