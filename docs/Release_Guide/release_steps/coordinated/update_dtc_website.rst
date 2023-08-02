Update DTC Website
------------------

* Navigate to https://dtcenter.org and sign in to the Drupal interface.

* Navigate to the METplus downloads page at
  https://dtcenter.org/community-code/metplus/download

* Click on the **Edit** button to edit the Downloads page.

* Create a new **Software Release** for the new coordinated release by clicking
  on **Add New Release**.

  * For **Full Title of Release** type "Coorindated METplus X.Y".

  * For **Related Community Code** select only the "METplus" option.

  * For **Version Label** type "Coordinated METplus X.Y".

  * Select the **Release Type** as "Recommended".

  * Select the **Release Options** as "Coordinated".

  * Enter the **Release Date**.

  * Click on **Add Code Download** then click **Add Link** to add links for each of the following:

    * Add Link: Link text should be "METplus X.Y.Z" and the URL should be a link to the METplus component DTC release page.

    * Add Link: Link text should be "MET X.Y.Z" and the URL should be a link to the MET component DTC release page.

    * Add Link: Link text should be "METviewer X.Y.Z" and the URL should be a link to the METviewer component DTC release page.

    * Add Link: Link text should be "METexpress X.Y.Z" and the URL should be a link to the METexpress component DTC release page.

    * Add Link: Link text should be "METplotpy X.Y.Z" and the URL should be a link to the METplotpy component DTC release page.

    * Add Link: Link text should be "METcalcpy X.Y.Z" and the URL should be a link to the METcalcpy component DTC release page.

    * Add Link: Link text should be "METdataio X.Y.Z" and the URL should be a link to the METdataio component DTC release page.

    * Add Link: Link text should be "Documentation" and the URL should be the top
      level directory of the main_vX.Y branch of the METplus User's Guide hosted on the web.
      For example, use
      "https://metplus.readthedocs.io/en/main_vX.Y/Users_Guide/" and NOT
      "https://metplus.readthedocs.io/en/vX.Y.Z/Users_Guide/"

    * Add Link: Link text should be "Existing Builds and Docker" and the URL
      should be the latest Existing Builds page, i.e.
      https://dtcenter.org/community-code/metplus/metplus-X-Y-existing-builds

  * In the **Release Notes** text box provide direct links to the *release-notes.html*
    files on the main_vX.Y branch of the User's Guide for each component.

  * Click on **Create Release**.

  * Update any existing coordinated releases by changing the **Release Type** from
    "Recommended" to "Other" and click the **Update Release** button.

  * Review the existing component releases and remove any remaining development
    releases (e.g. beta and rc) for any of the official releases included in this
    coordinated release.

  * Click on **Save** at the bottom of the page.

* Create a new **Existing Builds and Docker** page for the next coordinated release.
