---
name: Update Truth
about: Review use case differences that are caused by changes in an external repository and update truth dataset if necessary.
title: 'Update Truth: '
labels: 'alert: NEED ACCOUNT KEY, alert: NEED MORE DEFINITION, alert: NEED CYCLE ASSIGNMENT, type: update truth, priority: blocker, component: CI/CD, requestor: METplus Team'
assignees: ''

---

## Describe Expected Changes ##

*Write a short summary of the differences that will likely be found in the GitHub Actions testing workflow that was triggered by the pull request that warranted this issue*

- [ ] Link to relevant issue(s):
- [ ] Link to relevant pull request(s): 

## Define the Metadata ##

### Title ###
- [ ] Define the **Title** of this issue as **Update Truth: For dtcenter/{REPO}#{PR_NUMBER}** to indicate the repository and pull request that warranted this issue.

### Assignee ###

*Assign this issue to the author of the pull request that warranted this issue. Optionally assign anyone else who should review the differences in the output.*

- [ ] Select **engineer(s)** or **no engineer** required
- [ ] Select **scientist(s)** or **no scientist** required

### Milestone and Projects ###
- [ ] Select **Milestone** as the next official version if updating truth data for the `develop` branch **OR** select next **METplus-Wrappers-X.Y.Z bugfix** version if updating truth data for a `main_vX.Y` branch.
- [ ] If updating truth data for the `develop` branch, select the **METplus-Wrappers-X.Y.Z Development** project **OR** if updating truth for a `main_vX.Y` branch, select the **Coordinated METplus-X.Y Support** project


## Update Truth Checklist ###
- [ ] Review the GitHub Actions workflow that was triggered by the PR merge
  - If no differences were found, note this in a comment.
  - If all of the differences are expected, note this in a comment.
    Include any details of how the review was performed.
  - If unexpected differences are found, the following instructions can
    help uncover potential explanations. If none of these apply and the
    source of the differences cannot be determined, contact the
    METplus wrappers lead engineer (@georgemccabe) for assistance.
    - Search for other open issues that have the label `type: update truth`
      applied by clicking on the label on this issue. Coordinate with the
      author of these issues to ensure all diffs are properly reviewed.
    - Check if any additional GitHub Actions testing workflows have been
      triggered since the workflow that corresponds to this issue was run.
      Review the latest run to ensure that there are no diffs that are
      unrelated to this issue.
    - If the incorrect differences are caused by the changes from the
      issue that warranted this issue, consider reverting the PR and
      re-opening the issue.
  - Iterate until one of the above conditions apply.
- [ ] Approve the update of the truth data
  - Contact the METplus wrappers lead engineer (@georgemccabe) or
    backup lead (@jprestop) to let them know that the truth data can
    be updated.
- [ ] Update the truth data.
      This should be handled by a METplus wrappers engineer.
      See the [instructions to update the truth data](https://metplus.readthedocs.io/en/develop/Contributors_Guide/continuous_integration.html#update-truth-data-update-truth-yml)
      for more info.
- [ ] Close this issue.
