Update DTC Website
------------------

* Navigate to https://dtcenter.org and sign in to the Drupal interface.

* Navigate to the downloads page for the |projectRepo| repository at
  https://dtcenter.org/community-code/metplus/download

* Click on the **Edit** button to edit the Downloads page.

* Create a new **Software Release** for the newly released version by clicking
  on **Add New Release**.

  * For **Full Title of Release** type "|projectRepo| Version X.Y.Z".

  * For **Related Community Code** select both the "METplus" and the "|projectName|"
    options (For Macs, hold the Command key to select both).

  * For **Version Label** type "|projectRepo| X.Y.Z-betaN".

  * Select the **Release Type** ("Recommended" for official or bugfix releases or
    "Development" for development versions).

  * Enter the **Release Date**.

  * Click on **Add Code Download** then click **Add Link** to add links for each of the following:

    * Add Link: |addTarfileStep|

    * Add Link: Link text should be "User's Guide" and the URL should be the top
      level directory of the User's Guide hosted on the web. Beta releases can
      use "develop" in the URL, but for official releases, please ensure the
      link uses the branch name (e.g. main_vX.Y) as opposed to the tag name
      (e.g. vX.Y.Z).  For example, use
      "https://metplus.readthedocs.io/en/main_vX.Y/Users_Guide/" and NOT
      "https://metplus.readthedocs.io/en/vX.Y.Z/Users_Guide/"

    * Add Link: Link text should be "Existing Builds and Docker" and the URL
      should be the latest Existing Builds page, i.e.
      https://dtcenter.org/community-code/metplus/metplus-X-Y-existing-builds
      (If creating a new official release, be sure to add a new *Existing Builds
      and Docker* page, if one was not already created.)
  
  * In the **Release Notes** text box provide a direct link to the
    *release-notes.html* file in the User's Guide.

  * Click on **Create Release**.

  * Update the existing releases, as needed.
    
    * For a development release, ensure the "Release Type" is set to
      **Development** and change any previous **Development** versions to
      **Other**.
      
    * For a bugfix or official release, change any previous
      **Recommended** versions to **Other**.
      
    * For an official release, remove the corresponding development
      releases.

  * Edit the "Coordinated METplus Version X.Y" software release.
      
    * For a bugfix release, update the existing link and text in
      the "Coordinated METplus-X.Y" release section with the
      X.Y.Z+1 information.

  * |otherWebsiteUpdates|

  * Click on **Save** at the bottom of the page.

