Create Release Feature Branch
-----------------------------

* Create a feature branch in which to update the version number and add release notes being sure to include the GitHub issue number for the new release.

.. parsed-literal::

    git checkout -b feature_NNNN_vX.Y.Z       # for an official or bugfix release
    git checkout -b feature_NNNN_vX.Y.Z-betaN # for a development release
    git checkout -b feature_NNNN_vX.Y.Z-rcN   # for a development release
