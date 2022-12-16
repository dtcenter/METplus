#! /bin/bash

# utility function to run command get log the time it took to run
# ::group:: and ::endgroup:: create collapsible log groups in GitHub Actions
function time_command {
  local start_seconds=$SECONDS
  echo "::group::RUNNING: $*"
  "$@"
  local error=$?
  echo "::endgroup::"

  if [ ${error} -ne 0 ]; then
    echo "ERROR: '$*' exited with status = ${error}"
  fi

  local duration=$(( SECONDS - start_seconds ))
  echo "TIMING: Command took `printf '%02d' $(($duration / 60))`:`printf '%02d' $(($duration % 60))` (MM:SS): '$*'"

  return $error
}
