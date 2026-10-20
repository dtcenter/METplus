Add Next Version to Lookup Table
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Update the latest official release variable.

.. dropdown:: Instructions

  In the develop branch, modify the **metplus/component_versions.py** file to
  update the value for **LATEST_OFFICIAL_RELEASE** to reflect this X.Y release.

  If the 13.0.0 release was just created, set the value to *13.0*.

Add version information for the next coordinated release.

.. dropdown:: Instructions

  In the develop branch, modify the **metplus/component_versions.py** file to
  add an entry for the next planned X.Y coordinated release if it has not
  already been added.

  All METplus components, including METbaseimage, use consistent version
  numbers. Set each component to the same X.Y.0 version as the coordinated
  release. Make sure to set the Z number to 0.

  Set the version for metexpress to None (not a string).

  For example, if the coordinated 13.0 release was just created and the next
  planned release is 13.1, add::

      '13.1': {
          'metplus': '13.1.0',
          'met': '13.1.0',
          'metplotpy': '13.1.0',
          'metcalcpy': '13.1.0',
          'metdataio': '13.1.0',
          'metviewer': '13.1.0',
          'metexpress': None,
          'metbaseimage': '13.1.0',
      },
