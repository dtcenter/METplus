Update Bugfix Release Version Number
------------------------------------

- Create and work on a feature branch from the corresponding *main* branch (e.g. main_vX.Y) being sure to include the GitHub issue number for the new release (e.g. feature_NNNN_vX.Y.Z).
- Update the *met_version* variable in *met/src/basic/vx_util/util_constants.h* which defines the version number written to the MET output files.
- Update the *version*, *release_year*, and *release_date* variables in *met/docs/conf.py* which defines the version number for the documentation.
- Do *NOT* update the version number in the configuration files, add a new table file, or add a new test header file.
