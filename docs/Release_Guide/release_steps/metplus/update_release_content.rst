Update Release Content
----------------------

Update content that should go into the release version but remain unchanged
in the develop branch.

Update the version number
^^^^^^^^^^^^^^^^^^^^^^^^^

Remove **-dev** from the version number:

* As of METplus 4.0.0, we are naming releases with X.Y.Z format even if Z is 0.
* As of METplus v4.0.0, the file containing the version number is located at
  **metplus/VERSION** (in earlier releases, the file was located at
  docs/version or doc/version).
* In the develop branch, the version should match the upcoming release
  with -dev added to the end like X.Y.Z-betaN-dev, i.e. 4.0.0-beta1-dev
* Remove **-dev** from the version number so that it matches the release
  you are creating.

Update the version number in the quick search links
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Open the docs/Users_Guide/quicksearch.rst file for editing.
* Replace the word "develop" in all of the links with "vX.Y.Z",
  replacing the X.Y.Z with the version number.
  For example, replace "develop" with "v4.0.0".
* Save and close the file.

Update the version numbers in the manage externals files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

build_components/Externals_stable.cfg

Each of the components in these files has a branch associated with them.
Update the value for branch to the tag associated with the release for each
METplus component that is part of this METplus coordinated release, i.e.
MET should be 10.0.0 for the METplus 4.0.0 coordinated release.
