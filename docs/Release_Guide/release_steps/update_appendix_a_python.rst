Update Appendix A METplus Components Python Packages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Update Appendix A METplus Components Python Packages for this release.

.. dropdown:: Instructions

  Often, changes will be made to the versions of the Python package requirements
  or new Python packages will be added across the following METplus components:
  **METplus (including use cases)**, **MET Python Embedding**, **METcalcpy**,
  **METplotpy**, and **METdataio**. Many of the Python packages listed in
  :ref:`components_python_packages` are optional and not required, but ALL packages
  and their version number (if applicable) should be updated.

  The versions of the Python packages should match the versions listed in the
  requirements.txt file at top level of each repository and should include any new
  packages used in new METplus Use Cases.

  .. note::

    This change must be made in the release branch for METplus since
    :ref:`components_python_packages` lives in the METplus
    umbrella repository.
