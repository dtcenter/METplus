Create Release Branch
---------------------

* Create a branch from the develop branch for the new official release and push it to GitHub.

.. parsed-literal::

    cd |projectRepo|
    git checkout develop
    git pull
    git checkout -b main_vX.Y
    git push -u origin main_vX.Y

