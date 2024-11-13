Update Version Number
^^^^^^^^^^^^^^^^^^^^^

.. note::
   
  The software version number should have been updated for the next official release during development toward the **first development release** (e.g. beta1).
  If not, follow the :ref:`official release instructions <update_version_official>` to do so prior to creating the first development release.
  
* If the official release version has already been updated (e.g. beta2+ and rc1+), do the following:
  
  * In 'docs/conf.py', update the 'version', 'release_year', and 'release_date' variables for the documentation.

  * In 'docs/version', update the version number. This value is used by METplus use cases that run METdbLoad and is used by METviewer.

  * In the top level 'pyproject.toml', update the value of 'version'.
