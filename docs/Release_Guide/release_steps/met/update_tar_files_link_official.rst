Update Tar File Links
^^^^^^^^^^^^^^^^^^^^^

Tar files containing the source code for the libraries upon which MET depends are provided on the DTC website.
Update the tar file links for each official release.

.. dropdown:: Instructions

  - On the DTC web server machine (i.e. mohawk) navigate to installation directory as the met_test user.

  .. parsed-literal::

     runas met_test
     cd /d2/www/dtcenter/dfiles/code/METplus/MET/installation

  - Add a link for the newly created MET release to the METbaseimage version upon which it depends.

  .. parsed-literal::

     # Replace "A.B" with the METbaseimage version
     # upon which the MET "X.Y" version depends
     ln -sf tar_files.met-base.vA.B.tgz tar_files.met-vX.Y.tgz
 
  - Update the "latest" link for the newly created MET "X.Y" version.
 
  .. parsed-literal::

     # Replace "A.B" with the METbaseimage version
     ln -sf tar_files.met-base.vA.B.tgz tar_files.latest.tgz

  - Confirm the result at https://dtcenter.ucar.edu/dfiles/code/METplus/MET/installation.
