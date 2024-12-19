Update Version on Develop Branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Update the development version information.

.. dropdown:: Instructions

  Change |projectRepo|/docs/version value to the next release after this one with -dev added
  to the end. Releases will loosely follow these names, but are subject to change:

  +-------------------+----------------------------+
  | Release Version   | New Develop Version        |
  +===================+============================+
  |    X.Y.Z-beta1    |    X.Y.Z-beta2-dev         |
  +-------------------+----------------------------+
  |    X.Y.Z-beta2    |    X.Y.Z-beta3-dev         |
  +-------------------+----------------------------+
  |    X.Y.Z-beta3    |    X.Y.Z-rc1-dev           |
  +-------------------+----------------------------+
  |    X.Y.Z-rc1      |   (X+1).0.0-beta1-dev OR   |
  |                   |    **X.(Y+1).0-beta1-dev** |
  +-------------------+----------------------------+
