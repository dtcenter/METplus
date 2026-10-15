# METplus Agent Instructions

Instructions for AI coding agents working in this repository.
See the [Contributor's Guide](https://metplus.readthedocs.io/en/latest/Contributors_Guide/index.html)
for full details.

## Branches

- Feature branches are named `feature_<GitHub issue number>_<brief_description>`,
  e.g. `feature_777_wrapper_xyz`. Bugfix branches use `bugfix_` instead.
- Pull requests normally target `develop`. Bugfixes to a release also target
  the matching `main_vX.Y` branch.

## Python packages

- Follow PEP8.
- Do not add a new Python package without approval from the developers.
  METplus must run on operational HPCs, where every package needs approval.
- What to update depends on where the package is used:
  - **METplus wrappers code** (under `metplus/`): add the package to
    `requirements.txt` and to the package table in
    `docs/Users_Guide/appendixA.rst`.
  - **A use case** (under `parm/use_cases/model_applications/`): add the
    package to the table in `docs/Users_Guide/appendixA.rst` only. Do
    **not** add it to `requirements.txt`. Use cases can depend on packages
    that METplus wrappers do not need.

## New wrappers

Follow every step in `docs/Contributors_Guide/create_wrapper.rst`.

## Unit tests

- Decorate each new test with a `@pytest.mark.<marker>` marker. The markers
  are defined under `[tool.pytest.ini_options]` in `pyproject.toml`; register
  any new marker there.

## Use cases

Before adding or changing a use case, read and follow
`docs/Contributors_Guide/add_use_case.rst`. It covers:

- file and directory naming
- what a use case config may and may not set
- words to avoid in log messages
- registering a new use case in the test suite and documentation

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

2. **Title the PR after the branch**, replacing the underscores in the
   description with spaces, e.g. `Feature #777 wrapper xyz` for branch
   `feature_777_wrapper_xyz`. Spell out an abbreviation only when its
   meaning is clear, for example from the issue title (`sq` becomes
   `SonarQube` for an issue about SonarQube findings). If it is unclear,
   leave it as written.

3. **Use the PR template** in `.github/pull_request_template.md`. Fill in what
   you know (summary, testing performed) and leave the remaining items for
   the developer.
