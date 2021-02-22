Update Version Number
---------------------

*  Create a feature branch from the corresponding *main* branch (e.g. main_vX.Y) being sure to include the GitHub issue number for the new release (e.g. feature_NNNN_vX.Y.Z).

.. parsed-literal::

    git checkout -b feature_NNNN_vX.Y.Z

* Update the version in the code and documentation:

  * Update the *met_version* variable in *met/src/basic/vx_util/util_constants.h* which defines the version number written to the MET output files.

  * In *met/docs/conf.py*, update the *version*, *release_year*, and *release_date* variables for the documentation.
 
  * In *met/docs/version*, update the version string.

  * DO NOT update the version number listed in the MET configuration files, add a new table file, or add a new test header file.
