# METplus repository conventions

Guidance for AI coding agents working in this repository, and a useful summary
for human contributors.

## Read the Contributor's Guide first

The [METplus Contributor's
Guide](https://metplus.readthedocs.io/en/latest/Contributors_Guide/index.html),
whose source is `docs/Contributors_Guide/` in this repository, governs work
here. Its [GitHub
Workflow](https://metplus.readthedocs.io/en/latest/Contributors_Guide/github_workflow.html)
chapter covers how issues, labels, milestones, and project boards are used, how
branches are named, and how pull requests are opened, reviewed, and merged.
Follow it rather than inventing a process.

This file is the short form: the steps that are easy to miss. The guide is
authoritative. Where this file and the guide genuinely conflict, say so in the
pull request rather than silently following one.

## Branches

- Feature branches are named `feature_<GitHub issue number>_<brief_description>`,
  e.g. `feature_777_wrapper_xyz`.
- Bugfix branches also name the branch they will merge into, after the issue
  number: `bugfix_<GitHub issue number>_develop_<brief_description>` or
  `bugfix_<GitHub issue number>_main_vX.Y_<brief_description>`, e.g.
  `bugfix_777_develop_wrapper_xyz` and `bugfix_777_main_v6.2_wrapper_xyz`.
- Pull requests normally target `develop`. Bugfixes to a release also target
  the matching `main_vX.Y` branch.

## Code and Python packages

Before changing Python code or adding a Python package, read and follow
`docs/Contributors_Guide/coding_standards.rst`. It covers code style and where
to list a new package. Do not add a new package without approval from the
developers. A new package must be listed in the [METplus Components Python
Requirements](https://metplus.readthedocs.io/en/latest/Users_Guide/appendixA.html#metplus-components-python-packages)
table.

## New wrappers

Follow every step in `docs/Contributors_Guide/create_wrapper.rst`.

## Configuration variables

A new or renamed configuration variable needs an entry in
`docs/Users_Guide/glossary.rst`. If a specific wrapper uses it, it must also
be added to that wrapper's section of `docs/Users_Guide/wrappers.rst`. If it is
a general setting, consider adding it to
`docs/Users_Guide/systemconfiguration.rst`. A change that requires users to modify
existing configuration files needs an entry in the upgrade instructions in
`docs/Users_Guide/release-notes.rst`.

## Unit tests

Before adding or changing unit tests, read and follow
`docs/Contributors_Guide/testing.rst`. It covers running the tests and using
pytest markers.

## Use cases

Before adding or changing a use case, read and follow
`docs/Contributors_Guide/add_use_case.rst`.

When a pull request that adds a use case is approved and ready to merge,
suggest running `/merge-use-case-pr <number>`. It merges the pull request,
waits for the testing run on the base branch, checks that the only differences
are in the new use cases, and updates the truth data. Merging and updating the
truth data need write access to dtcenter/METplus; a contributor without it
should ask the reviewer to run it.

## Before creating a pull request

1. **Turn off use case tests.** In `.github/parm/use_case_groups.json`, every
   `"run"` value must be `false`. Developers set groups to `true` on feature
   branches so those use cases run on every push for testing; this must be
   undone before the pull request. To find any that are on:

   ```bash
   jq -r '.[] | select(.run == true) | "\(.category): \(.index_list)"' .github/parm/use_case_groups.json
   ```

   Set them to `false`, commit, and push **before** creating the pull request.
   The `Check Use Case Groups` workflow fails any pull request to `develop` or
   `main_vX.Y` that still has a group set to `true`.

2. **Title the pull request after the branch**, replacing the underscores in
   the description with spaces, e.g. `Feature #777 wrapper xyz` for branch
   `feature_777_wrapper_xyz`. Spell out an abbreviation only when its meaning
   is clear, for example from the issue title (`sq` becomes `SonarQube` for an
   issue about SonarQube findings). If it is unclear, leave it as written.

3. **Use the pull request template** in `.github/pull_request_template.md`.
   Fill in what you know (summary, testing performed) and leave the remaining
   items for the developer. Change `- [ ]` to `- [x]` on every item that has
   been answered or filled in: a `[Yes or No]` replaced with an answer, a
   "Describe..." item with text after it, a review date set. Leave unanswered
   items unchecked, along with the action items under "Pull Request
   Checklist", which record steps taken rather than answers given. Check items
   again whenever more answers are supplied later.

4. **Set the project and milestone.** A pull request into `develop` belongs to
   the upcoming release. Take its version from `metplus/VERSION` on `develop`,
   dropping any suffix such as `-rc1-dev` (e.g. `13.0.0-rc1-dev` gives
   `13.0.0`). Add the pull request to the `METplus-<X.Y> Development` project
   and the `METplus-<X.Y.Z>` milestone, e.g. `METplus-13.0 Development` and
   `METplus-13.0.0`. If either does not exist, or the milestone is closed, ask
   rather than picking another.
