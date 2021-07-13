Update Version Number for Release
---------------------------------

Remove **-dev** from the version number:

* As of METplus 4.0.0, we are naming releases with X.Y.Z format even if Z is 0.
* As of METplus v4.0.0, the file containing the version number is located at **metplus/VERSION** (in earlier releases, the file was located at docs/version or doc/version).
* In the develop branch, the version should match the upcoming release with -dev added to the end like X.Y.Z-betaN-dev, i.e. 4.0.0-beta1-dev
* Remove **-dev** from the version number so that it matches the release you are creating.
