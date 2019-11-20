Run the test as follows:

1) cd to METplus/internal_tests/pytests/extract_tiles

2) run the following from the command line:

pytest -c <path/to>/extract_tiles_test.conf -c <path/to>/custom.conf

IMPORTANT

Before you run the test, make sure to update the PROJ_DIR and the METPLUS_BASE (in the custom.conf file) 

to establish the location of the output directory.
