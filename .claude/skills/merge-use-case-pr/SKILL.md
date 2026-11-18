---
name: merge-use-case-pr
description: Merge an approved METplus pull request that adds use cases, confirm the resulting develop run differs only in the new use cases, then update the truth data
argument-hint: <METplus pull request number>
# Merges pull requests and updates truth data, so run it only when a user
# invokes it explicitly with /merge-use-case-pr.
disable-model-invocation: true
---

Merge the dtcenter/METplus pull request `$ARGUMENTS`, which adds one or more new
use cases, and carry it through the truth data update that the Contributor's
Guide describes under "After the Pull Request is Approved" in
`docs/Contributors_Guide/add_use_case.rst` and "Update Reference Branch" in
`docs/Contributors_Guide/continuous_integration.rst`.

Run every `gh` command with `-R dtcenter/METplus`. Below, `<base>` is the pull
request's base branch: `develop`, or `main_vX.Y` for a bugfix to a release.
Its reference branch is `<base>-ref`.

Invoking this skill is the user's approval for every step after the merge in
step 3: running Update Reference Branch, and merging the pull request it opens
into `<base>-ref` without review. It is **not** approval for the merge in
step 3 itself, which needs its own yes. Stop at every gate below rather than
working around it.

### 1. Check access and the pull request

- The user needs write access to merge and to run workflows:
  `gh api repos/dtcenter/METplus --jq .permissions`. If `push` is false, stop
  and tell them the person who merges the pull request, usually its reviewer,
  should run `/merge-use-case-pr`.
- `gh pr view $ARGUMENTS --json state,isDraft,baseRefName,reviewDecision,mergeable,isCrossRepository,milestone,projectItems`.
  Stop unless it is open, not a draft, approved, and mergeable, with a base of
  `develop` or `main_vX.Y`.
- Every `"run"` value in `.github/parm/use_case_groups.json` on the pull
  request head must be `false`. Stop if not.

### 2. Identify the new use case groups and review the pull request run

Compare `.github/parm/use_case_groups.json` on `<base>` and on the pull request
head (`gh api repos/dtcenter/METplus/contents/.github/parm/use_case_groups.json?ref=<ref>`
with `-H "Accept: application/vnd.github.raw"`). The **new groups** are the
`<category>:<index_list>` entries present only on the head. Testing jobs are
named `Use Case Tests (<category>:<index_list>)`.

Find the latest `testing.yml` run for the pull request head
(`gh run list --workflow testing.yml --branch <head branch> --event pull_request -L 1`)
and list each failed job with its failed steps:

```
gh api "repos/dtcenter/METplus/actions/runs/<id>/jobs?per_page=100" --paginate \
  --jq '.jobs[] | select(.conclusion=="failure") | {name, failed: [.steps[] | select(.conclusion=="failure") | .name]}'
```

- The new groups are expected to fail only at **Run difference tests**, since
  there is no truth data for them yet.
- Any **Run Use Cases** failure: stop. The use case does not run.
- Difference failures in other groups: report them. They will also be written
  into the truth data later, so the user must confirm they are expected.
- Other failing checks: report, do not block. SonarQube Scan always fails on a
  pull request from a fork, which gets no repository secrets. Check Links often
  fails on external sites unrelated to the change; name the link.

Then ask the user to confirm that the reviewer has completed
[Update the develop data directory](https://metplus.readthedocs.io/en/develop/Contributors_Guide/add_use_case.html#update-the-develop-data-directory).
Without it the new use cases fail on `<base>` for lack of input data.

### 3. Merge

Present the summary from step 2 and ask whether to merge. On a clear yes:
`gh pr merge $ARGUMENTS --squash`. Record the merge commit SHA from
`gh pr view $ARGUMENTS --json mergeCommit`.

### 4. Wait for the `<base>` testing run

Print the run list link so the user can follow along, or come back later if
the session ends:
`https://github.com/dtcenter/METplus/actions/workflows/testing.yml?query=branch%3A<base>`

Then wait with a background Bash command (`run_in_background`). Do not follow
a fixed run ID. A newer push, or a testing run triggered by a MET, METplotpy,
METcalcpy, or METdataio change, cancels the running one through the workflow's
concurrency rule, and a developer may rerun an older run, which keeps its
original ID and creation time and so is not the newest run on the branch.
Instead, wait until no `<base>` testing run is queued or in progress. Do not
use `gh run watch`, which exits while the run is still queued.

```
while :; do
  active=$(gh run list -R dtcenter/METplus --workflow testing.yml --branch <base> -L 20 \
      --json databaseId,status --jq '[.[] | select(.status != "completed") | .databaseId] | join(" ")')
  if [ $? -eq 0 ] && [ -z "$active" ]; then break; fi
  sleep 120
done
gh run list -R dtcenter/METplus --workflow testing.yml --branch <base> -L 10 \
  --json databaseId,conclusion,headSha,event \
  --jq '[.[] | select(.conclusion != "cancelled")][0]'
```

The command prints the latest completed, non-cancelled run, which is the run
Update Truth Data will read. Tell the user what the wait is on and end the
turn. You are re-invoked when the command exits.

When it does, confirm the run contains the merge:
`gh api repos/dtcenter/METplus/compare/<merge sha>...<run head sha> --jq .status`
must be `identical` or `ahead`. If it does not, stop and report.

### 5. Gate on the run's results

List the failed jobs and steps as in step 2. A run has about 80 jobs, and the
jobs endpoint with `per_page=100` can return HTTP 502 repeatedly. If it does,
page through with `per_page=10&page=N` until a page comes back empty, and check
that the count matches `total_count`. A rerun run has several attempts; the
endpoint without `/attempts/N` returns the latest, which is what Update Truth
Data reads.

A failed **Merge Error Logs** job is not by itself a use case error. Its "Check
for error logs" step calls the same API with `curl` and fails with `jq: error
... Cannot iterate over null` when that call fails. Decide from the use case
jobs instead: any **Save error logs** step that ran (did not skip) means a use
case produced error logs.

Update Truth Data reruns exactly
the groups whose **Run difference tests** step failed in the latest completed,
non-cancelled `<base>` run, so this gate decides what goes into the truth data.

Proceed only if all of these hold:

- No job failed at **Run Use Cases** or any step other than Run difference
  tests.
- Every new group failed at Run difference tests. One that passed gets no truth
  data; stop and report.
- No other group failed at Run difference tests. If one did, stop and report
  it. The run may include other merged changes, such as a MET change that
  started it, and the user decides whether those differences belong in the
  truth data.

If a **new** group failed at Run Use Cases after it passed in the pull request,
the reviewer most likely did not move the new input data for `<base>` and the
next release. Point the user to
[Update the develop data directory](https://metplus.readthedocs.io/en/develop/Contributors_Guide/add_use_case.html#update-the-develop-data-directory),
and once they say it is done, rerun the failed jobs with
`gh run rerun <run id> --failed` and go back to step 4. Any other Run Use Cases
failure: stop and report.

### 6. Run Update Reference Branch

```
gh workflow run update_reference_branch.yml -R dtcenter/METplus --ref <base> \
  -f pull_requests="#$ARGUMENTS" \
  -f change_summary="<one line naming the new use cases>"
```

Leave `run_all_groups` unset. The run finishes in under a minute. Then find the
pull request it opened, titled `Update <base>-ref after #$ARGUMENTS`:
`gh pr list --base <base>-ref --state open --json number,title,headRefName`.
Its head is `update_<base>_XXXXXXXX`. If the workflow failed or no such pull
request exists, stop and report.

### 7. Merge the `<base>-ref` pull request

Copy the milestone and project of pull request `$ARGUMENTS` onto it with
`gh pr edit`. Adding a project needs the `project` scope on the `gh` token; if
that fails, report it and continue, since it does not affect the truth data.
Then merge without waiting for its checks:

```
gh pr merge <number> -R dtcenter/METplus --squash --delete-branch
```

### 8. Watch Update Truth Data

The merge starts the Update Truth Data (automatic) workflow on `<base>-ref`.
Find it with
`gh run list --workflow update_truth_data.yml --branch <base>-ref -L 1`, print
its link, and wait for it the same way as in step 4.

Every use case job and the final **Create Output Docker Data Volumes** job must
succeed, and the matrix should hold the new groups and nothing else. If a use
case fails, point the user to the same Contributor's Guide section as in
step 5, and after they confirm, rerun **all** jobs of that run with
`gh run rerun <run id>`.

### 9. Report

Summarize the merged pull request, the testing run used, the `<base>-ref` pull
request, and the Update Truth Data result, with links.

If the pull request added more than one group in the same category, or a group
that could share an existing one's environment, mention that they could be
combined later in `.github/parm/use_case_groups.json`. Do not do it here:
combining them means pushing to `<base>`, which most contributors cannot do,
and it needs a new testing run before the truth data update.
