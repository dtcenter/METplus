Testing
=======

Test scripts are found in the GitHub repository in the internal_tests directory.

Unit Tests
----------

Unit tests are run with pytest. They are found in the 'pytests' directory. Each tool has its own sub-directory containing its test files.

run_pytests.sh is a bash script that can be run to execute all of the pytests. A report will be output showing which pytest categories failed.
When running on a new computer, you must create a minimum_pytest.<HOST>.sh file to be able to run the script. This file contains information about the local environment so that the tests can run.

Use Case Tests
--------------

Use case tests are run via a Python script called test_use_cases.py, found in the use_cases directory.
Eventually the running of these tests will be automated using an external tool, such as GitHub Actions or Travis CI.
The script contains a list of use cases that are found in the repository.  For each computer that will run the use cases, a metplus_test_env.<HOST>.sh file must exist to set local configurations.
All of the use cases can be run by executing the script run_test_use_cases.sh. The use case test script will output the results into a directory such as /d1/<USER>/test-use-case-b, defined in the environment file.
If /d1/<USER>/test-use-case-b already exists, its content will be copied over to /d1/<USER>/test-use-case-a. If data is found in If /d1/<USER>/test-use-case-b already exists, its content will be copied over th /d1/<USER>/test-use-case-a, the script will prompt the user to remove those files.
Once the tests have finished running, the output found in the two directories can be compared to see what has changed. Suggested commands to run to compare the output will be shown on the screen after completion of the script.

To see which files and directories are only found in one run::

    diff -r /d1/mccabe/test-use-case-a /d1/mccabe/test-use-case-b | grep Only

