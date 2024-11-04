Create Release Branch
^^^^^^^^^^^^^^^^^^^^^

.. note::

  These instructions only apply when creating the **first release candidate**
  (rc1) development release. Skip this section for earlier beta (betaN) or later 
  release candidate (rc2+) development releases.


* Create a new 'main_vX.Y' branch from the develop branch for the upcoming
  official release and push it to GitHub. All remaining development for the
  upcoming official release occurs on this new 'main_vX.Y' branch.

.. parsed-literal::

    cd |projectRepo|
    git checkout develop
    git pull
    git checkout -b main_vX.Y
    git push -u origin main_vX.Y

