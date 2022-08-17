Recreate an Existing Release
----------------------------

To recreate an existing development, bugfix, or official release:

* Reopen the corresponding development project from the
  `Developmental Testbed Center organization project page <https://github.com/orgs/dtcenter/projects>`_.
* Make an necessary additions to the existing project.  For example, move
  any newly completed issues and pull requests (e.g. from beta3 back to
  beta2).
* Reopen the GitHub issue for creating the previously created release.
* Delete the existing release from GitHub.
* Delete the existing release tag (e.g. v11.0.0-beta2) from GitHub.  
* Follow the instructions from the
  `Release Guide <https://metplus.readthedocs.io/en/develop/Release_Guide/index.html#instructions-summary>`_,
  being sure to update the release data for the actual release note. Consider
  adding a note in description section for the GitHub release to indicate
  that this release was re-created with an explanation. For example, "NOTE:
  The MET-11.0.0-beta2 development release from 8/3/2022 has been
  recreated to resolve a compilation issue."


