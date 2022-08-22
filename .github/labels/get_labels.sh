#!/bin/sh

# Must specify 3 arguments:
#   - username
#   - authorization key
#   - repository name

if [[ $# -ne 3 ]]; then
  echo "ERROR: `basename $0` ... must specify the GitHub username, authorization key, and repository name."
  echo "ERROR:   repo names: metplus, met, metdataio, metcalcpy, metplotpy, metviewer, metexpress, metplus-training"
  exit 1
else
  user=$1
  auth=$2
  repo=$3
fi

# Pull and format existing records for existing labels
curl -u "${user}:${auth}" -H "Accept: application/vnd.github.v3+json" \
"https://api.github.com/repos/dtcenter/${repo}/labels?page=1&per_page=100" | \
egrep  '"name":|"color":|"description":|{|}' | \
tr -d '\n' | sed -r 's/ +/ /g' | sed 's/}/}\n/g' | sed 's/,* {/{/g'

