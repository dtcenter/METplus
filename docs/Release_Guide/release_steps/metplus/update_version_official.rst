Update Version Number for Release
---------------------------------

Remove **-dev** from the version number

- As of METplus 4.0.0-beta2, we are naming releases with X.Y.Z format even if Z is 0
- As of METplus v3.0, the file containing the version number is located at docs/version (in earlier releases, the file was located at doc/version)
- In the develop branch, the version should match the upcoming release with -dev added to the end like X.Y.Z-betaN-dev, i.e. 4.0.0-beta1-dev
- Remove **-dev** from the version number so that it matches the release you are creating

Update the version number in the quick search links:
- Open the docs/Users_Guide/quicksearch.rst file for editing.
- Replace the word "develop" in all of the links with "vX.Y.Z", replacing the X.Y.Z with the version number.  For example, replace "develop" with "v4.0.0".
- Save and close the file.
