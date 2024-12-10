#!/bin/sh

# Must specify 3 arguments:
#   - username
#   - authorization key
#   - repository name

if [[ $# -ne 3 ]]; then
  echo "ERROR: `basename $0` ... must specify the GitHub username, authorization key, and METplus repository name."
  exit 1
else
  user=$1
  auth=$2
  repo=$3
fi

# Verbose output
VERBOSE=0

# GitHub label URL
URL="https://api.github.com/repos/dtcenter/${repo}/labels"
COMMON_LABELS="`dirname $0`/common_labels.txt"

# Output command file
CMD_FILE="`dirname $0`/commands/delete_labels_${repo}_cmd.sh"
echo "#!/bin/sh -v" > ${CMD_FILE}

# Get the current repo labels
SCRIPT_DIR=`dirname $0`
TMP_FILE="${repo}_labels.tmp"
CMD="${SCRIPT_DIR}/get_labels.sh ${user} ${auth} ${repo}"
echo "CALLING: ${CMD}"
${CMD} > ${TMP_FILE} 2>/dev/null

# Initialize counts
n_common=0
n_custom=0
n_delete=0

# Check each of the existing labels against the common list
while read -r line; do

  # Parse the label name
  name=`echo $line | sed -r 's/,/\n/g' | grep '"name":' | cut -d':' -f2-10 | cut -d'"' -f2`

  # Check if it appears in the list of common labels
  is_common=`egrep -i "\"${name}\"" ${COMMON_LABELS} | wc -l`

  # Check if its a custom label that beginning with component, type, or repository name
  is_custom=`echo ${name} | egrep -r -i "component:|type:|${repo}" | wc -l`

  # Keep COMMON labels
  if [[ $is_common -gt 0 ]]; then
    ((n_common+=1))
    if [[ $VERBOSE -gt 0 ]]; then
      echo "[COMMON] ${repo} label ... ${name}"
    fi
  # Keep CUSTOM, repo-specific labels
  elif [[ $is_custom -gt 0 ]]; then
    ((n_custom+=1))
    if [[ $VERBOSE -gt 0 ]]; then
      echo "[CUSTOM] ${repo} label ... ${name}"
    fi
  # DELETE non-common, non-custom labels
  else
    ((n_delete+=1))
    if [[ $VERBOSE -gt 0 ]]; then
      echo "[DELETE] ${repo} label ... ${name}"
    fi
    DELETE_URL="${URL}/`echo ${name} | sed -r 's/ /%20/g'`"
    echo "curl -u \"${user}:${auth}\" -X DELETE \
          -H \"Accept: application/vnd.github.v3+json\" \
          '${DELETE_URL}'" >> ${CMD_FILE}
  fi

done < ${TMP_FILE}

# Cleanup
rm -f ${TMP_FILE}

# Make the run command file executable
chmod +x ${CMD_FILE}

# Print summary
echo "For the ${repo} repository, found $n_common common, $n_custom custom, and $n_delete labels to be deleted."
echo "To delete $n_delete existing ${repo} labels, run:"
echo "  ${CMD_FILE}"
