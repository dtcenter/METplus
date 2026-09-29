# METplus GitHub Labels

This directory manages the GitHub labels shared by the METplus repositories:

* `common_labels.txt` defines the labels common to all METplus repositories, one JSON object per line.
* `update_labels.sh` generates the [GitHub CLI](https://cli.github.com) (`gh`) commands to update the labels in each repository.

The script **does not change any labels directly**. It writes the commands to the `commands` sub-directory for review. Run `commands/update_labels_all_cmd.sh` to apply them.

Run `update_labels.sh --help` for the full list of options. See the [Managing Labels with update_labels.sh](https://metplus.readthedocs.io/en/develop/Contributors_Guide/github_workflow.html#managing-labels-with-update-labels-sh) section of the METplus Contributor's Guide for more details.

## Label File Format

`common_labels.txt` contains one JSON object per line, as accepted by the GitHub labels API, with an added `archived` flag:

```
{"name": "type: bug","color": "e5bf7e","description": "Fix something that is not working","archived": false}
```

* `name` is the label name, which must be unique.
* `color` is a 6-digit hex color, without the leading `#`.
* `description` is a short description of the label, which may be empty.
* `archived` is `true` for labels that are retired but kept on existing issues and pull requests, and `false` otherwise.

## Examples

Run these commands from the top-level directory of the METplus repository. They require `gh auth login`.

### 1. Add a new common label to every repository

Add a line to `common_labels.txt` to define the label:

```
{"name": "requestor: NOAA/AOML","color": "3101c1","description": "NOAA Atlantic Oceanographic and Meteorological Laboratory","archived": false}
```

Then generate the commands:

```
.github/labels/update_labels.sh --sync
```

### 2. Add a custom label to a single repository

```
.github/labels/update_labels.sh --repos metplus \
  --create "component: use case" --color 1d76db \
  --description "METplus use case issue"
```

### 3. Replace an existing common label with a new one

Edit `common_labels.txt` to mark the old label as archived and add a line to define the new one:

```
{"name": "requestor: NOAA/PSD","color": "3101c1","description": "NOAA Physical Sciences Laboratory","archived": true}
{"name": "requestor: NOAA/PSL","color": "3101c1","description": "NOAA Physical Sciences Laboratory","archived": false}
```

Then generate the commands to create the new label, add it to the open issues and pull requests which have the old label, archive the old label, and remove it from those open issues and pull requests:

```
.github/labels/update_labels.sh --sync --strip-archived \
  --assign "requestor: NOAA/PSD=>requestor: NOAA/PSL"
```

To replace a repository-specific label instead, leave `common_labels.txt` unchanged and archive the old label directly. For example, to replace the `component: docker` label in the METplus repository with a new `component: containers` label, which is created with the same color and description as the old one:

```
.github/labels/update_labels.sh --repos metplus \
  --assign   "component: docker=>component: containers" \
  --archive  "component: docker" \
  --unassign "component: docker"
```

For each example, review the generated commands, apply them by running `.github/labels/commands/update_labels_all_cmd.sh`, and commit any changes to `common_labels.txt`.
