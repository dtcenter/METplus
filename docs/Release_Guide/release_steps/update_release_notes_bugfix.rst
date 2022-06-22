Update Release Notes
--------------------

You can refer to the GitHub Project board to see what has changed for this
release. Open the following URL in a browser:

.. parsed-literal::

    https://github.com/orgs/dtcenter/projects?type=beta

* Click on the project that corresponds to support for the release, i.e.
  |projectRepo| Version 4.1 Support

* Navigate to the "Closed Issues" tab.
  If this tab does not exist, follow these instructions to create it:

  * Click on "+ New view" button on the far right side of the view tabs
  * Click on "View <N>" (where <N> is an integer) and rename it to
    "Closed Issues"
  * Click on the down arrow next to the newly created view
  * Click on "Search or filter this view"
  * Enter the following info into the filter bar: **is:closed is:issue**
  * Click on the down arrow next to the view and click "Save changes"

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
