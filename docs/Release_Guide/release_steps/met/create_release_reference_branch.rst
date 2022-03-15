Create Release Reference Branch
-------------------------------

* Create a branch from the develop branch for the reference branch for the
  new official release and push it to GitHub. The branch name should match
  the format main_vX.Y-ref where X.Y is the major/minor release number.

.. parsed-literal::

    cd |projectRepo|
    git checkout develop
    git pull
    git checkout -b main_vX.Y-ref

Push reference branch to GitHub
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    git push -u origin main_vX.Y-ref

Pushing this branch to GitHub should trigger the GitHub Actions automation
that runs all of the use cases and creates Docker data volumes with the output
data. These data will be used to verify that any bugfixes applied to the
main_vX.Y branch does not break any of existing logic.

Monitor GitHub Actions Workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Navigate to https://github.com/dtcenter/MET/actions and verify that a
*Testing* workflow was triggered on the *main_vX.Y-ref* branch.

* Wait until the entire workflow has run successfully. The final job entitled
  "Create Output Docker Data Volumes" should create Docker data volumes for
  each use case category on DockerHub (dtcenter/met-dev).
