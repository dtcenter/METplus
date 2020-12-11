#!/bin/sh

# Must specify 4 arguments:
#   - repository name
#   - username
#   - authorization key
#   - label file

if [[ $# -ne 4 ]]; then
  echo "ERROR: $0 ... must specify the repository name, username, authorization key, and label file."
  exit 1
else
  repo=$1
  user=$2
  auth=$3
  labels=$4
fi

# GitHub label URL
URL="https://api.github.com/repos/dtcenter/${repo}/labels"

# Output command file
CMD="post_patch_labels_${repo}.cmd"
rm ${CMD}

# Get the current repo labels
SCRIPT_DIR=`dirname $0`
TMP_FILE="${repo}_labels.tmp"
${SCRIPT_DIR}/get_labels.sh ${repo} ${user} ${auth} > ${TMP_FILE}

# Read the lines of the label file
while read -r line; do

  # Parse the label name
  name=`echo $line | sed -r 's/,/\n/g' | grep '"name":' | cut -d':' -f2-10 | cut -d'"' -f2`

  # Check for existing label
  exists=`egrep -i "\"${name}\"" ${TMP_FILE} | wc -l`

  # POST a new label
  if [[ $exists -eq 0 ]]; then
    echo "[POST ] ${name}"
    echo "curl -u \"${user}:${auth}\" -X POST \
          -H \"Accept: application/vnd.github.v3+json\" \
          -d '${line}' ${URL}" >> $CMD
  # PATCH an existing label
  else
    old_name=`egrep -i "\"${name}\"" ${TMP_FILE} | sed -r 's/,/\n/g' | grep '"name":' | cut -d':' -f2-10 | cut -d'"' -f2 | sed -r 's/ /%20/g'`
    echo "[PATCH] ${old_name} -> ${name}"
    echo "curl -u \"${user}:${auth}\" -X PATCH \
          -H \"Accept: application/vnd.github.v3+json\" \
          -d '${line}' ${URL}/${old_name}" >> $CMD
  fi

done < $labels

# Cleanup
rm -f ${TMP_FILE}

# Make the run command file executable
chmod +x $CMD
echo "To make these changes, execute the run command file:"
echo "./${CMD}"

