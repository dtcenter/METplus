#!/bin/sh

# Must specify 3 arguments:
#   - repository name
#   - username
#   - authorization key

if [[ $# -ne 3 ]]; then
  echo "ERROR: $0 ... must specify the repository, username, and authorization key."
  exit 1
else
  repo=$1
  user=$2
  auth=$3
fi

# Pull and format existing records for existing labels
curl -u "${user}:${auth}" -H "Accept: application/vnd.github.v3+json" \
"https://api.github.com/repos/dtcenter/${repo}/labels?page=1&per_page=100" | \
egrep  '"name":|"color":|"description":|{|}' | \
tr -d '\n' | sed -r 's/ +/ /g' | sed 's/}/}\n/g' | sed 's/,* {/{/g'

