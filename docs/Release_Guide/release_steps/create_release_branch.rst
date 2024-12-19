Create Release Branch
^^^^^^^^^^^^^^^^^^^^^

For rc1 development releases, create a new main branch for the upcoming official release.

.. dropdown:: If creating an rc1 release

  * Create a new 'main_vX.Y' branch from the develop branch for the upcoming
    official release and push it to GitHub. All remaining development for the
    upcoming official release occurs on this new 'main_vX.Y' branch.

  .. parsed-literal::

      cd |projectRepo|
      git checkout develop
      git pull
      git checkout -b main_vX.Y
      git push -u origin main_vX.Y
