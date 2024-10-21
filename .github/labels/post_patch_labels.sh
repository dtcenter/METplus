#!/bin/bash

# Must specify 4 arguments:
#   - username
#   - authorization key
#   - repository name
#   - label file

if [[ $# -ne 4 ]]; then
  echo "ERROR: `basename $0` ... must specify the GitHub username, authorization key, METplus repository name, and label file."
  exit 1
else
  user=$1
  auth=$2
  repo=$3
  labels=$4
fi

# Verbose output
VERBOSE=0

# GitHub label URL
URL="https://api.github.com/repos/dtcenter/${repo}/labels"

# Output command files
POST_CMD_FILE="`dirname $0`/commands/post_labels_${repo}_cmd.sh"
echo "#!/bin/sh -v" > ${POST_CMD_FILE}

PATCH_CMD_FILE="`dirname $0`/commands/patch_labels_${repo}_cmd.sh"
echo "#!/bin/sh -v" > ${PATCH_CMD_FILE}

# Initialize counts
n_post=0
n_patch=0

# Get the current repo labels
SCRIPT_DIR=`dirname $0`
TMP_FILE="${repo}_labels.tmp"
CMD="${SCRIPT_DIR}/get_labels.sh ${user} ${auth} ${repo}"
echo "CALLING: ${CMD}"
${CMD} > ${TMP_FILE} 2>/dev/null

# Read the lines of the label file
while read -r line; do

  # Parse the label name
  name=`echo $line | sed -r 's/,/\n/g' | grep '"name":' | cut -d':' -f2-10 | cut -d'"' -f2`

  # Check for existing label
  exists=`egrep -i "\"${name}\"" ${TMP_FILE} | wc -l`

  # POST a new label
  if [[ $exists -eq 0 ]]; then
    ((n_post+=1))
    if [[ $VERBOSE -gt 0 ]]; then
      echo "[POST ] ${repo} label ... ${name}"
    fi
    echo "curl -u \"${user}:${auth}\" -X POST \
          -H \"Accept: application/vnd.github.v3+json\" \
          -d '${line}' '${URL}'" >> ${POST_CMD_FILE}
  # PATCH an existing label
  else
    ((n_patch+=1))
    old_name=`egrep -i "\"${name}\"" ${TMP_FILE} | sed -r 's/,/\n/g' | grep '"name":' | cut -d':' -f2-10 | cut -d'"' -f2 | sed -r 's/ /%20/g'`
    if [[ $VERBOSE -gt 0 ]]; then
      echo "[PATCH] ${repo} label ... ${old_name} -> ${name}"
    fi
    echo "curl -u \"${user}:${auth}\" -X PATCH \
          -H \"Accept: application/vnd.github.v3+json\" \
          -d '${line}' '${URL}/${old_name}'" >> ${PATCH_CMD_FILE}
  fi

done < $labels

# Cleanup
rm -f ${TMP_FILE}

# Make the run command file executable
chmod +x ${POST_CMD_FILE} ${PATCH_CMD_FILE}

# Print summary
echo "For the ${repo} repository, found $n_patch existing labels to be updated and $n_post new labels to be added."
echo "To add $n_post new ${repo} labels, run:"
echo "  ${POST_CMD_FILE}"
echo "To update $n_patch existing ${repo} labels, run:"
echo "  ${PATCH_CMD_FILE}"
