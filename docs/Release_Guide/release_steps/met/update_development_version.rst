Update Development Release Version Number
-----------------------------------------

- Work on a feature branch from the *develop* branch being sure to include the GitHub issue number for the new release (e.g. feature_NNNN_vX.Y.Z-betaN or feature_NNNN_vX.Y-rcN).
- Prior to creating the first development release (e.g. beta1) for a new version, the official release version number should have already been updated.
- If the official release version has not yet been updated (e.g. beta1), follow the official release instructions to do so.
- If the official release version has already been updated (e.g. beta2 and beyond), do the following:
  - Update the *version*, *release_year*, and *release_date* variables in *met/docs/conf.py* which defines the version number for the documentation.
