Pull Changes, Create Release Branch, And Merge To Development
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* On your system, pull any build-related code changes.

.. parsed-literal::

    git pull
    cd MATScommon
    git pull
    cd ../METexpress
    git pull
    cd MATScommon
    git pull
    cd ../..

* Create a release branch of the format main_vX.Y.Z. using your release version.

.. parsed-literal::

    git checkout -b main_vX.Y.Z
    git push -u origin main_vX.Y.Z
    cd MATScommon
    git checkout -b main_vX.Y.Z
    git push -u origin main_vX.Y.Z
    cd ../METexpress
    git checkout -b main_vX.Y.Z
    git push -u origin main_vX.Y.Z
    cd MATScommon
    git checkout -b main_vX.Y.Z
    git push -u origin main_vX.Y.Z
    cd ../..

* Checkout development and merge any build-related changes.

.. parsed-literal::

    git checkout development
    git merge main
    git push
    cd MATScommon
    git checkout development
    git merge main
    git push
    cd ../METexpress
    git checkout development
    git merge main
    git push
    cd MATScommon
    git pull
    cd ../..

* Add the following code to the top of MATS/MATScommon/meteor_packages/mats-common/public/MATSReleaseNotes.html.

.. parsed-literal::

    <div>
        <hr style="display: block; height: 2px; margin: 1em 0; border-top: 2px solid #000000;"/>
    </div>
    <div>
        <p><h4>Production build date: <x-cr>Current revision</x-cr></h4>
        <p><h4>Integration build date: <x-bd>Not yet built</x-bd></h4>
        <p style="margin: 25px 0;"></p>
        <p><h4>PUT APP VERSIONS HERE</h4>
        <p style="margin: 25px 0;"></p>
        <p>Changes: </p>
        <p>* PUT CHANGES HERE</p>
    </div>

* Commit and push to origin/development.

