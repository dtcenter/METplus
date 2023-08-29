---
name: Update Truth
about: Review use case differences that are caused by changes in an external repository and update truth dataset if necessary.
title: 'Update Truth: '
labels: 'alert: NEED ACCOUNT KEY, alert: NEED MORE DEFINITION, alert: NEED CYCLE ASSIGNMENT, type: update truth, priority: blocker, component: CI/CD'
assignees: ''

---

## Describe Expected Changes ##

*Write a short summary of the differences that will likely be found in the GitHub Actions testing workflow that was triggered by the pull request that warranted this issue*

## Define the Metadata ##

### Title ###
- [ ] Add a link to the pull request that warranted this issue to the issue title using format dtcenter/{REPO}#{PR_NUMBER}.

**Example:** Update Truth: For dtcenter/MET#2655

### Assignee ###

*Assign this issue to the author of the pull request that warranted this issue. Optionally assign anyone else who should review the differences in the output.*

- [ ] Select **engineer(s)** or **no engineer** required
- [ ] Select **scientist(s)** or **no scientist** required

### Labels ###
- [ ] Select **component(s)**
- [ ] Select **priority**
- [ ] Select **requestor(s)**

### Projects and Milestone ###
- [ ] Select **Repository** and/or **Organization** level **Project(s)** or add **alert: NEED CYCLE ASSIGNMENT** label
- [ ] Select **Milestone** as the next official version or **Future Versions**

## Update Truth Checklist ###
- [ ] Review the GitHub Actions workflow that was triggered by the PR merge
  - If no differences were found, note this in a comment.
  - If all of the differences are expected, note this in a comment.
  - If unexpected differences are found, revert the PR and re-open the issue.
- [ ] Close this issue.
