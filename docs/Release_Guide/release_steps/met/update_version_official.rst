Update Official Release Version Number
--------------------------------------

- Create and work on a feature branch from the *develop* branch being sure to include the GitHub issue number for the new release (e.g. feature_NNNN_vX.Y).
- Update the *met_version* variable in *met/src/basic/vx_util/util_constants.h* which defines the version number written to the MET output files.
- Update the *version*, *release_year*, and *release_date* variables in *met/docs/conf.py* which defines the version number for the documentation.
- Update the version number in the locations listed above.
- Update the version number listed in the MET configuration files:
  - Default configuration files in *met/data/config*.
  - Sample configuration files in *met/scripts/config*.
  - Test configuration files, searching recursively, in *test/config*.
- Add a new *met/data/table_files/met_header_columns_VX.Y.txt* defining the columns names for this version.
- Add a new *test/hdr/met_X_Y.hdr* file defining the column names for this version for the test scripts.
