Update Release Content
----------------------

Update content that should go into the release version but remain unchanged
in the develop branch.

**Update the version number in the quick search links:**

* Open the docs/Users_Guide/quicksearch.rst file for editing.
* Replace the word "develop" in all of the links with "vX.Y.Z",
  replacing the X.Y.Z with the version number.
  For example, replace "develop" with "v4.0.0".
* Save and close the file.

**Update the version numbers in the manage externals files:**

build_components/Externals_stable.cfg

Each of the components in these files has a branch associated with them.
Update the value for branch to the tag associated with the release for each
METplus component that is part of this METplus coordinated release, i.e.
MET should be 10.0.0 for the METplus 4.0.0 coordinated release.
