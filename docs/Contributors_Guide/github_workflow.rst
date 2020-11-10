.. _github-workflow:

GitHub Workflow
===============

How METplus releases are created
--------------------------------

The branching model employed by the METplus GitHub repository is similar to
that described in
`A successful Git branching model <https://nvie.com/posts/a-successful-git-branching-model/>`_,
where new or updated code is created on a 'feature' branch that is based on
the `NCAR/METplus GitHub 'develop' branch <https://github.com/dtcenter/METplus/tree/develop>`_..

The feature branch is named after the corresponding GitHub issue:

| *feature_<Github Issue number>_<brief_description>*
|

When work is complete, the code in the feature branch is merged into the
develop branch.  When a release candidate for METplus has been determined,
then the develop branch is used to create a master_vx.y release of METplus,
which includes data tarballs for use in running use cases.


Sequence of Events - Contributing Code
--------------------------------------

*Pre-requisite:*

Set up a GitHub repository account if you do not already have one, and log
into your account.  For more information about GitHub accounts, please refer
to the GitHub Documentation on `GitHub accounts <https://help.github.com/en/github/getting-started-with-github/signing-up-for-a-new-github-account>`_.


**Workflow Overview:**

A contributor to METplus will do the following:

1.  Create a GitHub Issue to track the new contribution.

2.  Fork the NCAR/METplus repository.

3.  Clone the fork to local repository.

4.  Set upstream remote (to assist in keeping upstream and local repositories synchronized).

5.  Generate a feature branch from the 'develop' branch for new development.

6.  Make changes to code in the feature branch.

7.  Commit changes to feature branch (limit one change per commit).

8.  Push the feature branch to GitHub.

9.  Open a pull request from feature branch to original repo (from which you forked, in step 2 above).

10.  Clean up after pull request has been merged by an authorized METplus developer.



Create a GitHub Issue that reflects what needs to be done
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Go to the `METplus repository <https://github.com/dtcenter/METplus>`_  and
  click on the `Issues link <https://github.com/dtcenter/METplus/issues>`_.

* Click on the green **New issue** button.

* Write a description of the task and attach appropriate values to Assignee,
  Labels, and Milestone links located on the right hand side of the page.


Fork the NCAR/METplus repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Retrieve a copy of the source code by forking the NCAR/METplus repository
  into your own GitHub repository. Click on the **Fork** button in the upper right
  hand side of the `METplus repository <https://github.com/dtcenter/METplus>`_.

* Click on the appropriate GitHub account when presented with the pop-up window
  with the question 'Where should we fork METplus?'.

* Your web page will refresh to your GitHub repository at, for example:

  .. code-block:: ini

    https://github.com/<your-github-user>/METplus

  where *<your-github-user>* is replaced with your GitHub username.  You now
  have an entire copy of the NCAR/METplus Github repository.


Clone the fork to a local repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Copy the source code to the directory where you will be doing your work.

* Change directories to a working directory. From the command line,
  enter the following:

  .. code-block:: ini

    git clone https://github.com/<your-github-user>/METplus

  replacing <your-github-user> with your GitHub username.

* Change directories to the METplus directory:

  .. code-block:: ini

    cd METplus

  Now you are in your local METplus repository.

Set upstream remote
^^^^^^^^^^^^^^^^^^^

* Add a remote named origin to the clone of your local Git repository, which
  will allow you to push changes to the repository you forked in step 1.

  .. code-block:: ini

    git remote add upstream https://github.com/dtcenter/METplus

* To verify that the upstream and origin are correct, at the command line enter:

  .. code-block:: ini

    git remote -v

  You should see something like the following:

  .. code-block:: ini

    origin	https://github.com/<your-github-user>/METplus (fetch)
    origin	https://github.com/<your-github-user>/METplus (push)
    upstream	https://github.com/dtcenter/METplus (fetch)
    upstream	https://github.com/dtcenter/METplus (push)

  where <your-github-user> is your GitHub username.


Generate a feature branch from the 'develop' branchfor new development
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Create a feature branch in the NCAR/METplus GitHub repository following this naming convention

| *feature_<Github Issue number>_<brief_description>*
|

  For example, for GitHub issue #777 that creates new wrapper xyz, the feature branch would be named:

| *feature_777_wrapper_xyz*
|

* Create your feature branch based off the develop branch

  .. code-block:: ini

    git checkout develop

* Verify that you are currently working in the develop branch by running

  .. code-block:: ini

    git branch

  You should see something like the following:

  .. code-block:: ini

    * develop
    main_v3.1

  The asterisk, "*", indicates the currently active branch.

* At the command line, create and checkout the feature branch. For example:

  .. code-block:: ini

    git checkout -b feature_777_wrapper_xyz

  replacing *feature_777_wrapper_xyz* with your feature branch name.

* Verify that you are working in the correct branch by running:

  .. code-block:: ini

    git branch

  You should see something like the following:

  .. code-block:: ini

    develop
    main_v3.1
    * feature_777_wrapper_xyz

  where the asterisk, "*", indicates which branch is currently in use/checked out.


Make changes to code in the feature branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Users should make changes to their feature branch and commit changes to their
local repository.

* Create code following the coding standards in the :ref:`codingstandards` section of
  the Contributor's Guide.

* Provide some tests for your code using the pytest framework, provide user documentation
  describing what the code does, and provide any necessary data.

* Keep your fork in sync. While working, it is highly likely that changes are occurring in
  the original repository.  This may impact your work.  Regularly use the following commands
  to keep your fork in sync with the original repository.

  .. code-block:: ini

    git pull upstream develop
    git push origin develop
    git merge origin develop

  The first command pulls changes from the original repository (the
  `METplus GitHub repository <https://github.com/dtcenter/METplus>`_ that you see when you
  run *git remote -v* and that you set to upstream in step 4 above).  The second command
  pushes those changes to your forked repository.  The third command will merge the local
  develop branch into the feature branch.


Commit changes to feature branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Commit any new files by running the following.  Run the *'git add'* command only if this file is
  newly created and does not yet exist in your repository.

  .. code-block:: ini

    git add <filename>
    git commit <filename>

  replacing <filename> with the filename.

  A popup window will appear, where you will enter a description of this commit, using the
  editor you selected when you set up your Git account.  Please refer to the
  `Git Setup <https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup>`_
  documentation on configuring your Git account.

  For the first line of your commit comment, enter a brief description, such as the GitHub
  Issue number and a brief description.  On the second and subsequent lines, provide a
  detailed description of the changes/additions you made.

  **Note**: It is a best practice to commit one change per commit, rather than wait
  until you have multiple changes to include in one commit.

Push the feature branch to GitHub
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Run the following:

  .. code-block:: ini

    git push origin <feature_777_wrapper_xyz>

  replacing *feature_777_wrapper_xyz* with your feature branch name, to push your changes to
  the origin (i.e. to your *https://github.com/<your-github-user>/METplus* repository)

Open a pull request using a browser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* To request to have your changes be incorporated into the remote repository
  (i.e. the `GitHub METplus repository <https://github.com/dtcenter/METplus>`_).

* An authorized METplus developer will need to approve the request and then merge your files
  into the repository's develop branch.  The develop branch will be used to create a future
  METplus release.

* In your browser, navigate to *https://github.com/<your-github-user>/METplus* replacing
  <your-github-user> with your GitHub username.

* Click on the green 'Compare & pull request' button

  * A web page with four grey buttons should appear:

    * On the left-most button (for setting the base repository), make sure you have selected
      'base repository:NCAR/METplus'

    * For the base button, make sure you have selected 'base:develop'

    * For the head repository button, make sure you have selected
      'head repository:<your-github-user>/METplus' where <your-github-user> is your GitHub
      account name.

    * For the compare button, make sure you have selected 'compare:<your_feature_branch>'
      where <your_feature_branch> corresponds to the feature branch where you have been
      making your changes (e.g. feature_777_wrapper_xyz).

    * In the 'write' window, add any additional comments/details.  In this window are the
      comments you created when you committed your changes in step 6 above.

    *  You can scroll down to see what changes were made to the file you committed.

    * When everything looks satisfactory, click on the green 'Create pull request' button.

    * An authorized METplus developer will accept the pull request (if everything
      meets acceptance criteria) and merge your code into the remote repository's develop
      branch.

Clean up after a successfully merged pull request
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* After an authorized METplus developer has accepted your changes and merged
  them into the develop repository, update your local clone by pulling changes
  from the original repository's (i.e. the `METplus develop branch <https://github.com/dtcenter/METplus/tree/develop>`_):

* Checkout your develop branch

  .. code-block:: ini

    git checkout develop

* Verify that you are now working from the develop branch

  .. code-block:: ini

    git branch

* Merge changes from the upstream develop branch with your local develop branch

  .. code-block:: ini

    git pull upstream develop

* Your local cloned repository should now have all the latest changes from the
  original repository's develop branch.

  Now you can delete your feature branch:

  .. code-block:: ini

    *git branch -D <branch name>*
    *git push --delete origin <branch name>*

  where <branch name> is your feature branch name, e.g. feature_777_wrapper_xyz

  You can verify that your feature branch has been successfully removed/deleted
  via your web browser. Navigate to *https://github.com/<your-github-user>/METplus*,
  replacing <your-github-user> with your GitHub username, and under the 'Branch'
  pulldown menu, you should no longer find your feature branch as a selection.














