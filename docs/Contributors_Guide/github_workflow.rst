.. _github-workflow:

GitHub Workflow
===============

How METplus releases are created
--------------------------------

The branching model employed by the METplus GitHub repository is similar to
that described in
`A successful Git branching model <https://nvie.com/posts/a-successful-git-branching-model/>`_,
where new or updated code is created on a 'feature' branch that is based on
the `dtcenter/METplus GitHub 'develop' branch <https://github.com/dtcenter/METplus/tree/develop>`_.

The feature branch is named after the corresponding GitHub issue:

*feature_<Github Issue number>_<brief_description>*


When work is complete, the code in the feature branch is merged into the
develop branch.  When a release candidate for METplus has been determined,
then the develop branch is used to create a main_vx.y release of METplus,
which includes data tarballs for use in running use cases.


Sequence of Events - Contributing Code
--------------------------------------

*Prerequisite:*

The user must set up a GitHub account if one does not already exist.
Log into the account.  For more information about GitHub accounts, please refer
to the GitHub Documentation on
`GitHub accounts <https://help.github.com/en/github/getting-started-with-github/signing-up-for-a-new-github-account>`_.


Workflow Overview
~~~~~~~~~~~~~~~~~

Contributors will follow these instructions for new development.
Detailed instructions for each item can be found below or by clicking the link.

#. :ref:`wo-find-issue`
#. :ref:`wo-fork-repo`
#. :ref:`wo-clone-repo`
#. :ref:`wo-set-upstream`
#. :ref:`wo-feature-branch`
#. :ref:`wo-make-changes`
#. :ref:`wo-commit-changes`
#. :ref:`wo-push-changes`

.. _wo-find-issue:

Find the GitHub issue
^^^^^^^^^^^^^^^^^^^^^

* Go to the `METplus repository <https://github.com/dtcenter/METplus>`_  and
  click on the `Issues tab <https://github.com/dtcenter/METplus/issues>`_.

* Search for an existing issue that describes the contribution.
  If one exists, take note of the issue number.
  If one cannot be found, create a
  `new Discussion <https://github.com/dtcenter/METplus/discussions/new>`_ on
  the METplus GitHub Discussions page to ask if an issue should be created.

.. _wo-fork-repo:

Fork the dtcenter/METplus repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **If the contributor has write access to the dtcenter/METplus repository,
  then forking the repository is not necessary.** If so, skip to the
  instructions related to creating a fork and keeping the fork in sync with
  the dtcenter/METplus repository.

* Retrieve a copy of the source code by forking the *dtcenter/METplus*
  repository into the user's own GitHub repository. Click on the **Fork**
  button in the upper right hand side of the
  `METplus repository <https://github.com/dtcenter/METplus>`_.

* Verify that your GitHub username is shown in the **Owner** pull down menu.
  If it is not, then the forked repository likely already exists. If so,
  continue to :ref:`wo-clone-repo`.

* Unselect the checkbox that says *Copy the main_vX.Y branch only*.

* The web page will refresh to the GitHub repository. For example:

  .. code-block:: ini

    https://github.com/{github-username}/METplus

  Where *{github-username}* is the user's GitHub username.
  An entire copy of the *dtcenter/METplus* GitHub repository is now in the
  user's area.

.. _wo-clone-repo:

Clone the repository locally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Change directories to a working directory. From the command line,
  enter the following:

  .. code-block:: ini

    git clone https://github.com/{github-username}/METplus

  replacing *{github-username}* with the user's GitHub username.
  If not working from a fork, then use *dtcenter*.

* Change directories to the METplus directory:

  .. code-block:: ini

    cd METplus

  This is the local METplus repository.

.. _wo-set-upstream:

Set upstream remote
^^^^^^^^^^^^^^^^^^^

* **If working from the dtcenter/METplus repository, skip this step.**

* Add a remote named origin to the clone of the local Git repository, which
  will allow changes to be pushed to the repository that was forked above.

  .. code-block:: ini

    git remote add upstream https://github.com/dtcenter/METplus

* To verify that the upstream and origin are correct, at the command
  line enter:

  .. code-block:: ini

    git remote -v

  Something like the following will be output:

  .. code-block:: ini

    origin	https://github.com/{github-username}/METplus (fetch)
    origin	https://github.com/{github-username}/METplus (push)
    upstream	https://github.com/dtcenter/METplus (fetch)
    upstream	https://github.com/dtcenter/METplus (push)

  where *{github-username}* is the user's GitHub username.

.. _wo-feature-branch:

Create a feature branch
^^^^^^^^^^^^^^^^^^^^^^^

* Generate a feature branch from the *develop* branch for new development
  following this naming convention:

  *feature_<Github Issue number>_<brief_description>*

  For example, for GitHub issue #777 that creates new wrapper xyz, the
  feature branch would be named:

  *feature_777_wrapper_xyz*


* Create the feature branch based off the develop branch:

  .. code-block:: ini

    git checkout develop

* Verify the current development branch is active by running:

  .. code-block:: ini

    git branch

  Something like the following will be output:

  .. code-block:: ini

    * develop
    main_v4.1

  The asterisk (*) indicates the active branch.

* Ensure that the develop branch is in sync with the upstream develop branch:

  .. code-block:: ini

   git fetch upstream
   git merge upstream/develop
   git push origin develop

* Create and checkout the feature branch. For example:

  .. code-block:: ini

    git checkout -b feature_777_wrapper_xyz

  replacing *feature_777_wrapper_xyz* with the feature branch name.

* Verify that the user is working in the correct branch by running:

  .. code-block:: ini

    git branch

  Something like the following will be output:

  .. code-block:: ini

    develop
    main_v4.1
    * feature_777_wrapper_xyz

  The asterisk (*) indicates the active branch.

.. _wo-make-changes:

Make changes to code in the feature branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Users should make changes to their feature branch and commit changes to their
local repository.

* If adding a new METplus use case:

    * Follow the instructions on the :ref:`adding-use-cases` section of the
      Contributor's Guide.

* If making code changes:

    * Follow the coding standards in the :ref:`codingstandards` section of the
      Contributor's Guide.

    * Add unit tests using the pytest framework

    * Add documentation

* If working in a forked repository, keep the fork in sync with the origin
  repository:

    * New changes to the origin repository may be added by others during
      development. Periodically apply these changes to the feature branch to
      avoid conflicts.

    * To merge the latest changes from the origin develop branch into the
      feature branch, run the following from the feature branch:

  .. code-block:: ini

    git fetch upstream
    git merge upstream/develop

  The *fetch* command obtains all new changes from the upstream (dtcenter)
  repository.
  The *merge* command merges the latest changes from the upstream develop
  branch into the feature branch.

* If not working in a forked repository, keep the feature branch in sync with
  the develop branch:

  .. code-block:: ini

    git fetch
    git merge develop

* If the console output includes the text *CONFLICT*, then there are
  conflicts between the two branches that must be resolved manually.
  Refer to the GitHub documentation for help with
  `Resolving a merge conflict using the command line <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-using-the-command-line>`_.

.. _wo-commit-changes:

Commit changes to feature branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* View all files that have changed since the last commit:

  .. code-block:: ini

    git status

* It is recommended to group related changes into a single commit.
  Mark files to be committed using the *git add* followed by the filename:

  .. code-block:: ini

    git add <filename1>
    git add <filename2>

* Check the status again to verify that the correct files have been staged
  for commit:

  .. code-block:: ini

    git status

* Commit the files by running the *git commit* command. The -m argument can
  be used to add a commit message to describe the changes.

  .. code-block:: ini

    git commit

  A popup window will appear. Enter a description about this commit, using the
  editor the user selected when the Git account was set up.
  Please refer to the
  `Git Setup <https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup>`_
  documentation on configuring a Git account.

  For the first line of the commit comment, enter a brief description,
  such as the GitHub
  Issue number and a brief description.  On the second and subsequent lines,
  provide a detailed description of the changes/additions that were made.

  **Note**: It is a best practice to commit one change per commit,
  rather than wait
  until there are multiple changes to include in one commit.

* Alternatively, the -m argument can be used to add a commit message to
  describe the changes.

  .. code-block:: ini

    git commit -m "{commit_message}"

  where {commit_message} is a descriptive message about the changes.


.. _wo-push-changes:

Push the feature branch to GitHub
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pushing changes up to GitHub periodically is recommended to avoid losing
progress by relying on the local copy of the changes.

* To push changes to GitHub, run the following:

  .. code-block:: ini

    git push origin <feature_777_wrapper_xyz>

  replacing *<feature_777_wrapper_xyz>* with the feature branch name


.. _pull-request-browser:
  
Open a pull request
^^^^^^^^^^^^^^^^^^^

* To request to have the changes be incorporated into the remote repository
  (i.e. the
  `GitHub METplus repository <https://github.com/dtcenter/METplus>`_).

* An authorized METplus developer will need to approve the request and
  then merge the files into the repository's develop branch.
  The develop branch will be used to create a future METplus release.

* In the browser, navigate to https://github.com/<your-github-user>/METplus
  replacing
  <your-github-user> with the user's GitHub username and no angle brackets <>.

* Click on the green 'Compare & pull request' button.

  * A web page with four grey buttons should appear:

    * On the left-most button (for setting the base repository),
      make sure the
      'base repository:dtcenter/METplus' is selected.

    * For the base button, make sure to select 'base:develop'.

    * For the head repository button, make sure to select
      'head repository:<your-github-user>/METplus'
      with the appropriate replacement for
      <your-github-user>.

    * For the compare button, make sure to select
      'compare:<your_feature_branch>'
      where <your_feature_branch> corresponds to the feature branch
      where the changes have been made (e.g. feature_777_wrapper_xyz).

    * In the 'write' window, follow the directions and fill in the template.
      Add any additional comments/details.  When filling in the template,
      be sure to "Define the PR metadata, as permissions allow.
      Select: **Reviewer(s), Project(s)**, and **Milestone**". When selecting a
      reviewer, internal contributors submitting pull requests should select
      the appropriate reviewer(s) and let the reviewer know that the pull
      request has been assigned to them. If external contributors are unsure
      who to assign as a reviewer, create a post in the
      `METplus GitHub Discussions Forum <https://github.com/dtcenter/METplus/discussions>`_
      asking for help with the assignment of a reviewer.
      
    * When everything looks satisfactory, click on the green 'Create pull
      request' button.

    * An authorized METplus developer will accept the pull request (if
      everything meets acceptance criteria) and merge the code into the remote
      repository's develop branch.

Approve a pull request using a browser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Submitting a pull request allows a user to propose changes, request a
review of the contributions and have the proposed changes merged into a
different branch. Pull requests allow the reviewer to see the differences
in the content from both branches.

For issues with sub-tasks, it may be desired to get some changes into the
develop branch sooner, rather than later. If the changes seem to make sense
on their own and don't rely on other sub-tasks to be complete, creating a pull
request for a sub-task may make sense. If a sub-task does rely on other
sub-tasks to be complete, then it may be best to wait to create a pull request
until the other sub-tasks are also complete.


Creating a pull request
^^^^^^^^^^^^^^^^^^^^^^^

1.  Click on the “Pull requests” tab in the GitHub repository and
    click on the assigned pull request.
2.  Ensure the continuous integration (CI) tests from
    `GitHub Actions <https://github.com/dtcenter/METplus/actions>`_ have
    passed.  See "All checks have passed" in the figure below. If the tests
    were not successful or if there are conflicts with the base branch,
    ask the requestor to make changes.

    .. figure:: figure/checks_pass_no_conflicts.png
    
3.  Take a look at the description of the testing already performed for
    these changes and then see what the recommended testing is for the
    reviewer to perform.
4.  Perform any testing that is requested of the reviewer.
5.  Check to ensure the correct "base" branch is selected. In most cases, the
    "base" branch will be the "develop" branch.
6.  Click on the “Files Changed” tab to review the differences in code
    between the “base” branch and the “compare” branch.
7.  Review each file and ensure that the changes seem reasonable.

    A reviewer can suggest changes be made by:
    
    a. Mousing over the line to comment on.

       .. figure:: figure/add_comment_on_line.png

         A blue box with a plus will appear. Click on the blue box.

       .. figure:: figure/insert_suggestion.png
    
         Click on the icon of a paper with +/- to “Insert a Suggestion”.
	 The line
         will be quoted and the reviewer can enter their suggestion below.
	 Then, click on
         the “Add Single Comment” button, so that the requestor will get an
         email letting them know the reviewer has made a suggested change.

    b. Or, a reviewer can edit the file directly on the web by clicking on the
       “...” icon (three dots) in the right hand corner next to the
       “Viewed” icon and selecting “Edit file”. 	

       .. figure:: figure/how_to_edit_file.png

8.  Ensure the requestor has made all necessary documentation updates.

9.  Ensure the requestor has made all necessary testing updates.

10.  If any changes were made, note that the CI tests will rerun.
     Before moving on, make sure "All checks have passed." and make sure
     “This branch has no conflicts with the base branch”.  Let the requestor
     know if the checks do not pass or if there is a conflict with the base
     branch so that they can make the  necessary changes.

11.  A reviewer has three possible options:

     * **Comment**: Submit general feedback without explicitly approving the
       changes or requesting additional changes.
     
     * **Approve**: Submit feedback and approve merging the changes proposed in
       the pull request.

     * **Request changes**: Submit feedback that must be addressed before the
       pull request can be merged.
	    
     .. figure:: figure/review_approve_changes.png

         A reviewer should click on: "Review changes", add comments to
	 the "Write box", and select either  "Comment", "Approve",
	 or "Request Changes", and then click on "Submit Review".

12. Once the recommended testing is complete and any necessary changes have
    been made, approve the request.


Merging pull requests
^^^^^^^^^^^^^^^^^^^^^
Once the pull request has been approved it is ready to be merged.  **As
permissions allow, the requestor is responsible for merging the pull request
once it has been approved.**


There are three merge methods to choose from: "Create a merge commit",
"Squash and merge", and "Rebase and merge". It is recommended to use the
**Squash and merge** method because all of the merge request’s commits are
combined into one and a clean history is retained. Click on the chosen merge
method.  

After merging, the requestor can then decide whether or not to delete
the branch.

.. figure:: figure/delete_branch.png

If the requestor wishes to delete the “compare” branch, the “Delete branch”
button should be selected and the corresponding GitHub issue should be closed.


Clean up after a successfully merged pull request
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* After an authorized METplus developer has accepted the changes and merged
  them into the develop repository, update the local clone by pulling changes
  from the original repository's (i.e. the
  `METplus develop branch <https://github.com/dtcenter/METplus/tree/develop>`_):

* Checkout the develop branch:

  .. code-block:: ini

    git checkout develop

* Verify that the develop branch is now active:

  .. code-block:: ini

    git branch

* Merge changes from the upstream develop branch with the local develop branch:

  .. code-block:: ini

    git pull upstream develop

* The local cloned repository should now have all the latest changes from the
  original repository's develop branch.

  Now the feature branch can be deleted:

  .. code-block:: ini

    *git branch -D <branch name>*
    *git push --delete origin <branch name>*

  where <branch name> is the feature branch name, e.g. feature_777_wrapper_xyz.

  Verify that the feature branch has been successfully removed/deleted
  via the web browser. Navigate to
  https://github.com/<your-github-user>/METplus,
  replacing <your-github-user> appropriately. Under the 'Branch'
  pulldown menu, the feature branch name should no longer be seen
  as an option.














