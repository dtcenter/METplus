#! /bin/bash

# utility function to run command get log the time it took to run
function time_command {
  local start_seconds=$SECONDS
  echo "RUNNING: $*"
  "$@"
  local error=$?

  local duration=$(( SECONDS - start_seconds ))
  echo "TIMING: Command took `printf '%02d' $(($duration / 60))`:`printf '%02d' $(($duration % 60))` (MM:SS): '$*'"
  if [ ${error} -ne 0 ]; then
    echo "ERROR: '$*' exited with status = ${error}"
  fi
  return $error
}
