Update Version Number for Release
---------------------------------

Remove **-dev** from the version number:

* We are naming releases with X.Y.Z format even if Z is 0.
* The file containing the version number is located at docs/version.
* In the METviewer/build.xml file, assign the version in the 'dist' target
* In the METviewer/vebapp/metviewer/metviewer1.jsp file, assign the version to <div id='release'> and <title>

* Save and close the file.
