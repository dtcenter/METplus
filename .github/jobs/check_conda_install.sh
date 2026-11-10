#! /bin/bash

# Check that the metplus package installed from conda-forge works.
# Run inside the activated Conda environment that contains metplus.
#
# The conda-forge recipe tests only run when the package is built, so they
# cannot catch a dependency released later that breaks an existing build,
# e.g. a shared library that changes its soname in a patch release.
#
# Optional environment variable:
#   WORK_DIR - directory for test output (default: a new temporary directory)

if [ -z "${CONDA_PREFIX}" ]; then
  echo "ERROR: CONDA_PREFIX is not set. Activate the environment first."
  exit 1
fi

WORK_DIR=${WORK_DIR:-$(mktemp -d)}
mkdir -p "${WORK_DIR}"

failures=()

# text printed by the dynamic loader when a library or symbol is missing
loader_errors='error while loading shared libraries|symbol lookup error|Library not loaded|Symbol not found|dyld'

echo "Installed packages of interest:"
conda list --prefix "${CONDA_PREFIX}" \
  | grep -E '^(metplus|netcdf-cxx4|libnetcdf|hdf5|python) '
echo

# get the files installed under bin/ by the metplus package from its metadata
meta_file=$(ls "${CONDA_PREFIX}"/conda-meta/metplus-[0-9]*.json 2>/dev/null | head -1)
if [ -z "${meta_file}" ]; then
  echo "ERROR: metplus package metadata not found in ${CONDA_PREFIX}/conda-meta"
  exit 1
fi

bin_files=$(python -c "import json, sys
for f in json.load(open(sys.argv[1]))['files']:
    if f.startswith('bin/'):
        print(f)" "${meta_file}")

# run each compiled executable and look for dynamic loader errors
num_checked=0
for rel_path in ${bin_files}; do
  exe="${CONDA_PREFIX}/${rel_path}"
  if ! file -b "${exe}" | grep -qE 'ELF|Mach-O'; then
    continue
  fi
  num_checked=$((num_checked + 1))
  tool=$(basename "${exe}")

  if [ "$(uname)" == "Linux" ]; then
    missing=$(ldd "${exe}" 2>&1 | grep 'not found')
    if [ -n "${missing}" ]; then
      echo "FAIL: ${tool} has unresolved libraries:"
      echo "${missing}"
      failures+=("${tool}")
      continue
    fi
  fi

  output=$("${exe}" --help 2>&1)
  status=$?
  # 127 is the exit status when the loader fails on Linux,
  # and 128 or higher means the process was killed by a signal
  if [ ${status} -ge 126 ] || echo "${output}" | grep -qE "${loader_errors}"; then
    echo "FAIL: ${tool} --help exited with status ${status}:"
    echo "${output}" | head -20
    failures+=("${tool}")
  else
    echo "OK: ${tool}"
  fi
done

if [ ${num_checked} -eq 0 ]; then
  echo "FAIL: no compiled executables found in the metplus package"
  failures+=("no executables")
fi
echo
echo "Checked ${num_checked} executables"
echo

# exercise NetCDF write and read with MET tools, using a named grid as input
mask_file="${WORK_DIR}/gen_vx_mask_lat.nc"
plot_file="${WORK_DIR}/plot_data_plane_lat.ps"
if gen_vx_mask G004 G004 "${mask_file}" -type lat -thresh 'ge30' -name lat_mask -v 1 \
   && plot_data_plane "${mask_file}" "${plot_file}" 'name="lat_mask"; level="(*,*)";' -v 1 \
   && [ -s "${plot_file}" ]; then
  echo "OK: gen_vx_mask and plot_data_plane wrote ${mask_file} and ${plot_file}"
else
  echo "FAIL: gen_vx_mask or plot_data_plane did not produce output"
  failures+=("gen_vx_mask/plot_data_plane")
fi

# check the METplus wrappers, running from the work directory so that a
# metplus source tree in the current directory is not imported instead
cd "${WORK_DIR}" || exit 1
installed_version=$(conda list --prefix "${CONDA_PREFIX}" --json '^metplus$' \
  | python -c "import json, sys; print(json.load(sys.stdin)[0]['version'])")
imported_version=$(python -c "import metplus; print(metplus.__version__)")
if [ "${imported_version}" == "${installed_version}" ]; then
  echo "OK: import metplus ${imported_version}"
else
  echo "FAIL: import metplus gave version '${imported_version}', expected '${installed_version}'"
  failures+=("import metplus")
fi

# run_metplus.py --help exits non-zero in some versions, so check the output
output=$(run_metplus.py --help 2>&1)
if echo "${output}" | grep -q "Running METplus v${installed_version}"; then
  echo "OK: run_metplus.py --help"
else
  echo "FAIL: run_metplus.py --help printed:"
  echo "${output}" | head -20
  failures+=("run_metplus.py")
fi

echo
if [ ${#failures[@]} -ne 0 ]; then
  echo "ERROR: ${#failures[@]} check(s) failed: ${failures[*]}"
  exit 1
fi

echo "All checks passed"
