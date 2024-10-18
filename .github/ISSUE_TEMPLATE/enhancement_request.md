---
name: Enhancement request
about: Improve something that it's currently doing
title: 'Enhancement: '
labels: 'alert: NEED ACCOUNT KEY, alert: NEED MORE DEFINITION, alert: NEED CYCLE ASSIGNMENT, type: enhancement'
assignees: ''

---

*Replace italics below with details for this issue.*

## Describe the Enhancement ##
*Provide a description of the enhancement request here.*

### Time Estimate ###
*Estimate the amount of work required here.*
*Issues should represent approximately 1 to 3 days of work.*

### Sub-Issues ###
Consider breaking the enhancement down into sub-issues.
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
- [ ] Review default **alert** labels
- [ ] Select **component(s)**
- [ ] Select **priority**
- [ ] Select **requestor(s)**

### Milestone and Projects ###
- [ ] Select **Milestone** as a **METplus-Wrappers-X.Y.Z** version, **Consider for Next Release**, or **Backlog of Development Ideas**
- [ ] For a **METplus-Wrappers-X.Y.Z** version, select the **METplus-Wrappers-X.Y.Z Development** project

## Define Related Issue(s) ##
Consider the impact to the other METplus components.
- [ ] [METplus](https://github.com/dtcenter/METplus/issues/new/choose), [MET](https://github.com/dtcenter/MET/issues/new/choose), [METdataio](https://github.com/dtcenter/METdataio/issues/new/choose), [METviewer](https://github.com/dtcenter/METviewer/issues/new/choose), [METexpress](https://github.com/dtcenter/METexpress/issues/new/choose), [METcalcpy](https://github.com/dtcenter/METcalcpy/issues/new/choose), [METplotpy](https://github.com/dtcenter/METplotpy/issues/new/choose)

## Enhancement Checklist ##
See the [METplus Workflow](https://metplus.readthedocs.io/en/latest/Contributors_Guide/github_workflow.html) for details.
- [ ] Complete the issue definition above, including the **Time Estimate** and **Funding Source**.
- [ ] Fork this repository or create a branch of **develop**.
Branch name: `feature_<Issue Number>_<Description>`
- [ ] Complete the development and test your changes.
- [ ] Add/update log messages for easier debugging.
- [ ] Add/update unit tests.
- [ ] Add/update documentation.
- [ ] Add any new Python packages to the [METplus Components Python Requirements](https://metplus.readthedocs.io/en/develop/Users_Guide/appendixA.html#metplus-components-python-packages) table.
- [ ] For any new datasets, an entry to the [METplus Verification Datasets Guide](https://metplus.readthedocs.io/en/latest/Verification_Datasets/index.html).
- [ ] Push local changes to GitHub.
- [ ] Submit a pull request to merge into **develop**.
Pull request: `feature <Issue Number> <Description>`
- [ ] Define the pull request metadata, as permissions allow.
Select: **Reviewer(s)** and **Development** issue
Select: **Milestone** as the next official version
Select: **METplus-Wrappers-X.Y.Z Development** project for development toward the next official release
- [ ] Iterate until the reviewer(s) accept and merge your changes.
- [ ] Delete your fork or branch.
- [ ] Close this issue.
