Finalize Release on GitHub
--------------------------

* Close the GitHub issue for creating this official release.
* Edit the milestone for the current release by updating the *Due date* with the actual release date.
* If necessary, create a new milestone for the next official release (e.g. next vX.Y.Z release).
* If necessary, reassign any remaining issues for the current milestone to the next one.
* Close the current milestone.
* Confirm that all existing development projects for the current milestone are closed.
* If necessary, create development projects for the next milestone (e.g. |projectRepo|-X.Y.Z-beta1, beta2, beta3).
* Update the repository settings by resetting the *Default branch* to the new main_vX.Y branch:

.. parsed-literal::

     https://github.com/dtcenter/|projectRepo|
     -> Settings
     -> Branches (tab on left)
     -> change the drop down to new branch

