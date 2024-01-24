Update Release Notes
^^^^^^^^^^^^^^^^^^^^

You can refer to the GitHub Project board to see what has changed for this
release. Open the following URL in a browser:

.. parsed-literal::

    https://github.com/orgs/dtcenter/projects

* Click on the project that corresponds to support for the release, i.e.
  METplus Version X.Y Support

* Navigate to the "Closed Issues" tab. If this tab does not exist,
  see :ref:`wo-support-project` to create it.

* Find the closed issues with dtcenter/|projectRepo| in the Repository column
  that have been added since the last bugfix release for |projectRepo|.

* Open the following URL in a browser:

.. parsed-literal::

    https://github.com/dtcenter/|projectRepo|/issues

* Navigate to the |projectRepo| X.Y.Z Milestone to check for any issues
  that may not appear in the METplus Version X.Y Support project board.

* Update the release-notes.rst file found in the User's Guide directory.

* Consider organizing release notes into logical groups
  (e.g. Enhancements, Bugfixes, Documentation, etc.) and modifying
  GitHub issue titles for consistency. The release notes should match
  the GitHub issue titles, when possible.
  
* Use your best judgement to apply bold formatting for any major or important changes.

* When creating a bugfix release, leave the "Version X.Y.0 release notes
  (YYYYMMDD)" in place, along with any other bugfix release notes and
  add a section above for the latest bugfix release (i.e. "Version X.Y.Z
  release notes (YYYYMMDD)").
  
* Commit changes and push to GitHub.
