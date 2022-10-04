Testing
=======

Test scripts are found in the GitHub repository in the internal/tests
directory.

.. _cg-unit-tests:

Unit Tests
----------

Unit tests are run with pytest. They are found in the *pytests* directory.
Each tool has its own subdirectory containing its test files.

Unit tests can be run by running the 'pytest' command from the
internal/tests/pytests directory of the repository.
The 'pytest' Python package must be available.
A report will be output showing which pytest categories failed.
When running on a new computer, a **minimum_pytest.<HOST>.sh**
file must be created to be able to run the script. This file contains
information about the local environment so that the tests can run.

All unit tests must include one of the custom markers listed in the
internal/tests/pytests/pytest.ini file. Some examples include:

    * util
    * wrapper_a
    * wrapper_b
    * wrapper_c
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

    pytest -m <MARKER-NAME>

To run all tests that do not have a given marker, run::

    pytest -m "not <MARKER-NAME>"

Multiple marker groups can be run by using the 'or' keyword::

    pytest -m "<MARKER-NAME1> or <MARKER-NAME2>"


Use Case Tests
--------------

Use case tests are run via a Python script called **test_use_cases.py**,
found in the *use_cases* directory.
Eventually the running of these tests will be automated using an external
tool, such as GitHub Actions or Travis CI.
The script contains a list of use cases that are found in the repository.
For each computer that will run the use cases, a
**metplus_test_env.<HOST>.sh** file must exist to set local configurations.
All of the use cases can be run by executing the script
**run_test_use_cases.sh**. The use case test script will output the results
into a directory such as */d1/<USER>/test-use-case-b*, defined in the
environment file.
If */d1/<USER>/test-use-case-b* already exists, its content will be copied
over to */d1/<USER>/test-use-case-a*. If data is found in
the */d1/<USER>/test-use-case-b* directory  already exists, its content
will be copied
over to the */d1/<USER>/test-use-case-a* directory, the script will prompt
the user to remove those files.
Once the tests have finished running, the output found in the two
directories can be compared to see what has changed. Suggested commands
to run to compare the output will be shown on the screen after completion
of the script.

To see which files and directories are only found in one run::

    diff -r /d1/mccabe/test-use-case-a /d1/mccabe/test-use-case-b | grep Only

