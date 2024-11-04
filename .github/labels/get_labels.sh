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

# Pull and format existing records for existing labels
# Run twice for page 1 and page 2 to support up to 200 existing labels
for page_number in 1 2; do
  curl -u "${user}:${auth}" -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/dtcenter/${repo}/labels?page=${page_number}&per_page=100" | \
  egrep  '"name":|"color":|"description":|{|}' | \
  tr -d '\n' | sed -r 's/ +/ /g' | sed 's/}/}\n/g' | sed 's/,* {/{/g'
done

