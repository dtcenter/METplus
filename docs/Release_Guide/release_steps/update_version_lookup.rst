Update Version Lookup Table
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Modify the version lookup table in the METplus repository to include the
correct version.

.. dropdown:: Instructions

  * Clone the METplus repository.

    Using SSH:

    .. parsed-literal::

        git clone git@github.com:dtcenter/METplus

    Using HTTP:

    .. parsed-literal::

        git clone https://github.com/dtcenter/METplus

  * Enter the METplus repository directory:

  .. parsed-literal::

      cd METplus

  * Checkout the develop branch

  .. parsed-literal::

      git checkout develop

  * Create a branch off of develop to update.
    Include the name of the repository and version in the name.

  .. parsed-literal::

      git checkout -b update_version_vX.Y.Z_repo

  * Open **metplus/component_versions.py** and increment the version for the
    appropriate |projectRepo| entry.

  * Commit change, push to GitHub, and create a pull request to merge change
    into the **develop** branch.
