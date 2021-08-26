---
name: New feature request
about: Make it do something new
title: ''
labels: 'alert: NEED ACCOUNT KEY, alert: NEED MORE DEFINITION, alert: NEED PROJECT ASSIGNMENT, type: new feature'
assignees: ''

---

*Replace italics below with details for this issue.*

## Describe the New Feature ##
*Provide a description of the new feature request here.*

### Acceptance Testing ###
*List input data types and sources.*
*Describe tests required for new functionality.*

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

### Projects and Milestone ###
- [ ] Select **Repository** and/or **Organization** level **Project(s)** or add **alert: NEED PROJECT ASSIGNMENT** label
- [ ] Select **Milestone** as the next official version or **Future Versions**

## Define Related Issue(s) ##
Consider the impact to the other METplus components.
- [ ] [METplus](https://github.com/dtcenter/METplus/issues/new/choose), [MET](https://github.com/dtcenter/MET/issues/new/choose), [METdatadb](https://github.com/dtcenter/METdatadb/issues/new/choose), [METviewer](https://github.com/dtcenter/METviewer/issues/new/choose), [METexpress](https://github.com/dtcenter/METexpress/issues/new/choose), [METcalcpy](https://github.com/dtcenter/METcalcpy/issues/new/choose), [METplotpy](https://github.com/dtcenter/METplotpy/issues/new/choose)

## New Feature Checklist ##
See the [METplus Workflow](https://metplus.readthedocs.io/en/latest/Contributors_Guide/github_workflow.html) for details.
- [ ] Complete the issue definition above, including the **Time Estimate** and **Funding source**.
- [ ] Fork this repository or create a branch of **develop**.
Branch name: `feature_<Issue Number>_<Description>`
- [ ] Complete the development and test your changes.
- [ ] Add/update log messages for easier debugging.
- [ ] Add/update unit tests.
- [ ] Add/update documentation.
- [ ] Push local changes to GitHub.
- [ ] Submit a pull request to merge into **develop**.
Pull request: `feature <Issue Number> <Description>`
- [ ] Define the pull request metadata, as permissions allow.
Select: **Reviewer(s)** and **Linked issues**
Select: **Repository** level development cycle **Project** for the next official release
Select: **Milestone** as the next official version
- [ ] Iterate until the reviewer(s) accept and merge your changes.
- [ ] Delete your fork or branch.
- [ ] Close this issue.
