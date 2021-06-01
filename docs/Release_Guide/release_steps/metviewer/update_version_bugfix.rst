Update Version Number for Release
---------------------------------

Update the version number for the bugfix release:

* For METviewer, the file containing the version number is located at docs/version.
* If the current release is listed as X.Y.Z (major.minor.micro), the bugfix version should be X.Y.Z+1
  (i.e. increment the micro value by 1: 1.1.0 becomes 1.1.1)
* In the METviewer/build.xml file, assign the version in the 'dist' target
* In the METviewer/vebapp/metviewer/metviewer1.jsp file, assign the version to <div id='release'> and <title>


