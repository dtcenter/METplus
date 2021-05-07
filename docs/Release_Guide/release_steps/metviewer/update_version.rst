Update Version Number for Release
---------------------------------

Create the version number

- In the METviewer/docs/version file, assign the version to the '__version__' keyword
- In the METviewer/build.xml file, assign the version in the 'dist' target
- In the METviewer/vebapp/metviewer/metviewer1.jsp file, assign the version to <div id='release'> and <title>
- We are naming releases with X.Y.Z format even if Z is 0.
- In the develop branch, the version should match the upcoming release like X.Y.Z-betaN
