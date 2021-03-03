Update DTC Website
------------------

* Navigate to the downloads page for the |projectRepo| repository at www.dtcenter.org.

* Sign in to the Drupal interface and edit the Downloads page.

* If creating a new official release, be sure to add a new
  *Existing Builds and Docker* page, if one was not already created.

* Create a new *Software Release* for the newly released version by clicking on *Add New Release*.

  * For *Full Title of Release* type "|projectRepo| Version X.Y.Z".

  * For *Related Community Code* select both the METplus and the |projectRepo| options (use shift to select).

  * For *Version Label* type "|projectRepo| X.Y.Z betaN".

  * Select the release type (*Recommended* for official or bugfix releases or *Development* for development versions). If necessary, change previously *Recommended* versions to *Other*.

  * Enter the release date.

  * Click on *Add Code Download* then click *Add Link* to add links for each of the following:

  * Add Link: Release
      * If creating a MET release, the URL should be the .tar.gz file created
        in the "Attach Release Tarfile" step and the link text should be
        the file name of the tar file.
      * If creating a release for a project other than MET, the URL should be
        the release page that was just created under the GitHub Releases tab
        and the link text should be the name of the release.

  * Add Link: Link text should be "User's Guide" and the URL should be the top
    level directory of the User's Guide hosted on the web.

  * Add Link: Link text should be "Existing Builds and Docker" and the URL
    should be the latest Existing Builds page, i.e.
    https://dtcenter.org/community-code/metplus/metplus-4-0-existing-builds

  * Inside the text box in the "Release Notes" section provide a direct link to
    the release-notes.html in the User's Guide.

  * Click on "Create Release".

  * Click on "Save".  
