Finalize Release on GitHub
--------------------------

* Update milestones:

  * Edit the milestone for the current release by updating the *Due date* with the actual release date.

  * Close the current milestone.

  * Create a new milestone for the first bugfix release (e.g. first vX.Y.1 (bugfix) release).

  * If necessary, create a new milestone for the next official release (e.g. next vX.Y.Z release).

* Update issues:

  * Close the GitHub issue for creating this official release.

  * If necessary, reassign any remaining issues for the current milestone to other milestones.

* Update projects:

  * Confirm that all existing development projects for the current milestone are closed.

  * If necessary, create development projects for the next milestone (e.g. |projectRepo|-X.Y.Z-beta1, beta2, beta3).

* Update branches:

  * Remove any remaining stale development branches from the new release.

  * Update the repository settings by resetting the *Default branch* to the new main_vX.Y branch:

.. parsed-literal::

     https://github.com/dtcenter/|projectRepo|
     -> Settings
     -> Branches (tab on left)
     -> change the drop down to new branch
