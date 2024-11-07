Add Next Version to Lookup Table
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the develop branch, modify the **metplus/component_versions.py** file to
add an entry for the next coordinated release.

If the X.0 release was just created, add an entry for the X.1 release.

If the X.1 release was just created, add an entry for the X+1.0 release.

Set the appropriate X.Y.0 versions for each component.
Maybe sure to set the Z number to 0.

Set the version for metexpress to None (not a string).

For example, if the coordinated 6.0 release was just created, add::

    '6.1': {
        'metplus': '6.1.0',
        'met': '12.1.0',
        'metplotpy': '3.1.0',
        'metcalcpy': '3.1.0',
        'metdataio': '3.1.0',
        'metviewer': '6.1.0',
        'metexpress': None,
    },

For example, if the coordinated 6.1 release was just created, add::

    '7.0': {
        'metplus': '7.0.0',
        'met': '13.0.0',
        'metplotpy': '4.0.0',
        'metcalcpy': '4.0.0',
        'metdataio': '4.0.0',
        'metviewer': '7.0.0',
        'metexpress': None,
    },
