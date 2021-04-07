Update DTC Website
------------------

* Navigate to the downloads page for the |projectRepo| repository at
  www.dtcenter.org.

* Sign in to the Drupal interface and edit the Downloads page.

* Create a new *Software Release* for the newly released version by clicking
  on *Add New Release*.

  * For *Full Title of Release* type "|projectRepo| Version X.Y.Z".

  * For *Related Community Code* select both the METplus and the |projectName|
    options (use shift to select).

  * For *Version Label* type "|projectRepo| X.Y.Z betaN".

  * Select the release type (*Recommended* for official or bugfix releases or
    *Development* for development versions). If necessary, change previously
    *Recommended* versions to *Other*.

  * Enter the release date.

  * Click on *Add Code Download* then click *Add Link* to add links for each of the following:

    * Add Link: |addTarfileStep|

    * Add Link: Link text should be "User's Guide" and the URL should be the top
      level directory of the User's Guide hosted on the web.

    * Add Link: Link text should be "Existing Builds and Docker" and the URL
      should be the latest Existing Builds page, i.e.
      https://dtcenter.org/community-code/metplus/metplus-4-0-existing-builds
      (If creating a new official release, be sure to add a new *Existing Builds
      and Docker* page, if one was not already created.)
  
  * Inside the text box in the "Release Notes" section provide a direct link to
    the *release-notes.html* file in the User's Guide.

  * Click on "Create Release".

  * Click on "Save".
