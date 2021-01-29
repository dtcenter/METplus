Update Version Number
---------------------

*  Create a feature branch from the *develop* branch being sure to include the GitHub issue number for the new release (e.g. feature_NNNN_vX.Y.Z).

.. parsed-literal::

    git checkout -b feature_NNNN_vX.Y.Z
  
* Update the version in the code and documentation:
  
  * If necessary, update the *met_version* variable in *met/src/basic/vx_util/util_constants.h* which defines the version number written to the MET output files.

  * In *met/docs/conf.py*, update the *version*, *release_year*, and *release_date* variables for the documentation.
   
  * In *met/docs/version*, update the version string.
  
  * If necessary, update the version number listed in the MET configuration files:

    * Default configuration files in *met/data/config*.

    * Sample configuration files in *met/scripts/config*.

    * Test configuration files, searching recursively, in *test/config*.

  * If necessary, add a new *met/data/table_files/met_header_columns_VX.Y.txt* defining the columns names for this version.

  * If necessary, add a new *test/hdr/met_X_Y.hdr* file defining the column names for this version for the test scripts.
