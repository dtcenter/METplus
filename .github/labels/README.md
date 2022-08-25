METplus Repository Labels
=========================

The contents of this directory define GitHub issue labels that are common
to all of the METplus-related repositories in the DTCenter organization.

These labels should be defined consistently across all of the repositories.
However, individual repositories are encouraged to add labels specific to
their codebase.

Labels are defined for the following categories:
- "alert" flags issues for discussion
- "component" classifies the type of work (customization encouraged)
- "priority" defines the priority level
- "reporting" defines project management reporting requirements
- "requestor" identifies the relevant organization(s)
- "type" corresponds to GitHub issue templates (customization allowed)

In general, new "alert", "priority", "reporting", and "requestor" labels
should be added to this common location and defined consistently across
all the METplus repositories.

Each repository should define a relevant set of "component" labels since
they will vary widely depending on the code base.

New "type" labels should only be added to a repository when a corresponding
GitHub issue template is also added.

Sample commands for processing all METplus repos: 

```
# List of METplus repositories
REPO_LIST="metplus met metplotpy metcalcpy metdataio metviewer \
                      metexpress metplus-training metplus-internal \
                      metbaseimage";

# Build commands to add/update common labels
for repo in ${REPO_LIST}; do
  echo $repo;
  ./post_patch_labels.sh [user] [auth] $repo common_labels.txt;
done

# Build commands to delete extra labels
for repo in ${REPO_LIST}; do
  echo $repo;
  ./delete_labels.sh [user] [auth] $repo;
done
```

The resulting commands are written to bash shell scripts in the commands
directory. Those commands should be carefully reviewed before executing them.

