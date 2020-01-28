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
| When work is complete, the code in the feature branch is merged into the 'develop' branch.  When a release candidate
| for METplus has been determined, then the develop branch is used to create a master_vx.y release of
| METplus, which includes data tarballs for use in running use cases.


**Sequence of Events- Contributing Code**

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
|    * Go to https://github.com/NCAR/METplus  and click on the **Issues** link, to the right of the **Code** tab
|
|      * Click on the green **New issue** button
|
|      * Write a description of the task and attach appropriate values to Assignee, Labels, and Milestone links
|      located on the right hand side of the page
|
|
|
|
| 2.  Fork the NCAR/METplus
|     Retrieve a copy of the source code by forking the NCAR/METplus repository into your own GitHub repository by clicking
|     on the 'Fork' button in the upper right hand side of the web page at https://github.com/NCAR/METplus.
|     Click on the appropriate GitHub account when presented with the pop-up window with the question
|          'Where should we fork METplus?'
|
|     Your web page will refresh to your GitHub repository at https://github.com/<your-github-user>/METplus
|     You now have an entire copy of the NCAR/METplus Github repository.
|
|
| 3. Clone the fork to a local repository, ie. copy the source code to the directory where you will be doing your
|    work. From the command line, enter the following:
|        *git clone https://github.com/<your-github-account>/METplus*
|
|
| 4. Add a remote named origin to the clone of your local Git repository.  Thie is how you will push changes to the
|    repository you forked in step 1:
|        *git remote add upstream https://github.com/NCAR/METplus*
|
|    To verify that the upstream and origin are correct, at the command line enter:
|        *git remote -v*
|
|    You should see something like the following:
|
|         origin	https://github.com/<github-username>/METplus (fetch)
|         origin	https://github.com/<github-username>/METplus (push)
|         upstream	https://github.com/NCAR/METplus (fetch)
|         upstream	https://github.com/NCAR/METplus (push)
|
|         where <github-username> is your GitHub user account name
|
| 5. Create a feature branch in the NCAR/METplus GitHub repository following this naming convention:
|
|        *feature_<Github Issue number>_<brief_description>*
|
|        So for example, for GitHub issue #777 that creates new wrapper xyz, the feature branch would be:
|             *feature_777_wrapper_xyz*
|
|        At the command line, create and checkout the feature branch:
|            *git checkout -b feature_777_wrapper_xyz*
|
|        replacing *feature_777_wrapper_xyz* with your feature branch name.
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
| 6.  Make changes to your feature branch
|     While you are making changes to your feature branch, please keep in mind that other contributors are also
|     making changes and committing them to upstream develop
|     (i.e.the GitHub repository at https://github.com/NCAR/METplus).
|     As a result, your forked repository can become out of synchronization, requiring you to regularly synchronize
|     your feature branch with the upstream develop.
|
| 7.  Commit changes to your feature branch.
|     After you have created your code following the coding standards and created accompanying tests and documentation,
|     you are ready to commit your changes to your feature branch.  It is a best practice to commit one change
|     per commit, rather than wait until you have multiple changes to include in one commit.













Checkout the 'develop' branch:

         git checkout develop

Create a feature branch from the develop branch (above):

* e.g. for GitHub issue 777 that refactors xyz wrapper:

         git branch feature_777_refactor_xyz_wrapper




3.  Make code changes to the feature branch you created in step 2 above.


4.  Frequently commit your changes to your feature branch, and frequently merge any updates from the

    develop branch.

     commit <file-to-commit>




**Retrieving Source Code as External Contributor**

add content here...




