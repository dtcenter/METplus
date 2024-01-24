Tag App Version and Build
^^^^^^^^^^^^^^^^^^^^^^^^^

* METexpress apps are versioned as major.minor.patch. To trigger the build of a specific version, you will need to tag the current main branch in all the repositories with the version number.

.. parsed-literal::

    git tag vX.Y.Z
    git push origin vX.Y.Z
    cd MATScommon
    git tag vX.Y.Z
    git push origin vX.Y.Z
    cd ../METexpress
    git tag vX.Y.Z
    git push origin vX.Y.Z
    cd MATScommon
    git pull
    cd ../..

* This will cause github to automatically build the versioned app containers for the release.
