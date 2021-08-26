---
name: Bug report
about: Fix something that's not working
title: ''
labels: 'alert: NEED ACCOUNT KEY, alert: NEED MORE DEFINITION, alert: NEED PROJECT ASSIGNMENT, type: bug'
assignees: ''

---

*Replace italics below with details for this issue.*

## Describe the Problem ##
*Provide a clear and concise description of the bug here.*

### Expected Behavior ###
*Provide a clear and concise description of what you expected to happen here.*

### Environment ###
Describe your runtime environment:
*1. Machine: (e.g. HPC name, Linux Workstation, Mac Laptop)*
*2. OS: (e.g. RedHat Linux, MacOS)*
*3. Software version number(s)*

### To Reproduce ###
Describe the steps to reproduce the behavior:
*1. Go to '...'*
*2. Click on '....'*
*3. Scroll down to '....'*
*4. See error*
*Post relevant sample data following these instructions:*
*https://dtcenter.org/community-code/model-evaluation-tools-met/met-help-desk#ftp*

### Relevant Deadlines ###
*List relevant project deadlines here or state NONE.*

### Funding Source ###
*Define the source of funding and account keys here or state NONE.*

## Define the Metadata ##

### Assignee ###
- [ ] Select **engineer(s)** or **no engineer** required
- [ ] Select **scientist(s)** or **no scientist** required

### Labels ###
- [ ] Select **component(s)**
- [ ] Select **priority**
- [ ] Select **requestor(s)**

### Projects and Milestone ###
- [ ] Select **Organization** level **Project** for support of the current coordinated release
- [ ] Select **Repository** level **Project** for development toward the next official release or add **alert: NEED PROJECT ASSIGNMENT** label
- [ ] Select **Milestone** as the next bugfix version

## Define Related Issue(s) ##
Consider the impact to the other METplus components.
- [ ] [METplus](https://github.com/dtcenter/METplus/issues/new/choose), [MET](https://github.com/dtcenter/MET/issues/new/choose), [METdatadb](https://github.com/dtcenter/METdatadb/issues/new/choose), [METviewer](https://github.com/dtcenter/METviewer/issues/new/choose), [METexpress](https://github.com/dtcenter/METexpress/issues/new/choose), [METcalcpy](https://github.com/dtcenter/METcalcpy/issues/new/choose), [METplotpy](https://github.com/dtcenter/METplotpy/issues/new/choose)

## Bugfix Checklist ##
See the [METplus Workflow](https://metplus.readthedocs.io/en/latest/Contributors_Guide/github_workflow.html) for details.
- [ ] Complete the issue definition above, including the **Time Estimate** and **Funding Source**.
- [ ] Fork this repository or create a branch of **main_\<Version>**.
Branch name: `bugfix_<Issue Number>_main_<Version>_<Description>`
- [ ] Fix the bug and test your changes.
- [ ] Add/update log messages for easier debugging.
- [ ] Add/update unit tests.
- [ ] Add/update documentation.
- [ ] Push local changes to GitHub.
- [ ] Submit a pull request to merge into **main_\<Version>**.
Pull request: `bugfix <Issue Number> main_<Version> <Description>`
- [ ] Define the pull request metadata, as permissions allow.
Select: **Reviewer(s)** and **Linked issues**
Select: **Organization** level software support **Project** for the current coordinated release
Select: **Milestone** as the next bugfix version
- [ ] Iterate until the reviewer(s) accept and merge your changes.
- [ ] Delete your fork or branch.
- [ ] Complete the steps above to fix the bug on the **develop** branch.
Branch name:  `bugfix_<Issue Number>_develop_<Description>`
Pull request: `bugfix <Issue Number> develop <Description>`
Select: **Reviewer(s)** and **Linked issues**
Select: **Repository** level development cycle **Project** for the next official release
Select: **Milestone** as the next official version
- [ ] Close this issue.
