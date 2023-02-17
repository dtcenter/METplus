---
name: New use case
about: Add a new use case
title: 'New Use Case: '
labels: 'alert: NEED ACCOUNT KEY, alert: NEED MORE DEFINITION, alert: NEED PROJECT ASSIGNMENT, type: new use case'
assignees: ''

---

*Replace italics below with details for this issue.*

## Describe the New Use Case ##
*Provide a description of the new feature request here.*

### Use Case Name and Category ###
*Provide use case name, following Contributor's Guide naming template, and list which category the use case will reside in.*
*If a new category is needed for this use case, provide its name and brief justification*

### Input Data ###
*List input data types and sources.*
*Provide a total input file size, keeping necessary data to a minimum.* 

### Acceptance Testing ###
*Describe tests required for new functionality.*
*As use case develops, provide a run time here*

### Time Estimate ###
*Estimate the amount of work required here.*
*Issues should represent approximately 1 to 3 days of work.*

### Sub-Issues ###
Consider breaking the new feature down into sub-issues.
- [ ] *Add a checkbox for each sub-issue here.*

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
- [ ] Select **privacy**

### Projects and Milestone ###
- [ ] Select **Repository** and/or **Organization** level **Project(s)** or add **alert: NEED PROJECT ASSIGNMENT** label
- [ ] Select **Milestone** as the next official version or **Future Versions**

## Define Related Issue(s) ##
Consider the impact to the other METplus components.
- [ ] [METplus](https://github.com/dtcenter/METplus/issues/new/choose), [MET](https://github.com/dtcenter/MET/issues/new/choose), [METdataio](https://github.com/dtcenter/METdataio/issues/new/choose), [METviewer](https://github.com/dtcenter/METviewer/issues/new/choose), [METexpress](https://github.com/dtcenter/METexpress/issues/new/choose), [METcalcpy](https://github.com/dtcenter/METcalcpy/issues/new/choose), [METplotpy](https://github.com/dtcenter/METplotpy/issues/new/choose)

## New Use Case Checklist ##
See the [METplus Workflow](https://metplus.readthedocs.io/en/latest/Contributors_Guide/github_workflow.html) for details.
- [ ] Complete the issue definition above, including the **Time Estimate** and **Funding source**.
- [ ] Fork this repository or create a branch of **develop**.
Branch name: `feature_<Issue Number>_<Description>`
- [ ] Complete the development and test your changes.
- [ ] Add/update log messages for easier debugging.
- [ ] Add/update unit tests.
- [ ] Add/update documentation.
- [ ] Add any new Python packages to the [METplus Components Python Requirements](https://metplus.readthedocs.io/en/develop/Users_Guide/overview.html#metplus-components-python-requirements) table.
- [ ] Push local changes to GitHub.
- [ ] Submit a pull request to merge into **develop**.
Pull request: `feature <Issue Number> <Description>`
- [ ] Define the pull request metadata, as permissions allow.
Select: **Reviewer(s)** and **Development** issues
Select: **Repository** level development cycle **Project** for the next official release
Select: **Milestone** as the next official version
- [ ] Iterate until the reviewer(s) accept your changes. Merge branch into **develop**.
- [ ] Create a second pull request to merge **develop** into **develop-ref**, following the same steps for the first pull request.
- [ ] Delete your fork or branch.
- [ ] Close this issue.
