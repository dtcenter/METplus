Update Version Number
^^^^^^^^^^^^^^^^^^^^^

.. note::
   
  The software version number should have been updated for the next official release during development toward the **first development release** (e.g. beta1).
  If not, follow the :ref:`official release instructions <update_version_official>` to do so prior to creating the first development release.
  
* If the official release version has already been updated (e.g. beta2+ and rc1+), do the following:
  
  * In 'docs/conf.py', update the 'version', 'release_year', and 'release_date' variables for the documentation.

  * In the top level file 'build.xml', update the version value for the attribute name 'Specification-Version' under the 'dist' target name.

  * In the 'webapp/metviewer/metviewer1.jsp' file:

    * Update the 'TITLE' version value under 'HEAD'.

    * Update the version value in the :code:`span id="release"` section.
