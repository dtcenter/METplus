---
name: Update Truth
about: Review use case differences that are caused by changes in an external repository and update truth dataset if necessary.
title: 'Update Truth: '
labels: 'alert: NEED ACCOUNT KEY, alert: NEED MORE DEFINITION, alert: NEED CYCLE ASSIGNMENT, type: update truth, priority: blocker, component: CI/CD, requestor: METplus Team'
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
    Include any details of how the review was performed.
  - If unexpected differences are found, revert the PR and re-open the issue.
    Iterate until one of the above conditions apply.
- [ ] Confirm that the truth data can be updated
  - Confirm with the METplus wrappers lead engineer (@georgemccabe) or
    backup lead (@jprestop) that the truth data can be updated.
  - If the engineers are unavailable, follow these instructions to confirm
    that the update can be performed:
    - Search for other open issues that have the label `type: update truth`
      applied by clicking on the label on this issue. Coordinate with the
      author of these issues to ensure all diffs are properly reviewed.
    - Check if any additional GitHub Actions testing workflows have been
      triggered since the workflow that corresponds to this issue was run.
      Review the latest run to ensure that there are no diffs that are
      unrelated to this issue.
- [ ] Update the truth data.
      This may be handled by a METplus wrappers engineer.
      See the (instructions to update the truth data)[https://metplus.readthedocs.io/en/develop/Contributors_Guide/continuous_integration.html#update-truth-data-update-truth-data-yml]
      for more info.
- [ ] Close this issue.
