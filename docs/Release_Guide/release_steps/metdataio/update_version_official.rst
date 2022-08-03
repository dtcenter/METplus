Update Version Number for Release
---------------------------------

Remove **-dev** from the version number:

* We are naming releases with X.Y.Z format even if Z is 0.
* The file containing the version number is located at docs/version.
* In the develop branch, the version should match the upcoming release with -dev added to the end like X.Y.Z-betaN-dev, i.e. 4.0.0-beta1-dev
* Remove **-dev** from the version number so that it matches the release you are creating.

In docs/conf.py, update the version, release_year, and release_date variables for the documentation.
