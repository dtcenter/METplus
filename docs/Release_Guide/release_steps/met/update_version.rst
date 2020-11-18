Update Version Number for Release
---------------------------------

To update the MET version number, start by writing a GitHub issue to describe the change. Next, create a feature branch from the corresponding *main* branch (e.g. main_vX.Y).

- Details for an official release (e.g. vX.Y)
  - Update the *met_version* variable in *met/src/basic/vx_util/util_constants.h* which defines the version number written to the MET output files.
  - Update the *version* variable in *met/docs/conf.py* which defines the version number for the documentation.
  - Update the version number in the locations listed above.
  - Update the version number listed in the MET configuration files:
    - Default configuration files in *met/data/config*.
    - Sample configuration files in *met/scripts/config*.
    - Test configuration files, searching recursively, in *test/config*.
  - Add a new *met/data/table_files/met_header_columns_VX.Y.txt* defining the columns names for this version.
  - Add a new *test/hdr/met_X_Y.hdr* file defining the column names for this version for the test scripts.

- Details for a bugfix release (e.g. vX.Y.Z)
  - Update the *met_version* variable in *met/src/basic/vx_util/util_constants.h* which defines the version number written to the MET output files.
  - Update the *version* variable in *met/docs/conf.py* defines the version number for the documentation.
  - Do *NOT* update the version number in the configuration files, add a new table file, or add a new test header file.
  
- Details for a development release (e.g. vX.Y-betaN or vX.Y-rcN)
  - Prior to creating the first development release (e.g. beta1) for a new version, the official release version number should have already been updated.
  - If the official release version has not yet been updated (e.g. beta1), follow the official release instructions to do so.
  - If the official release version has already been updated (e.g. beta2 and beyond), do the following:
    - Update the *version* variable in *met/docs/conf.py* which defines the version number for the documentation.
