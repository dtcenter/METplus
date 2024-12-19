Update the Documentation on the Web
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Because Read the Docs is configured to automate the building of new "main"
branches in the METplus components' repositories, nothing needs to be done
to build the documentation for the new release. See the
:ref:`Read the Docs section <read-the-docs>` for further information.
For an official release, it is important to update the "Default branch" to
this latest "main" branch.  An administrator of the METplus component
repository will need to do the following to update the default branch:

  * Log into their Read the Docs account
    
  * Click on the appropriate METplus component project
    
  * Click on Settings in the top right menu
     
  * Select the new default branch in the dropdown menu for "Default branch"
    (e.g. main_v4.0.0) and click the Save button at the bottom of the page
    
  * Ensure that "latest" points to the new default branch by clicking on
    "latest" build that just started and click on "Version latest" to view the
    build run. When it finishes running, click on "View Docs" on the right of
    the page and confirm that the version number
    displayed in the header is the desired version for "latest".
    
 
