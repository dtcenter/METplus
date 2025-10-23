Update Version Number
^^^^^^^^^^^^^^^^^^^^^

Update the software version information. Remove **-dev** from the version number.

.. dropdown:: Instructions

  * In 'metplotpy/_version.py', update the version number.

    * The version should match the upcoming release with -dev added to the end like X.Y.Z-betaN-dev, i.e. 4.0.0-beta1-dev

    * Remove the '-dev' suffix and ensure that the version number is correct.

  * In 'docs/conf.py', update the 'release_year' and 'release_date' variables.
