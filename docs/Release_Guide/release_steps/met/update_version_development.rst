Update Version Number
---------------------

*  Create a feature branch from the *develop* branch being sure to include the GitHub issue number for the new release (e.g. feature_NNNN_vX.Y.Z-betaN or feature_NNNN_vX.Y.Z-rcN).

.. parsed-literal::

    git checkout -b feature_NNNN_vX.Y.Z-betaN
   
* Prior to creating the first development release (e.g. beta1) for a new version, the official release version number should have already been updated.
  
* If the official release version has not yet been updated (e.g. beta1), follow the official release instructions to do so.
  
* If the official release version has already been updated (e.g. beta2 and beyond), do the following:
  
  * In *met/docs/conf.py*, update the *version*, *release_year*, and *release_date* variables for the documentation.
   
  * In *met/docs/version*, update the version string.
