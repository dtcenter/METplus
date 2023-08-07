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

.. _wo-development-project:

GitHub Projects to manage development
-------------------------------------

Software development for official METplus releases is organized into development cycles.
While the length a development cycle can vary widely, they are nominally 6 weeks long.
GitHub issues and pull requests assigned to each cycle are either completed during the
time window for that cycle or reassigned to a future development cycle.


Each development cycle culminates in the creation of a software release. The
:ref:`releaseTypes` section describes the various types of software releases
(development, official, or bugfix).  Each development cycle culminates in a beta release,
a release candidate, or the official release. Generally, a **beta** development cycle results
in a **beta** development release while an **rc** development cycle results in an **rc**
development release.


The METplus team uses GitHub projects to manage these development cycles as well as the support
of official releases.  In earlier versions, each development cycle was managed by an individual
GitHub project but more recent versions use a single GitHub project to manage all of the
development cycles.  Listed below are instructions for creating a single GitHub project to
manage development toward a new official release.  Note that sufficient permissions in GitHub
are required to perform the following steps.


1. Create a **New project**.

   - From the `DTCenter GitHub Projects <https://github.com/orgs/dtcenter/projects>`_
     page, select the **New project** button.

   - In the **Select a template** popup window, select the **Project templates: Feature**
     option, and click the **Create** button.

2. Update the project **Settings**.

   - Click on the three dots to the right of the project name to see **More options**
     and select **Settings**.  Modify these settings as follows.

      - Project name: The default project name is **@UserNames's feature**.  Rename it as
        **{METplus Component}-{Target Version Number} Development** (e.g. **METplus-Wrappers-5.1.0 Development**).

      - Add a description: Add **Development toward {METplus Component} version {Target Version Number}.**

      - README: Add additional details as needed to the **README** section.  Projects managing development
        for multiple repositories, such as METplus-Analysis, should list the target version number for
        each repository.

      - Scroll down to the **Danger zone** and change **Visibilty** from its default value of **Private**
        to **Public**.

   - Select **Manage access** on the left hand navigation bar.

      - By default, the project creator has **Admin** access.

      - Add **Admin** access for any user with that level of access to any one
        of the repositories managed by this project.

      - Add **Write** access for the **METplus** group.

   - Locate the **Custom fields** section in the left hand navigation bar

      - Select **Status** and retain the default list of options, but delete the
        **New** option by clicking the **X** to its right.

      - Select **Iteration** and modify the **Field name** to be **Cycle**.  Delete any existing cycles.
        Under **More options** select a **Start on** date and set the default **Duration** as 6 weeks.
        Click the **Add** and **Add iteration** buttons to create 5 cycles, each with the default duration
        of 6 weeks. Modify the cycle names to be **Beta1**, **Beta2**, and so on. Click **Save changes**.

      - Select **Estimate** and click the three dots to the right and **Delete field**.

   - Click the back arrow to return to the project page.

3. Update the project **Workflows**.

   - Click on the three dots to the right of the project name to see **More options**
     and select **Workflows**.  Modify these settings as follows.

      - Enable the **Item added to project** workflow and set the status to **Backlog**.

      - Enable the **Item reopened** workflow and set the status to **In progress**.

      - Enable the **Item closed** workflow and set the status to **Done**.

      - Enable the **Pull request merged** workflow and set the status to **Done**.

      - Leave all other workflows disabled.

   - Click the back arrow to return to the project page.

4. Create project **Views**.

   - Each view appears as a tab on the project page.  Create a new view as described below.

      - Select the **+ New view** option.

      - Click on the view name to modify it, rename it as **All Cycles**, and hit **Enter**.

      - Click on the down arrow and, under **Configuration**, select the **Fields** option. Enable
        the options for **Title**, **Repository**, **Assignees**, **Cycle**, **Status**,
        **Linked Pull Request**, and **Reviewers**. Drag and drop the items to reorder them as listed above.

      - In the resulting view, click the three dots in the **Status** column. Select the **Sort descending**
        and **Group by values** options.

      - The blue dot on the down arrow for this tab indicates that there are unsaved changes.
        Select the **Save changes** option.

   - Click on the down arrow and select **Duplicate View**.  Do this 8 times and name/refine these views as follows.

      - View name **All Required** shows all items labelled as *REQUIRED* for the development or official release.
        Click on the 3 horizontal bars and define the filtering criteria as
        ``is:open label:'required: FOR OFFICIAL RELEASE','required: FOR DEVELOPMENT RELEASE'``.
        Click **Save Changes**.

      - View names **Beta1** through **Beta5** show items for each individual development cycle.
        Click on the 3 horizontal bars and define the filtering criteria as
        ``cycle:Beta1``, ``cycle:Beta2``, and so on. Click **Save Changes**.

      - View name **Closed Issues** shows issues that have been closed across all development cycles.
        Click on the 3 horizontal bars and define the filtering criteria as
        ``is:closed is:issue``. Click on the 3 dots in the **Cycle** column and select
        **Group by values**.  Click **Save Changes**.

      - View name **High/Blocker Not Required** shows all items labelled as *HIGH* or *BLOCKER*
        priority but not marked as required for the development or official release.
        Click on the 3 horizontal bars and define the filtering criteria as
        ``is:open label:'priority: high','priority: blocker'``
        ``-label:'required: FOR DEVELOPMENT RELEASE'``
        ``-label:'required: FOR OFFICIAL RELEASE'``.
        Click **Save Changes**.

   - Delete any other views created by default by clicking the down arrow next to the view name and
     selecting **Delete view**.

5. Refine the project settings, development cycle dates, and views, as needed, based on the preferences
   of the development team.

6. Link the new project to each repository.

   - Navigate to the project page for each repository managed by this project
     (e.g. `METplus Projects <https://github.com/dtcenter/METplus/projects>`_).

   - Click the **Link a project** button and find/select this newly created project.

.. _wo-support-project:

GitHub Projects to manage support
---------------------------------

Support for coordinated METplus releases is managed using a *single* GitHub project
for all components.  Bugfix issues and the corresponding pull request fixes are added
to that support project.  Each fix is assigned to the current bugfix milestone of
the corresponding source code repository.


The :ref:`releaseTypes` section describes the various types of software releases
(development, official, or bugfix).  The GitHub support project contains issues and
pull requests that apply only to bugfix releases.


Listed below are instructions for creating a GitHub project to manage support after an
official coordinated METplus release.  Note that sufficient permissions in GitHub are
required to perform the following steps.


1. Create a **New project**.

   - From the `DTCenter GitHub Projects <https://github.com/orgs/dtcenter/projects>`_
     page, select the **New project** button.

   - In the **Select a template** popup window, select the **Project templates: Feature**
     option, and click the **Create** button.

2. Update the project **Settings**.

   - Click on the three dots to the right of the project name to see **More options**
     and select **Settings**.  Modify these settings as follows.

      - Project name: The default project name is **@UserNames's feature**.  Rename it as
        **Coorindated METplus-X.Y Support** (e.g. **Coordinated METplus-5.0 Support**).

      - Add a description: Add **Issues related to support for the METplus X.Y
        coordinated release.**

      - README: List the X.Y version number for each METplus component contained within
        the coordinated release.

      - Scroll down to the **Danger zone** and change **Visibilty** from its default value
        of **Private** to **Public**.

   - Select **Manage access** on the left hand navigation bar.

      - By default, the project creator has **Admin** access.

      - Add **Admin** access for at least 2 other users with that level of access on one
        of the METplus component repositories.

      - Add **Write** access for the **METplus** group.

   - Locate the **Custom fields** section in the left hand navigation bar

      - Select **Status** and retain the default list of options, but delete the
        **New** option by clicking the **X** to its right.

      - For **Iteration** and **Estimate**, click the 3 dots to the right of the
        **Field name** and **Delete field**.

   - Click the back arrow to return to the project page.

3. Update the project **Workflows**.

   - Click on the three dots to the right of the project name to see **More options**
     and select **Workflows**.  Modify these settings as follows.

      - Enable the **Item added to project** workflow and set the status to **Backlog**.

      - Enable the **Item reopened** workflow and set the status to **In progress**.

      - Enable the **Item closed** workflow and set the status to **Done**.

      - Enable the **Pull request merged** workflow and set the status to **Done**.

      - Leave all other workflows disabled.

   - Click the back arrow to return to the project page.

4. Create project **Views**.

   - Each view appears as a tab on the project page.  Create a new view as described below.

      - Select the **+ New view** option.

      - Click on the view name to modify it, rename it as **All Milestones**, and hit **Enter**.

      - Click on the down arrow and, under **Configuration**, select the **Fields** option. Enable
        the options for **Title**, **Repository**, **Assignees**, **Milestone**, **Status**,
        **Linked Pull Request**, and **Reviewers**. Drag and drop the items to reorder them
        as listed above.

      - In the resulting view, click the three dots in the **Milestone** column. Select the
        **Sort descending** and **Group by values** options.

      - The blue dot on the down arrow for this tab indicates that there are unsaved changes.
        Select the **Save changes** option.

   - Click on the down arrow and select **Duplicate View**.  Name/refine this views as follows.

      - View name **Closed Issues** shows issues that have been closed across all bugfix
        milestones.  Click on the 3 horizontal bars and define the filtering criteria as
        ``is:closed is:issue``. Click on the 3 dots in the **Milestone** column and
        select **Group by values**. Click **Save Changes**.

   - Delete any other views created by default by clicking the down arrow next to the view
     name and selecting **Delete view**.

5. Refine the project settings and views, as needed, based on the preferences of the support team.

6. Link the new project to each repository.

   - Navigate to the project page for each METplus component repository:

      - `METplus <https://github.com/dtcenter/METplus/projects>`_,
        `MET <https://github.com/dtcenter/MET/projects>`_,
        `METviewer <https://github.com/dtcenter/METviewer/projects>`_,
        `METexpress <https://github.com/dtcenter/METexpress/projects>`_,
        `METplotpy <https://github.com/dtcenter/METplotpy/projects>`_,
        `METcalcpy <https://github.com/dtcenter/METcalcpy/projects>`_,
        `METdataio <https://github.com/dtcenter/METdataio/projects>`_

   - Click the **Link a project** button and find/select this newly created support project.

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

Find or Create a GitHub Issue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Go to the `METplus repository <https://github.com/dtcenter/METplus>`_  and
  click on the `Issues tab <https://github.com/dtcenter/METplus/issues>`_.

* Search for an existing issue that describes the contribution.
  If one exists, take note of the issue number.
  If one cannot be found, create a
  `new Discussion <https://github.com/dtcenter/METplus/discussions/new>`_ on
  the METplus GitHub Discussions page to ask if an issue should be created.

* If creating a new issue, select the
  `"New Issue" <https://github.com/dtcenter/METplus/issues/new/choose>`_ button
  and review the categories of issues (e.g. Bug report, enhancement request,
  New feature request, New use case, Sub-Issue, Task).  Find an appropriate
  categories and click on "Get Started" next to the category.

  Create a short, but descriptive title. In the 'write' window, follow the
  directions and fill in the template.  Add any additional comments/details.
  When filling in the template, be sure to "Define the PR metadata, as
  permissions allow. Select: **Assignee(s), Project(s)**, and **Milestone**". 

  Before an issue is created, a "Project" can be selected, but there is no
  option to select a cycle.

  .. image:: figure/1Issue-before-created.png
    :width: 400	     

  After the issue is created, more options appear under the "Project" section.

  .. image:: figure/2Issue-after-created.png
    :width: 400
	    
  Click the "Status" drop down and select "Todo".

  .. image:: figure/3Issue-set-status.png
    :width: 400
	     
  Click on "+1 more" then under "Cycle", click "Choose an iteration" and
  select the current development cycle.

  .. image:: figure/4Issue-plus-one-set-cycle.png
    :width: 400
	     
  After selecting the appropriate "Cycle", be sure to remove the
  **alert: NEED CYCLE ASSIGNMENT** label, which is added by default.

  If the description of the issue is clear and does not need further
  definition, be sure to remove the **alert: NEED MORE DEFINITION**
  label, which is added by default.

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

    git fetch upstream develop
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

* If working from a fork, navigate to
  https://github.com/<github-user>/METplus where *<github-user>* is
  the user's GitHub username. If working from a branch in the dtcenter
  organization, navigate to https://github.com/dtcenter/METplus

* Click the 'Pull Requests' tab and click the green "New pull request" button.

* If working from a fork, a web page with four grey buttons should appear:

  * On the left-most button (for setting the base repository),
    make sure the 'base repository:dtcenter/METplus' is selected.

  * For the base button, make sure to select 'base:develop'.

  * For the head repository button, make sure to select
    'head repository:<your-github-user>/METplus'
    with the appropriate replacement for
    <your-github-user>.

  * For the compare button, make sure to select
    'compare:<your_feature_branch>'
    where <your_feature_branch> corresponds to the feature branch
    where the changes have been made (e.g. feature_777_wrapper_xyz).

* If working from a branch in the dtcenter organization, there should be
  two grey buttons.

  * For the **base** button, select *develop*.
  * For the **compare** button, select the feature or bugfix branch.

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

* Before a pull request is created, a "Project" can be selected, but there
  is no option to select a cycle.

  .. figure:: figure/1PR-before-created.png

  After the pull request is created, more options appear under the "Project" section.

  .. figure:: figure/2PR-after-created.png

  Click the "Status" drop down and select "Review".

  .. figure:: figure/3PR-set-status.png

  Click on "+1 more" then under "Cycle", click "Choose an iteration" and
  select the current development cycle.

  .. figure:: figure/4PR-plus-one-set-cycle.png

  To link the issue that corresponds to the pull request, click on the
  gear next to "Development," type the issue number, then select the issue
  that is displayed.

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


Reviewing a pull request
^^^^^^^^^^^^^^^^^^^^^^^^

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














