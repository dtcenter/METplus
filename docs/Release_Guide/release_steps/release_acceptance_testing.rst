Release Acceptance Testing
--------------------------

A single GitHub Discussion is created in the METplus repository in the
`Release Acceptance Testing <https://github.com/dtcenter/METplus/discussions/categories/release-acceptance-testing>`_
category to summarize external testing for all development cycles of the METplus
components included in a coordinated release.

* If creating a release for the first development cycle (e.g. beta1 release),
  check to see if the
  `Release Acceptance Testing <https://github.com/dtcenter/METplus/discussions/categories/release-acceptance-testing>`_
  discussion for the next coordinated release has already been created.
* If not, create a new one to summarize external testing for all development
  cycles of the METplus components.

  * Locate the **Release Acceptance Testing** discussion for the last
    coordinated release.
  * Copy and paste its contents into a new discussion, being sure to update
    the title of the discussion and empty the contents of repository testing
    tables for each of the METplus components.
  * Carefully review the contents and links and update them as needed.
  * If needed, create a new label for the next **METplus X.Y Coordinated Release**
    in the METplus repository and add that label to this discussion.

* Update the contents of the **Release Acceptance Testing** discussion for
  each |projectRepo| development release.

  * Locate the |projectRepo| repository testing table within the body of the discussion.
  * For issues for which no external testing is required:

    * Create a *single table entry* for this development cycle.
    * Set the "Status" column to **PASS**.
    * Set the "|projectRepo| Issue" column to a list of links for all of the issues.
    * Set the "Dev Cycle" column to the current development cycle name (e.g. beta1, beta2, beta3, rc1).
    * Leave the "Tester" column empty.
    * Set the "Acceptance Testing Comment Link" column to **No external testing required**.

  * For issues that do require external testing:

    * Create a *separate table entry* for each issue.
    * Set the "Status" column to **OPEN**.
    * Set the "|projectRepo| Issue" column to link to the issue.
    * Set the "Dev Cycle" column to the current development cycle name (e.g. beta1, beta2, beta3, rc1).
    * Set the "Tester" column to a list of GitHub user name(s) to solicit their feedback.
    * Leave the "Acceptance Testing Comment Link" column empty.

  * Save your edits to the discussion.

* External testers are instructed to add comments to the discussion to summarize
  the status of their testing. The METplus team monitors those comments and, as needed,
  updates the "Status" and "Acceptance Testing Comment Link" columns of the repository
  testing table for each METplus component.
