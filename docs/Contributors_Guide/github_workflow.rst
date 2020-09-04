GitHub Workflow
===============

**How METplus releases are created**

| The branching model employed by the METplus GitHub repository is similar to that
| described in the following document:
|
|      https://nvie.com/posts/a-successful-git-branching-model/
|
| where new or updated code is created on a 'feature' branch that is based on the NCAR/METplus GitHub 'develop' branch.
| The feature branch is named after the corresponding GitHub issue:
|       *feature_<Github Issue number>_<brief_description>*
|
| When work is complete, the code in the feature branch is merged into the develop branch.  When a release candidate
| for METplus has been determined, then the develop branch is used to create a master_vx.y release of
| METplus, which includes data tarballs for use in running use cases.


**Sequence of Events - Contributing Code**

*Pre-requisite:*

| Set up a GitHub repository account if you do not already have one, and log into your account.  For
| more information about GitHub accounts, please refer to the following
|
|   https://help.github.com/en/github/getting-started-with-github/signing-up-for-a-new-github-account
|

| Workflow Overview:
|
|  A contributor to METplus will do the following:
|    1.  Create a GitHub Issue to track the new contribution
|    2.  Fork the NCAR/METplus repository
|    3.  Clone the fork to local repository
|    4.  Set upstream remote (to assist in keeping upstream and local repositories synchronized)
|    5.  Generate a feature branch from the 'develop' branch where new development will take place
|    6.  Make changes to code in the feature branch
|    7.  Commit changes to feature branch (limit one change per commit)
|    8.  Push feature branch to GitHub
|    9.  Open a pull request from feature branch to original repo (from which you forked, in step 2 above)
|   10.  Clean up after pull request has been merged by METplus core team member/approval committee
|
|
|
| 1. Create a GitHub Issue that reflects what needs to be done
|
|    * Go to https://github.com/dtcenter/METplus  and click on the **Issues** link, to the right of the **Code** tab
|
|      * Click on the green **New issue** button
|
|      * Write a description of the task and attach appropriate values to Assignee, Labels, and Milestone links
|      located on the right hand side of the page
|
|
| 2.  Fork the NCAR/METplus repository
|     Retrieve a copy of the source code by forking the NCAR/METplus repository into your own GitHub repository. Click
|     on the 'Fork' button in the upper right hand side of the web page at https://github.com/dtcenter/METplus.
|     Click on the appropriate GitHub account when presented with the pop-up window with the question
|          'Where should we fork METplus?'
|
|     Your web page will refresh to your GitHub repository at https://github.com/<your-github-user>/METplus
|     You now have an entire copy of the NCAR/METplus Github repository.
|
|
| 3. Clone the fork to a local repository, ie. copy the source code to the directory where you will be doing your
|    work. 
|       'cd' to the directory where you wish to do your work. From the command line, enter the following:
|            *git clone https://github.com/<your-github-account>/METplus*
|
|       'cd' to the METplus directory.  Now you are working in your local METplus repository.
|
| 4. Add a remote named origin to the clone of your local Git repository.  Thie is how you will push changes to the
|    repository you forked in step 1:
|        *git remote add upstream https://github.com/dtcenter/METplus*
|
|    To verify that the upstream and origin are correct, at the command line enter:
|        *git remote -v*
|
|    You should see something like the following:
|
|         origin	https://github.com/<github-username>/METplus (fetch)
|         origin	https://github.com/<github-username>/METplus (push)
|         upstream	https://github.com/dtcenter/METplus (fetch)
|         upstream	https://github.com/dtcenter/METplus (push)
|
|         where <github-username> is your GitHub user account name
|
|
| 5. Create a feature branch in the NCAR/METplus GitHub repository following this naming convention:
|
|        *feature_<Github Issue number>_<brief_description>*
|
|        So for example, for GitHub issue #777 that creates new wrapper xyz, the feature branch would be named:
|             *feature_777_wrapper_xyz*
|
|        Create your feature branch based off the develop branch:
|            *git checkout develop*
|
|        Verify that you are currently working in the develop branch by entering the following:
|            *git branch*
|
|
|             You should see something like the following:
|               * develop
|                master_v2.2    
|             
|             The asterisk, * indicates the currently active branch.
|
|        At the command line, create and checkout the feature branch:
|            *git checkout -b feature_777_wrapper_xyz*
|
|        except replace *feature_777_wrapper_xyz* with your feature branch name.
|
|        Verify that you are working in the correct branch by entering:
|            *git branch*
|
|        You should see something like the following:
|             develop
|             master_v2.2
|             * feature_777_wrapper_xyz
|
|        where the asterisk, * indicates which branch is currently in use/checked out.
|
|
| 6.  Make changes to your feature branch and commit changes to your local repository (i.e. where you are doing
|     your work/local computer)
|
|     Create your code following the coding standards in the Coding Standards section of the Contributor's Guide.
|     In addition, please provide some tests for your code using the pytest framework and provide user documentation
|     describing what your code does and provide any necessary data.
|
|
|     Keep your fork in sync:
|         While you are working, it is highly likely that changes are occurring to the original repository.  This
|         may impact your work.  Periodically/regularly use these commands to keep your fork in sync with the
|         original repository:
|            *git pull upstream develop*
|
|            *git push origin develop*
|
|            The first command pulls changes from the original repository.
|            i.e. the https://github.com/dtcenter/METplus
|            repository that you see when you perform *git remote -v* and that you set to upstream in
|            step #4 above.  The second command pushes those changes to your forked repository.
|
|     Commit any new files:
|         *git add <filename>*
|           Perform this step only if this file is newly created and does not yet exist in your repository.
|
|         *git commit <filename>*
|           A popup window will appear, where you will enter a description of this commit, using the editor you selected
|           when you set up your Git account.  Please refer to the following on configuring your
|           Git account: https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup
|
|           For the first line of your commit comment, enter a brief description, such as the GitHub Issue number
|           and a brief description.  On the second and subsequent lines, provide a detailed description of the
|           changes/additions you made.
|
|
|         **Note**: It is a best practice to commit one change per commit, rather than wait
|                   until you have multiple changes to include in one commit.
|
| 7.  Push your changes to GitHub
|
|         *git push origin <your feature>*
|           to push your changes to the origin (i.e. to your https://github.com/<github-username>/METplus repository)
|
|           Replace <your feature> with the name of your feature branch, e.g.:
|               *git push origin feature_777_wrapper_xyz*
|
|
| 8.  Open a pull request using your browser
|
|     To request to have your changes be incorporated into the remote repository
|     (i.e. https://github.com/dtcenter/METplus repository).
|
|     The METplus maintainers will need to approve the request and then merge your files into the main
|     repository's develop branch.  The develop branch will then be used to create a release candidate.
|
|        * In your browser, navigate to https://github.com/<github-username>/METplus
|
|        * Click on the green 'Compare & pull request' button
|
|        * A web page appears with four grey buttons:
|
|            * On the left-most button (for setting the base repository), make sure you have selected
|              'base repository:NCAR/METplus'
|
|            * For the base button, make sure you have selected 'base:develop'
|
|            * For the head repository button, make sure you have selected 'head repository:<github_username>/METplus'
|              where <github_username> is your GitHub account name.
|
|            * For the compare button, make sure you have selected 'compare:<your_feature_branch>'
|              where <your_feature_branch> corresponds to the feature branch where you have been making your
|              changes (e.g. feature_777_wrapper_xyz).
|
|            * In the 'write' window, add any additional comments/details.  In this window are the comments you
|              created when you committed your changes in step 6 above.
|
|              *  You can scroll down to see what changes were made to the file you committed.
|
|            * When everything looks satisfactory, click on the green 'Create pull request' button.
|
|            * Someone from the METplus maintainer group will accept the pull request (if everything meets acceptance criteria)
|              and merge your code into the remote repository's develop branch.
|
|
| 9.  Clean up after a successful merged pull request
|
|     After the METplus maintainers have accepted your changes and have merged them into the main repository, update
|     your local clone by pulling changes from the original repository's (i.e. the https://github.com/dtcenter/METplus repository)
|     develop branch:
|
|     Checkout your develop branch:
|           *git checkout develop*
|
|     Verify that you are now working from the develop branch:
|           *git branch*
|
|     Merge changes from the upstream develop branch with your local develop branch:
|           *git pull upstream develop*
|
|     Your local cloned repository should now have all the latest changes from the original repository's develop branch.
|
|     Now you can delete your feature branch:
|
|          *git branch -D <branch name>*
|          *git push --delete origin <branch name>*
|
|     where <branch name> is your feature branch name, e.g. feature_777_wrapper_xyz
|
|         e.g. git push --delete origin feature_777_wrapper_xyz
|
|     You can verify that your feature branch has been successfully removed/deleted via your web browser.
|     Navigate to https://github.com/<github-username>/METplus and under the 'Branch' pulldown menu, you
|     should no longer find your feature branch as a selection.
|
|
| *Re-cap*:
|   You've created a feature branch, made changes, committed those changes to the repository, pushed them to GitHub,
|   opened a pull request,had your changes merged by the repository maintainers, and finally performed some clean-up.
















