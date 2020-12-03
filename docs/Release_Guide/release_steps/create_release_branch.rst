Create Release Branch
---------------------

Create a branch from the develop branch that corresponds to the release and
push the branch to GitHub. For release X.Y.Z-betaN, run the following commands
(for bash, use setenv for first command if using csh)::

    release_branch=main_vX.Y.Z-betaN

    cd METplus
    git checkout develop
    git pull
    git checkout -b $release_branch
