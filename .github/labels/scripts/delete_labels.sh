#!/bin/sh

# Must specify 3 arguments:
#   - username
#   - authorization key
#   - repository name

if [[ $# -ne 3 ]]; then
  echo "ERROR: $0 ... must specify the GitHub username, authorization key, and repository name."
  exit 1
else
  user=$1
  auth=$2
  repo=$3
fi

# Constants
URL="https://api.github.com/repos/dtcenter/${repo}/labels"
COMMON_LABELS="`dirname $0`/../common_labels.txt"

# Output command file
CMD_FILE="delete_labels_${repo}_cmd.sh"
echo "#!/bin/sh -v" > ${CMD_FILE}

# Get the current repo labels
SCRIPT_DIR=`dirname $0`
TMP_FILE="${repo}_labels.tmp"
CMD="${SCRIPT_DIR}/get_labels.sh ${user} ${auth} ${repo}"
echo "CALLING: ${CMD}"
${CMD} > ${TMP_FILE}

# Check each of the existing labels against the common list
while read -r line; do

  # Parse the label name
  name=`echo $line | sed -r 's/,/\n/g' | grep '"name":' | cut -d':' -f2-10 | cut -d'"' -f2`

  # Check if it's a common label and a component label
  is_common=`egrep -i "\"${name}\"" ${COMMON_LABELS} | wc -l`
  is_comp_or_type=`echo ${name} | egrep "component:|type:" | wc -l`

  # POST a new label
  if [[ $is_common -eq 0 && $is_comp_or_type -eq 0 ]]; then
    echo "[DELETE] ${repo} -> ${name}"
    DELETE_URL="${URL}/`echo ${name} | sed -r 's/ /%20/g'`"
    echo "curl -u \"${user}:${auth}\" -X PATCH \
          -H \"Accept: application/vnd.github.v3+json\" \
          ${DELETE_URL}'" >> ${CMD_FILE}
  # Keep this label
  else
    echo "[KEEP  ] ${name}"
  fi

done < ${TMP_FILE}

# Cleanup
rm -f ${TMP_FILE}

# Make the run command file executable
chmod +x ${CMD_FILE}
echo "To make these changes, execute the run command file:"
echo "./${CMD_FILE}"
