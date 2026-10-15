# METplus Agent Instructions

Instructions for AI coding agents working in this repository.
See the [Contributor's Guide](https://metplus.readthedocs.io/en/latest/Contributors_Guide/index.html)
for full details.

## Branches

- Feature branches are named `feature_<GitHub issue number>_<brief_description>`,
  e.g. `feature_777_wrapper_xyz`. Bugfix branches use `bugfix_` instead.
- Pull requests normally target `develop`. Bugfixes to a release also target
  the matching `main_vX.Y` branch.

## Before creating a pull request

1. **Turn off use case tests.** In `.github/parm/use_case_groups.json`, every
   `"run"` value must be `false`. Developers set groups to `true` on feature
   branches so those use cases run on every push for testing; this must be
   undone before the PR. To find any that are on:

   ```bash
   jq -r '.[] | select(.run == true) | "\(.category): \(.index_list)"' .github/parm/use_case_groups.json
   ```

   Set them to `false`, commit, and push **before** creating the PR. The
   pull request is built from the pushed branch, so a local-only change does
   not count. The `Check Use Case Groups` workflow fails any PR to `develop`
   or `main_vX.Y` that still has a group set to `true`.

2. **Title the PR after the branch**, e.g. `Feature #777 wrapper_xyz` for
   branch `feature_777_wrapper_xyz`.

3. **Use the PR template** in `.github/pull_request_template.md`. Fill in what
   you know (summary, testing performed) and leave the remaining items for
   the developer.
