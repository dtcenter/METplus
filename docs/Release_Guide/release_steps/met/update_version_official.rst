.. _update_version_official:

Update Version Number
^^^^^^^^^^^^^^^^^^^^^
  
* Update the version in the code and documentation:
  
  * If necessary, update the *met_version* variable in *src/basic/vx_util/util_constants.h* which defines the version number written to the MET output files.

  * In *docs/conf.py*, update the *version*, *release_year*, and *release_date* variables for the documentation.

  * In *docs/Users_Guide/installation.rst*, search for the X.Y version, replacing the current X.Y version with the official X.Y version, if necessary. Pay particular attention to the "Note" about the C++ standard and modify if necessary.  The X.Y version number in the "Note" box should NOT change unless the default C++ standard changes.
   
  * If necessary, update the version number listed in the MET configuration files:

    * Default configuration files in *data/config*.

    * Sample configuration files in *scripts/config*.

    * Test configuration files, searching recursively, in *internal/test_unit/config*.

  * If necessary, add a new *data/table_files/met_header_columns_VX.Y.txt* defining the columns names for this version.

  * If necessary, add a new *internal/test_unit/hdr/met_X_Y.hdr* file defining the column names for this version for the test scripts.
