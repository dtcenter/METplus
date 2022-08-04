#!/bin/bash

# Must specify 4 arguments:
#   - username
#   - authorization key
#   - repository name
#   - label file

if [[ $# -ne 4 ]]; then
  echo "ERROR: `basename $0` ... must specify the GitHub username, authorization key, repository name, and label file."
  echo "ERROR:   repo names: metplus, met, metdataio, metcalcpy, metplotpy, metviewer, metexpress, metplus-training, metplus-internal"
  exit 1
else
  user=$1
  auth=$2
  repo=$3
  labels=$4
fi

# GitHub label URL
URL="https://api.github.com/repos/dtcenter/${repo}/labels"

# Output command file
CMD_FILE="`dirname $0`/commands/post_patch_labels_${repo}_cmd.sh"
echo "#!/bin/sh -v" > ${CMD_FILE}

# Get the current repo labels
SCRIPT_DIR=`dirname $0`
TMP_FILE="${repo}_labels.tmp"
CMD="${SCRIPT_DIR}/get_labels.sh ${user} ${auth} ${repo}"
echo "CALLING: ${CMD}"
${CMD} > ${TMP_FILE}

# Read the lines of the label file
while read -r line; do

  # Parse the label name
  name=`echo $line | sed -r 's/,/\n/g' | grep '"name":' | cut -d':' -f2-10 | cut -d'"' -f2`

  # Check for existing label
  exists=`egrep -i "\"${name}\"" ${TMP_FILE} | wc -l`

  # POST a new label
  if [[ $exists -eq 0 ]]; then
    echo "[POST ] ${repo} label ... ${name}"
    echo "curl -u \"${user}:${auth}\" -X POST \
          -H \"Accept: application/vnd.github.v3+json\" \
          -d '${line}' '${URL}'" >> ${CMD_FILE}
  # PATCH an existing label
  else
    old_name=`egrep -i "\"${name}\"" ${TMP_FILE} | sed -r 's/,/\n/g' | grep '"name":' | cut -d':' -f2-10 | cut -d'"' -f2 | sed -r 's/ /%20/g'`
    echo "[PATCH] ${repo} label ... ${old_name} -> ${name}"
    echo "curl -u \"${user}:${auth}\" -X PATCH \
          -H \"Accept: application/vnd.github.v3+json\" \
          -d '${line}' '${URL}/${old_name}'" >> ${CMD_FILE}
  fi

done < $labels

# Cleanup
rm -f ${TMP_FILE}

# Make the run command file executable
chmod +x ${CMD_FILE}
echo "To make these changes, execute the run command file:"
echo "./${CMD_FILE}"

