#! /bin/bash

# Install the metplus package from conda-forge and check that it works.
# Run inside an activated, empty Conda environment configured to use only
# the conda-forge channel.
#
# The conda-forge recipe tests only run when the package is built, so they
# cannot catch a dependency released later that breaks an existing build,
# e.g. a shared library that changes its soname in a patch release.
#
# Environment variables:
#   METPLUS_VERSION - X.Y.Z version of metplus to install (required)
#   WORK_DIR - directory for test output (default: a new temporary directory)
#
# When run in GitHub Actions, each failure is reported as an error annotation
# and a report is added to the job summary.

if [ -z "${CONDA_PREFIX}" ]; then
  echo "ERROR: CONDA_PREFIX is not set. Activate the environment first."
  exit 1
fi
if [ -z "${METPLUS_VERSION}" ]; then
  echo "ERROR: METPLUS_VERSION is not set"
  exit 1
fi

WORK_DIR=${WORK_DIR:-$(mktemp -d)}
mkdir -p "${WORK_DIR}"
SUMMARY_FILE=${GITHUB_STEP_SUMMARY:-/dev/null}
PLATFORM="$(uname -s) $(uname -m)"
LABEL="metplus ${METPLUS_VERSION} on ${PLATFORM}"

# number of output lines to include for each failure
MAX_LINES=15

# text printed by the dynamic loader when a library or symbol is missing
LOADER_ERRORS='error while loading shared libraries|symbol lookup error|Library not loaded|Symbol not found|dyld'

num_failures=0
details_file="${WORK_DIR}/failure_details.md"
: > "${details_file}"

# Print an error, add a GitHub Actions error annotation, and add the
# output to the failure details in the job summary.
# Arguments: title, message, output (optional)
report_failure() {
  local title=$1 message=$2 output=$3
  num_failures=$((num_failures + 1))
  echo "FAIL: ${title}: ${message}"
  if [ -n "${output}" ]; then
    echo "${output}" | head -${MAX_LINES}
  fi

  if [ "${GITHUB_ACTIONS}" == "true" ]; then
    local text="${message}"
    if [ -n "${output}" ]; then
      text+=$'\n'$(echo "${output}" | head -5)
    fi
    # escape characters that have special meaning in workflow commands
    text=${text//'%'/'%25'}
    text=${text//$'\r'/'%0D'}
    text=${text//$'\n'/'%0A'}
    echo "::error title=${LABEL}: ${title}::${text}"
  fi

  {
    echo "<details><summary><b>${title}</b>: ${message}</summary>"
    echo
    if [ -n "${output}" ]; then
      echo '```text'
      echo "${output}" | head -${MAX_LINES}
      echo '```'
    fi
    echo "</details>"
    echo
  } >> "${details_file}"
}

# Write the job summary and exit with status 1 if any check failed.
finish() {
  {
    if [ ${num_failures} -eq 0 ]; then
      echo "### :white_check_mark: ${LABEL}"
    else
      echo "### :x: ${LABEL}: ${num_failures} check(s) failed"
    fi
    echo
    printf '%s' "${notes}"
    if [ -n "${package_table}" ]; then
      echo "| Package | Version | Build |"
      echo "|---|---|---|"
      echo "${package_table}"
      echo
    fi
    echo "| Check | Result |"
    echo "|---|---|"
    printf '%s' "${results_table}"
    echo
    cat "${details_file}"
  } >> "${SUMMARY_FILE}"

  echo
  if [ ${num_failures} -ne 0 ]; then
    echo "ERROR: ${num_failures} check(s) failed for ${LABEL}"
    exit 1
  fi
  echo "All checks passed for ${LABEL}"
  exit 0
}

# Add a row to the results table in the job summary.
# Arguments: check name, result text
add_result() {
  results_table+="| $1 | $2 |"$'\n'
}

# Print a warning, add a GitHub Actions warning annotation, and add a note
# to the job summary. A warning does not fail the check.
# Arguments: title, message
report_warning() {
  local title=$1 message=$2
  echo "WARNING: ${title}: ${message}"
  if [ "${GITHUB_ACTIONS}" == "true" ]; then
    echo "::warning title=${LABEL}: ${title}::${message//'%'/'%25'}"
  fi
  notes+="> [!WARNING]"$'\n'"> **${title}**: ${message}"$'\n\n'
}

package_table=""
results_table=""
notes=""

# If the requested version was never published to conda-forge, e.g. a bugfix
# release of an older X.Y that the feedstock bot did not pick up, check the
# latest X.Y.Z that is available instead and warn about the missing one.
# The empty environment may not contain python, so parse the plain output.
requested_version=${METPLUS_VERSION}
xy=$(echo "${requested_version}" | cut -d. -f1,2)
available=$(conda search --override-channels -c conda-forge "metplus=${xy}" 2>/dev/null \
            | awk '$1 == "metplus" {print $2}' | sort -uV)
if [ -z "${available}" ]; then
  report_failure "Install" \
    "no metplus ${xy}.x release is available on conda-forge for this platform"
  add_result "Install" ":x: no ${xy}.x release on conda-forge"
  finish
fi
if ! echo "${available}" | grep -qx "${requested_version}"; then
  METPLUS_VERSION=$(echo "${available}" | tail -1)
  report_warning "Not on conda-forge" \
    "metplus ${requested_version} has not been published to conda-forge for this platform, so checking ${METPLUS_VERSION}, the latest ${xy}.x release available there ($(echo ${available} | sed 's/ /, /g'))"
  LABEL="metplus ${METPLUS_VERSION} on ${PLATFORM}"
fi

echo "Installing ${LABEL}"

install_output=$(conda install -y "metplus==${METPLUS_VERSION}" 2>&1)
if [ $? -ne 0 ]; then
  report_failure "Install" "conda install metplus==${METPLUS_VERSION} failed" \
    "$(echo "${install_output}" | tail -${MAX_LINES})"
  add_result "Install" ":x: failed"
  finish
fi
add_result "Install" ":white_check_mark:"

echo "Installed packages of interest:"
package_list=$(conda list --prefix "${CONDA_PREFIX}" \
  | grep -E '^(metplus|netcdf-cxx4|libnetcdf|hdf5|python) ')
echo "${package_list}"
echo
package_table=$(echo "${package_list}" | awk '{print "| "$1" | "$2" | "$3" |"}')

# get the files installed under bin/ by the metplus package from its metadata
meta_file=$(ls "${CONDA_PREFIX}"/conda-meta/metplus-[0-9]*.json 2>/dev/null | head -1)
if [ -z "${meta_file}" ]; then
  report_failure "Install" "metplus package metadata not found in ${CONDA_PREFIX}/conda-meta"
  finish
fi

bin_files=$(python -c "import json, sys
for f in json.load(open(sys.argv[1]))['files']:
    if f.startswith('bin/'):
        print(f)" "${meta_file}")

# run each compiled executable and look for dynamic loader errors
num_checked=0
load_failures=()
first_load_error=""
for rel_path in ${bin_files}; do
  exe="${CONDA_PREFIX}/${rel_path}"
  if ! file -b "${exe}" | grep -qE 'ELF|Mach-O'; then
    continue
  fi
  num_checked=$((num_checked + 1))
  tool=$(basename "${exe}")

  error_output=""
  if [ "$(uname)" == "Linux" ]; then
    error_output=$(ldd "${exe}" 2>&1 | grep 'not found')
  fi
  if [ -z "${error_output}" ]; then
    output=$("${exe}" --help 2>&1)
    status=$?
    # 127 is the exit status when the loader fails on Linux,
    # and 128 or higher means the process was killed by a signal
    if [ ${status} -ge 126 ] || echo "${output}" | grep -qE "${LOADER_ERRORS}"; then
      error_output="exit status ${status}"$'\n'"${output}"
    fi
  fi

  if [ -n "${error_output}" ]; then
    echo "FAIL: ${tool}"
    echo "${error_output}" | head -${MAX_LINES}
    load_failures+=("${tool}")
    if [ -z "${first_load_error}" ]; then
      first_load_error="${tool}: ${error_output}"
    fi
  else
    echo "OK: ${tool}"
  fi
done

if [ ${num_checked} -eq 0 ]; then
  report_failure "MET executables" "no compiled executables found in the metplus package"
  add_result "MET executables" ":x: none found"
elif [ ${#load_failures[@]} -ne 0 ]; then
  # report all load failures together to stay within the annotation limits
  report_failure "MET executables" \
    "${#load_failures[@]} of ${num_checked} executables failed to load: ${load_failures[*]}" \
    "${first_load_error}"
  add_result "MET executables" ":x: ${#load_failures[@]} of ${num_checked} failed to load"
else
  add_result "MET executables" ":white_check_mark: ${num_checked} load"
fi
echo

# exercise NetCDF write and read with MET tools, using a named grid as input
mask_file="${WORK_DIR}/gen_vx_mask_lat.nc"
plot_file="${WORK_DIR}/plot_data_plane_lat.ps"
output=$( { gen_vx_mask G004 G004 "${mask_file}" -type lat -thresh 'ge30' -name lat_mask -v 1 \
  && plot_data_plane "${mask_file}" "${plot_file}" 'name="lat_mask"; level="(*,*)";' -v 1; } 2>&1 )
if [ $? -eq 0 ] && [ -s "${plot_file}" ]; then
  echo "OK: gen_vx_mask and plot_data_plane wrote and read NetCDF"
  add_result "NetCDF write and read" ":white_check_mark:"
else
  report_failure "NetCDF write and read" \
    "gen_vx_mask or plot_data_plane did not produce output" "${output}"
  add_result "NetCDF write and read" ":x:"
fi

# check the METplus wrappers, running from the work directory so that a
# metplus source tree in the current directory is not imported instead
cd "${WORK_DIR}" || exit 1
output=$(python -c "import metplus; print(metplus.__version__)" 2>&1)
if [ "$(echo "${output}" | tail -1)" == "${METPLUS_VERSION}" ]; then
  echo "OK: import metplus ${METPLUS_VERSION}"
  add_result "import metplus" ":white_check_mark:"
else
  report_failure "import metplus" "did not give version ${METPLUS_VERSION}" "${output}"
  add_result "import metplus" ":x:"
fi

# run_metplus.py --help exits non-zero in some versions, so check the output
output=$(run_metplus.py --help 2>&1)
if echo "${output}" | grep -q "Running METplus v${METPLUS_VERSION}"; then
  echo "OK: run_metplus.py --help"
  add_result "run_metplus.py" ":white_check_mark:"
else
  report_failure "run_metplus.py" "--help did not report version ${METPLUS_VERSION}" "${output}"
  add_result "run_metplus.py" ":x:"
fi

finish
