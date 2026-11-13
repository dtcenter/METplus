#! /bin/bash

# utility function to run command get log the time it took to run
# ::group:: and ::endgroup:: create collapsible log groups in GitHub Actions
function time_command {
  local start_seconds=$SECONDS
  echo "::group::RUNNING: $*"

  local error
  # pipe output to log file if set
  if [ "x$CMD_LOGFILE" == "x" ]; then
    "$@"
    error=$?
  else
    echo "Logging to ${CMD_LOGFILE}"
    "$@" &>> $CMD_LOGFILE
    error=$?
    unset CMD_LOGFILE
  fi

  local duration=$(( SECONDS - start_seconds ))
  echo "TIMING: Command took `printf '%02d' $(($duration / 60))`:`printf '%02d' $(($duration % 60))` (MM:SS): '$*'"
  echo "::endgroup::"

  if [ ${error} -ne 0 ]; then
    echo "ERROR: '$*' exited with status = ${error}"
  fi

  return $error
}

# utility function to call the GitHub API with gh api, retrying on failure.
# Arguments are passed to gh api. GH_TOKEN must be set.
# gh api exits non-zero on an HTTP error, unlike curl -s, so a failed request
# is not passed to jq as if it were the response.
# Output is written only after a request succeeds, because gh api --paginate
# writes each page as it is fetched, so a request that fails partway would
# otherwise write the earlier pages again on the next attempt
function gh_api_retry {
  local max_attempts=3
  local attempt
  local arg
  local endpoint=""
  # declared separately so the if below tests the exit status of gh api,
  # not of local, which is always 0
  local output
  # find endpoint (first argument that is not an option) for log messages
  for arg in "$@"; do
    if [[ "${arg}" != -* ]]; then
      endpoint=${arg}
      break
    fi
  done
  for attempt in $(seq 1 ${max_attempts}); do
    if output=$(gh api "$@"); then
      [ -n "${output}" ] && echo "${output}"
      return 0
    fi
    if [ ${attempt} -lt ${max_attempts} ]; then
      echo "WARNING: gh api ${endpoint} failed (attempt ${attempt} of ${max_attempts}), retrying in 30 seconds" >&2
      sleep 30
    fi
  done
  echo "ERROR: gh api ${endpoint} failed after ${max_attempts} attempts" >&2
  return 1
}

# utility function to scan a Docker image for vulnerabilities
function cve_scan_image {
  echo "Scanning image $1"
  CMD_LOGFILE="${GITHUB_WORKSPACE}/CVE_Scan_`echo $1 | sed 's%[/,:]%_%g'`.log"
  time_command grype $1
  CMD_LOGFILE="${GITHUB_WORKSPACE}/CVE_Scan_`echo $1 | sed 's%[/,:]%_%g'`.log"
  N_CRITICAL=`grep "Critical" ${CMD_LOGFILE} | wc -l`
  if [ ${N_CRITICAL} -gt 0 ]; then
    echo "WARNING: Found ${N_CRITICAL} Critical CVEs for image $1 in ${CMD_LOGFILE}"
    echo
    egrep "SEVERITY|Critical" ${CMD_LOGFILE}
    echo
  fi
}
