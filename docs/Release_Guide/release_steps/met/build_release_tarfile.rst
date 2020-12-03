Build Release Tarfile
---------------------

The MET software is distributed as a tarfile, but not the one created by GitHub. On a project machine (e.g. kiowa), clone the MET repository and run a script to build the tarfile for the newly tagged release.

.. parsed-literal::

    git clone https://github.com/dtcenter/MET
    met/scripts/met_checkout_and_build.sh tag vX.Y.Z

Edit the vX.Y.Z release on GitHub by uploading the resulting tar file (met-X.Y.Z.YYYYMMDD.tar.gz) as a release asset.
