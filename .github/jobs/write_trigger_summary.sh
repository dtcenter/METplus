#! /bin/bash

# Run by GitHub Actions (in .github/workflows/testing.yml) to describe what
# triggered a workflow_dispatch run in the job summary shown on the run's
# summary page. Other METplus component repositories trigger this workflow
# when a change is pushed to develop or main_vX.Y, passing the repository,
# commit hash, ref, and user in the workflow_dispatch inputs. This finds the
# pull request that the commit came from, which the run name does not show.
#
# Reads the workflow_dispatch inputs from environment variables
# INPUT_REPOSITORY, INPUT_SHA, INPUT_REF, INPUT_ACTOR, INPUT_TITLE,
# INPUT_FORCE_MET_IMAGE, INPUT_METPLOTPY_BRANCH, INPUT_METCALCPY_BRANCH, and
# INPUT_METDATAIO_BRANCH. GH_TOKEN must be set to query the GitHub API.
# Writes to $GITHUB_STEP_SUMMARY, or to stdout if it is not set.

summary=${GITHUB_STEP_SUMMARY:-/dev/stdout}

# escape characters that would break a markdown table cell
function md_cell {
  echo "$1" | sed 's/|/\\|/g'
}

# list inputs that override the default versions, which apply whether the
# run was triggered by another repository or by hand
function write_overrides {
  local rows=""
  [ -n "${INPUT_FORCE_MET_IMAGE}" ] && rows+="| MET image | \`$(md_cell "${INPUT_FORCE_MET_IMAGE}")\` |"$'\n'
  [ -n "${INPUT_METPLOTPY_BRANCH}" ] && rows+="| METplotpy branch | \`$(md_cell "${INPUT_METPLOTPY_BRANCH}")\` |"$'\n'
  [ -n "${INPUT_METCALCPY_BRANCH}" ] && rows+="| METcalcpy branch | \`$(md_cell "${INPUT_METCALCPY_BRANCH}")\` |"$'\n'
  [ -n "${INPUT_METDATAIO_BRANCH}" ] && rows+="| METdataio branch | \`$(md_cell "${INPUT_METDATAIO_BRANCH}")\` |"$'\n'
  if [ -n "${rows}" ]; then
    echo
    echo "### Version overrides"
    echo
    echo "| Input | Value |"
    echo "|---|---|"
    echo -n "${rows}"
  fi
}

# run triggered by hand from the Actions tab
if [ -z "${INPUT_REPOSITORY}" ]; then
  {
    echo "## Manually triggered"
    echo
    echo "Started by ${GITHUB_TRIGGERING_ACTOR:-${GITHUB_ACTOR}} on the \`${GITHUB_REF_NAME}\` branch."
    if [ -n "${INPUT_TITLE}" ]; then
      echo
      echo "**Title:** $(md_cell "${INPUT_TITLE}")"
    fi
    write_overrides
  } >> "${summary}"
  exit 0
fi

repo=${INPUT_REPOSITORY}
sha=${INPUT_SHA}
branch=${INPUT_REF#refs/heads/}
repo_url="https://github.com/${repo}"

# only link to and query the API for dtcenter repositories and a valid
# commit hash, since the inputs are free text
repo_md=$(md_cell "${repo}")
pr_rows=""
commit_row="| **Commit** | \`$(md_cell "${sha:0:9}")\` |"
if [[ "${repo}" == dtcenter/* ]]; then
  repo_md="[${repo}](${repo_url})"
fi
if [[ "${repo}" == dtcenter/* ]] && [[ "${sha}" =~ ^[0-9a-f]{40}$ ]]; then
  commit_url="${repo_url}/commit/${sha}"
  commit_row="| **Commit** | [\`${sha:0:9}\`](${commit_url}) |"

  # first line of the commit message, author, and date
  if commit_json=$(gh api "repos/${repo}/commits/${sha}" \
      --jq '{title: (.commit.message | split("\n")[0]), author: .commit.author.name, date: .commit.author.date}'); then
    commit_title=$(echo "${commit_json}" | jq -r .title)
    commit_author=$(echo "${commit_json}" | jq -r .author)
    commit_date=$(echo "${commit_json}" | jq -r .date)
    commit_row="| **Commit** | [\`${sha:0:9}\`](${commit_url}) $(md_cell "${commit_title}") |"$'\n'
    commit_row+="| **Author** | $(md_cell "${commit_author}") on ${commit_date} |"
  fi

  # pull request that the commit was merged from. The API also lists pull
  # requests that only contain the commit, e.g. one that updates a -ref
  # branch, so keep only one whose merge commit is this commit
  if prs=$(gh api "repos/${repo}/commits/${sha}/pulls" \
      --jq ".[] | select(.merge_commit_sha == \"${sha}\") |
            \"[#\(.number) \(.title | gsub(\"\\\\|\"; \"\\\\|\"))](\(.html_url)) by \(.user.login)\""); then
    if [ -n "${prs}" ]; then
      while IFS= read -r pr; do
        pr_rows+="| **Pull request** | ${pr} |"$'\n'
      done <<< "${prs}"
    else
      pr_rows="| **Pull request** | None (commit was pushed directly) |"$'\n'
    fi
  else
    pr_rows="| **Pull request** | Could not get pull request information |"$'\n'
  fi
fi

{
  echo "## Triggered by ${repo_md}"
  echo
  echo "| | |"
  echo "|---|---|"
  echo -n "${pr_rows}"
  echo "${commit_row}"
  echo "| **Branch** | \`$(md_cell "${branch}")\` |"
  echo "| **Pushed by** | $(md_cell "${INPUT_ACTOR}") |"
  write_overrides
} >> "${summary}"
