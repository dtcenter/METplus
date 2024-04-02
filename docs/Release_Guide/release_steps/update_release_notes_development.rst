Update Release Notes
^^^^^^^^^^^^^^^^^^^^

You can refer to the GitHub Project board to see what has changed for this
release. Open the following URL in a browser:

.. parsed-literal::

    https://github.com/orgs/dtcenter/projects

* Click on the project that corresponds to this release, i.e.
  |projectRepo|-X.Y.Z Development

* Navigate to the "Closed Issues" tab. If this tab does not exist,
  see :ref:`wo-development-project` to create it.

* Update the release-notes.rst file found in the User's Guide directory.

* Consider organizing release notes into logical groups
  (e.g. Enhancements, Bugfixes, Documentation, etc.) and modifying
  GitHub issue titles for consistency. The release notes should match
  the GitHub issue titles, when possible.

* Use your best judgement to apply bold formatting for any major or important changes.

* If you are creating a beta1 release, remove the previous version's release
  notes, i.e. for 3.0.0-beta1, remove all 2.Y.Z notes and start a 3.0.0
  section with the format "Version X.Y.Z release notes (YYYYMMDD)".

* If you are creating a betaX release, add a new betaX section above the betaX-1
  release.

* For the METplus repository, update the **development timeline**.

  * If your are creating a beta1 release, add development timeline
    information with approximate dates for planned development cycles.

  * For other development releaes, edit the actual release dates and planned
    release dates for future development cycles, as needed.

* Commit changes and push to GitHub.
