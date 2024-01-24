Merge Development Changes to Main Branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ONLY PROCEED TO THIS STEP IF ALL OF THE AUTOMATED TESTS PASS FOR THE LATEST NIGHTLY DEVELOPMENT BUILD AT mats-docker-dev.gsd.esrl.noaa.gov (VPN required).

* Merge the latest development code into the main branch and push to origin.

.. parsed-literal::

    git merge development
    git push
    cd MATScommon
    git merge development
    git push
    cd ../METexpress
    git merge development
    git push
    cd MATScommon
    git pull
    cd ../..

