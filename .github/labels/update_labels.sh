#!/bin/bash
#
# Manage GitHub labels across multiple METplus repositories: synchronize
# them against the common label definitions, reassign issues/pull requests
# from one label to another, assign labels to open issues/PRs, create,
# rename, delete, archive, and unarchive labels, and update label colors
# and descriptions.
#
# The --sync and --prune options replace the earlier curl-based scripts that
# managed the common labels defined in common_labels.txt.
#
# Requires the GitHub CLI (gh) to be installed and authenticated:
#   gh auth status || gh auth login
#
# Note that the GitHub CLI has no label archiving command, so archiving is
# done through the REST API, which accepts an "archived" flag when updating
# a label. Archived labels retain their history on existing issues/PRs but
# cannot be added to new ones.
#
# This script makes NO changes. It queries each repository and writes the
# resulting gh commands to the commands/ directory for review. Inspect the
# generated files and run them to apply the changes.
#

SCRIPT_NAME=$(basename $0)
SCRIPT_DIR=$(dirname $0)
CMD_DIR="${SCRIPT_DIR}/commands"

# Default GitHub organization
ORG="dtcenter"

# Default list of METplus repositories
REPO_LIST="metplus met metplotpy metcalcpy metdataio metviewer \
           metexpress metbaseimage metplus-internal metplus-training"

# Sentinel indicating that an optional value was not provided on the command
# line, so that --description "" can be used to clear a description
UNSET="@@NOT_SET@@"

# Label operations, populated from the command line. The COLOR and DESC
# arrays run parallel to the operation arrays.
CREATE_LIST=()
CREATE_COLOR=()
CREATE_DESC=()
MOVE_LIST=()
MOVE_COLOR=()
MOVE_DESC=()
ASSIGN_LIST=()
ASSIGN_COLOR=()
ASSIGN_DESC=()
EDIT_LIST=()
EDIT_COLOR=()
EDIT_DESC=()
ARCHIVE_LIST=()
UNARCHIVE_LIST=()
DELETE_LIST=()
UNASSIGN_LIST=()

# Remove every archived label from the open issues and pull requests
STRIP_ARCHIVED=0

# Synchronize each repository against a file of common label definitions
SYNC=0
SYNC_FILE="${SCRIPT_DIR}/common_labels.txt"
PRUNE=0

# Labels to keep when pruning, even though they are not common to every
# repository: the per-component and per-repository custom labels
KEEP_PATTERN="component:|type:|^MET"

# Common label definitions, read once and applied to every repository
SYNC_NAME=()
SYNC_COLOR=()
SYNC_DESC=()
SYNC_ARCH=()

# Labels created by --create, --move, or --assign, listed at the end so that
# they can be added to the common label definitions
NEW_NAME=()
NEW_COLOR=()
NEW_DESC=()

usage() {
  cat << EOF
Usage: ${SCRIPT_NAME} [options]

  -s, --sync [FILE]        Make every repository match the common label
                           definitions in FILE, creating missing labels and
                           correcting colors, descriptions, and archived
                           state. Default: common_labels.txt.
      --prune              With --sync, also delete repository labels that
                           are absent from the label file. Labels matching
                           "${KEEP_PATTERN}"
                           are kept, since those are component- and
                           repository-specific rather than common.
      --create "NAME"      Create a new label NAME in each repository that
                           does not already define it. Requires --color so
                           that the label looks the same everywhere. May be
                           used more than once.
      --delete "NAME"      Permanently delete label NAME, removing it from
                           every issue/PR that carries it. Consider --archive
                           instead, which preserves history. May be used more
                           than once.
  -m, --move   "OLD=>NEW"  Add label NEW to every issue/PR currently labelled
                           OLD and then delete label OLD. Affects open and
                           closed issues/PRs. May be used more than once.
  -a, --assign "NEW"       Add label NEW to every OPEN issue/PR.
      --assign "OLD=>NEW"  Add label NEW to every OPEN issue/PR currently
                           labelled OLD, leaving OLD in place. If NEW does
                           not exist, it is created with the color and
                           description of OLD. Closed issues/PRs are never
                           touched. Nothing is deleted. May be used more than
                           once.
      --unassign "NAME"    Remove label NAME from every OPEN issue/PR. The
                           label itself is kept, as are its assignments on
                           closed issues/PRs. May be used more than once.
      --strip-archived     Remove every archived label from the OPEN issues
                           and PRs of each repository, including any labels
                           archived earlier in the same run. Their history on
                           closed issues/PRs is left intact.
  -n, --rename "OLD=>NEW"  Rename existing label OLD to NEW, preserving its
                           existing assignments. May be used more than once.
  -u, --update "NAME"      Update label NAME in place, without renaming it.
                           Use with --color and/or --description. May be used
                           more than once.
      --archive "NAME"     Archive label NAME. It keeps its history on
                           existing issues/PRs but can no longer be added to
                           new ones. May be used more than once.
      --unarchive "NAME"   Restore a previously archived label NAME. May be
                           used more than once.
  -c, --color  HEX         Set the color of the label named by the preceding
                           --create, --move, --assign, --rename, or --update
                           option. The leading "#" is optional.
  -d, --description TEXT   Set the description of the label named by the
                           preceding --create, --move, --assign, --rename, or
                           --update option. Pass "" to clear an existing
                           description.
  -r, --repos  "R1 R2 .."  Space-separated list of repositories to process.
                           Default: all METplus repositories.
  -o, --org    ORG         GitHub organization. Default: ${ORG}.
  -h, --help               Print this usage statement.

The --color and --description options apply to the operation that immediately
precedes them, so several labels may be updated differently in a single run.
For --move and --assign they describe the target label, which is created if
it does not already exist.

Commands are written in dependency order: unarchive, create, move,
rename/update, assign, archive, strip, delete. That way a label can be
created, assigned, and archived in a single run without the later steps
failing.

See ${SCRIPT_DIR}/README.md for examples and the format of the label file.

EOF
}

# Single-quote a string for safe inclusion in the generated command files
sq() {
  printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"
}

# Escape a string for use inside a jq double-quoted string literal
jq_str() {
  printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'
}

# Percent-encode a label name for use in a REST API URL path. The gh CLI
# does not encode path segments, and label names contain spaces.
urlenc() {
  local str="$1" out="" chr i
  for (( i=0; i<${#str}; i++ )); do
    chr="${str:i:1}"
    case "${chr}" in
      [a-zA-Z0-9.~_-]) out="${out}${chr}" ;;
      *)               out="${out}$(printf '%%%02X' "'${chr}")" ;;
    esac
  done
  printf '%s' "${out}"
}

# Split an "OLD=>NEW" argument
split_old() { printf '%s' "${1%%=>*}"; }
split_new() { printf '%s' "${1#*=>}"; }

# Print a progress message, padding the action tag to a fixed width so that
# the messages line up
log() { printf '  %-11s %s\n' "[$1]" "$2"; }

# Normalize and validate a hex color, stripping any leading "#". GitHub
# stores colors in lowercase, so match that to avoid redundant updates.
check_color() {
  local color="${1#\#}"
  if [[ ! "${color}" =~ ^[0-9A-Fa-f]{6}$ ]]; then
    echo "ERROR: ${SCRIPT_NAME} ... --color must be a 6-digit hex value, not \"$1\"." 1>&2
    exit 1
  fi
  printf '%s' "${color}" | tr '[:upper:]' '[:lower:]'
}

# Look up a label record by name in the cached repository label list
get_rec() {
  awk -F'\t' -v n="$1" '$1 == n {print; exit}' ${TMP_FILE}
}

# The label list is read once per repository, before any commands run, so
# the cache must be kept in step with the commands being generated. That
# way a label can be created, renamed, or unarchived and then referenced by
# a later operation in the same run.
add_rec() {
  printf '%s\t%s\t%s\t\n' "$1" "$2" "$3" >> ${TMP_FILE}
}

rename_rec() {
  awk -F'\t' -v OFS='\t' -v o="$1" -v n="$2" \
      '$1 == o { $1 = n } { print }' ${TMP_FILE} > ${TMP_FILE}.new \
    && mv ${TMP_FILE}.new ${TMP_FILE}
}

unarchive_rec() {
  awk -F'\t' -v OFS='\t' -v n="$1" \
      '$1 == n { $4 = "" } { print }' ${TMP_FILE} > ${TMP_FILE}.new \
    && mv ${TMP_FILE}.new ${TMP_FILE}
}

drop_rec() {
  awk -F'\t' -v n="$1" '$1 != n { print }' ${TMP_FILE} > ${TMP_FILE}.new \
    && mv ${TMP_FILE}.new ${TMP_FILE}
}

archive_rec() {
  awk -F'\t' -v OFS='\t' -v n="$1" \
      '$1 == n && $4 == "" { $4 = "pending" } { print }' ${TMP_FILE} > ${TMP_FILE}.new \
    && mv ${TMP_FILE}.new ${TMP_FILE}
}

# Remember a newly created label, once, to suggest adding it to the label file
note_new() {
  local j
  for (( j=0; j<${#NEW_NAME[@]}; j++ )); do
    [[ "${NEW_NAME[$j]}" == "$1" ]] && return
  done
  NEW_NAME+=("$1")
  NEW_COLOR+=("$2")
  NEW_DESC+=("$3")
}

# Track which operation --color and --description apply to
LAST_OP=""

# Parse the command line
while [[ $# -gt 0 ]]; do
  case "$1" in
    -s|--sync)
      SYNC=1; LAST_OP=""
      # The label file argument is optional
      if [[ -n "$2" && "$2" != -* ]]; then
        SYNC_FILE="$2"; shift 2
      else
        shift 1
      fi ;;
    --prune)
      PRUNE=1; LAST_OP=""; shift 1 ;;
    --create)
      if [[ -z "$2" ]]; then
        echo "ERROR: ${SCRIPT_NAME} ... --create requires a label name."
        exit 1
      fi
      CREATE_LIST+=("$2"); CREATE_COLOR+=("${UNSET}"); CREATE_DESC+=("${UNSET}")
      LAST_OP="create"; shift 2 ;;
    --delete)
      if [[ -z "$2" ]]; then
        echo "ERROR: ${SCRIPT_NAME} ... --delete requires a label name."
        exit 1
      fi
      DELETE_LIST+=("$2"); LAST_OP=""; shift 2 ;;
    -m|--move)
      if [[ "$2" != *"=>"* ]]; then
        echo "ERROR: ${SCRIPT_NAME} ... --move requires an \"OLD=>NEW\" argument."
        exit 1
      fi
      MOVE_LIST+=("$2"); MOVE_COLOR+=("${UNSET}"); MOVE_DESC+=("${UNSET}")
      LAST_OP="move"; shift 2 ;;
    -a|--assign)
      if [[ -z "$2" ]]; then
        echo "ERROR: ${SCRIPT_NAME} ... --assign requires a \"NEW\" or \"OLD=>NEW\" argument."
        exit 1
      fi
      ASSIGN_LIST+=("$2"); ASSIGN_COLOR+=("${UNSET}"); ASSIGN_DESC+=("${UNSET}")
      LAST_OP="assign"; shift 2 ;;
    -n|--rename)
      if [[ "$2" != *"=>"* ]]; then
        echo "ERROR: ${SCRIPT_NAME} ... --rename requires an \"OLD=>NEW\" argument."
        exit 1
      fi
      EDIT_LIST+=("$2"); EDIT_COLOR+=("${UNSET}"); EDIT_DESC+=("${UNSET}")
      LAST_OP="edit"; shift 2 ;;
    -u|--update)
      if [[ -z "$2" ]]; then
        echo "ERROR: ${SCRIPT_NAME} ... --update requires a label name."
        exit 1
      fi
      # Store as a no-op rename so that it shares the --rename code path
      EDIT_LIST+=("$2=>$2"); EDIT_COLOR+=("${UNSET}"); EDIT_DESC+=("${UNSET}")
      LAST_OP="edit"; shift 2 ;;
    --unassign)
      if [[ -z "$2" ]]; then
        echo "ERROR: ${SCRIPT_NAME} ... --unassign requires a label name."
        exit 1
      fi
      UNASSIGN_LIST+=("$2"); LAST_OP=""; shift 2 ;;
    --strip-archived)
      STRIP_ARCHIVED=1; LAST_OP=""; shift 1 ;;
    --archive)
      if [[ -z "$2" ]]; then
        echo "ERROR: ${SCRIPT_NAME} ... --archive requires a label name."
        exit 1
      fi
      ARCHIVE_LIST+=("$2"); LAST_OP=""; shift 2 ;;
    --unarchive)
      if [[ -z "$2" ]]; then
        echo "ERROR: ${SCRIPT_NAME} ... --unarchive requires a label name."
        exit 1
      fi
      UNARCHIVE_LIST+=("$2"); LAST_OP=""; shift 2 ;;
    -c|--color)
      COLOR=$(check_color "$2") || exit 1
      case "${LAST_OP}" in
        create) CREATE_COLOR[${#CREATE_COLOR[@]}-1]="${COLOR}" ;;
        move)   MOVE_COLOR[${#MOVE_COLOR[@]}-1]="${COLOR}" ;;
        assign) ASSIGN_COLOR[${#ASSIGN_COLOR[@]}-1]="${COLOR}" ;;
        edit)   EDIT_COLOR[${#EDIT_COLOR[@]}-1]="${COLOR}" ;;
        *)      echo "ERROR: ${SCRIPT_NAME} ... --color must follow a --create, --move, --assign, --rename, or --update option."
                exit 1 ;;
      esac
      shift 2 ;;
    -d|--description)
      case "${LAST_OP}" in
        create) CREATE_DESC[${#CREATE_DESC[@]}-1]="$2" ;;
        move)   MOVE_DESC[${#MOVE_DESC[@]}-1]="$2" ;;
        assign) ASSIGN_DESC[${#ASSIGN_DESC[@]}-1]="$2" ;;
        edit)   EDIT_DESC[${#EDIT_DESC[@]}-1]="$2" ;;
        *)      echo "ERROR: ${SCRIPT_NAME} ... --description must follow a --create, --move, --assign, --rename, or --update option."
                exit 1 ;;
      esac
      shift 2 ;;
    -r|--repos)  REPO_LIST="$2"; shift 2 ;;
    -o|--org)    ORG="$2";       shift 2 ;;
    -h|--help)   usage; exit 0 ;;
    *)
      echo "ERROR: ${SCRIPT_NAME} ... unrecognized option \"$1\"."
      usage
      exit 1 ;;
  esac
done

if [[ ${PRUNE} -eq 1 && ${SYNC} -eq 0 ]]; then
  echo "ERROR: ${SCRIPT_NAME} ... --prune requires --sync, which defines the labels to keep."
  exit 1
fi

if [[ ${SYNC}               -eq 0 && ${#CREATE_LIST[@]}    -eq 0 && \
      ${#MOVE_LIST[@]}      -eq 0 && ${#ASSIGN_LIST[@]}    -eq 0 && \
      ${#EDIT_LIST[@]}      -eq 0 && ${#ARCHIVE_LIST[@]}   -eq 0 && \
      ${#UNARCHIVE_LIST[@]} -eq 0 && ${#DELETE_LIST[@]}    -eq 0 && \
      ${#UNASSIGN_LIST[@]}  -eq 0 && ${STRIP_ARCHIVED}     -eq 0 ]]; then
  echo "ERROR: ${SCRIPT_NAME} ... must specify at least one label operation."
  usage
  exit 1
fi

# Read the common label definitions
if [[ ${SYNC} -eq 1 ]]; then

  if [[ ! -f "${SYNC_FILE}" ]]; then
    echo "ERROR: ${SCRIPT_NAME} ... label file \"${SYNC_FILE}\" does not exist."
    exit 1
  fi

  if ! command -v jq > /dev/null 2>&1; then
    echo "ERROR: ${SCRIPT_NAME} ... --sync requires jq to parse \"${SYNC_FILE}\"."
    exit 1
  fi

  # One JSON object per line, so a parse error names the offending line
  if ! jq -e . "${SYNC_FILE}" > /dev/null 2>&1; then
    echo "ERROR: ${SCRIPT_NAME} ... \"${SYNC_FILE}\" is not valid JSON. Check for a malformed line:"
    jq -e . "${SYNC_FILE}" 2>&1 > /dev/null | head -3
    exit 1
  fi

  # Fields are separated by a unit separator rather than a tab. Tab counts
  # as IFS whitespace, so read would collapse consecutive tabs and shift an
  # empty description or color into the wrong variable.
  while IFS=$'\037' read -r name color desc arch; do

    if [[ -z "${name}" ]]; then
      echo "ERROR: ${SCRIPT_NAME} ... \"${SYNC_FILE}\" contains an entry with no name."
      exit 1
    fi

    if [[ -z "${color}" ]]; then
      echo "ERROR: ${SCRIPT_NAME} ... \"${SYNC_FILE}\" entry \"${name}\" has no color."
      exit 1
    fi

    SYNC_NAME+=("${name}")
    SYNC_COLOR+=("$(printf '%s' "${color#\#}" | tr '[:upper:]' '[:lower:]')")
    SYNC_DESC+=("${desc}")
    SYNC_ARCH+=("${arch}")

  done < <(jq -r '[.name, (.color // ""), (.description // ""),
                   (if .archived then "true" else "false" end)]
                  | map(gsub("[[:cntrl:]]"; " ")) | join("\u001f")' "${SYNC_FILE}")

  echo "Read ${#SYNC_NAME[@]} label definitions from ${SYNC_FILE}"

fi

# Require a color for new labels so that they are defined consistently
# across every repository rather than being given a random color
for (( i=0; i<${#CREATE_LIST[@]}; i++ )); do
  if [[ "${CREATE_COLOR[$i]}" == "${UNSET}" ]]; then
    echo "ERROR: ${SCRIPT_NAME} ... --create \"${CREATE_LIST[$i]}\" requires --color."
    exit 1
  fi
done

# Check for the GitHub CLI
if ! command -v gh > /dev/null 2>&1; then
  echo "ERROR: ${SCRIPT_NAME} ... the GitHub CLI (gh) is not installed."
  exit 1
fi

if ! gh auth status > /dev/null 2>&1; then
  echo "ERROR: ${SCRIPT_NAME} ... the GitHub CLI (gh) is not authenticated. Run: gh auth login"
  exit 1
fi

mkdir -p ${CMD_DIR}

# Master command file that runs all of the per-repository files
ALL_CMD_FILE="${CMD_DIR}/update_labels_all_cmd.sh"
echo '#!/bin/bash' > ${ALL_CMD_FILE}
echo 'cd "$(dirname "$0")" || exit 1' >> ${ALL_CMD_FILE}

TMP_FILE=$(mktemp)
trap "rm -f ${TMP_FILE} ${TMP_FILE}.new" EXIT

N_REPO_FILES=0

# Process each repository
for REPO in ${REPO_LIST}; do

  SLUG="${ORG}/${REPO}"

  echo
  echo "Processing repository: ${SLUG}"

  # Get the current labels as name<TAB>color<TAB>description<TAB>archived_at
  if ! gh api "repos/${SLUG}/labels" --paginate \
       --jq '.[] | [.name, .color, (.description // ""), (.archived_at // "")] | @tsv' \
       > ${TMP_FILE} 2>/dev/null; then
    echo "  WARNING: unable to list labels for ${SLUG}, skipping."
    continue
  fi

  CMD_FILE="${CMD_DIR}/update_labels_${REPO}_cmd.sh"
  echo "#!/bin/bash -v" > ${CMD_FILE}

  n_cmd=0

  # Unarchive labels first, so that they can be assigned further below
  for NAME in "${UNARCHIVE_LIST[@]}"; do

    REC=$(get_rec "${NAME}")

    if [[ -z "${REC}" ]]; then
      # Archived labels may be omitted from the label listing, so issue the
      # request anyway rather than assuming the label does not exist
      log UNARCHIVE "${SLUG} label ... ${NAME} (not listed, attempting anyway)"
    elif [[ -z "$(printf '%s' "${REC}" | cut -f4)" ]]; then
      log SKIP "${SLUG} label ... ${NAME} is not archived"
      continue
    else
      log UNARCHIVE "${SLUG} label ... ${NAME}"
    fi

    LABEL_PATH="repos/${SLUG}/labels/$(urlenc "${NAME}")"
    echo "gh api --method PATCH $(sq "${LABEL_PATH}") \
-F archived=false --silent" >> ${CMD_FILE}
    ((n_cmd+=1))

    if [[ -z "${REC}" ]]; then
      add_rec "${NAME}" "" ""
    else
      unarchive_rec "${NAME}"
    fi

  done

  # Bring the repository in line with the common label definitions. Creates,
  # edits, and unarchives happen here; archiving is deferred to the archive
  # phase below so that labels stay assignable for as long as possible.
  n_sync_ok=0
  for (( i=0; i<${#SYNC_NAME[@]}; i++ )); do

    NAME="${SYNC_NAME[$i]}"
    COLOR="${SYNC_COLOR[$i]}"
    DESC="${SYNC_DESC[$i]}"
    WANT_ARCH="${SYNC_ARCH[$i]}"

    REC=$(get_rec "${NAME}")

    # Create a missing label. The GitHub API accepts "archived" only when
    # updating a label, so a label that should be archived is created first
    # and archived below.
    if [[ -z "${REC}" ]]; then
      log CREATE "${SLUG} label ... ${NAME}"
      echo "gh label create $(sq "${NAME}") -R $(sq "${SLUG}") \
--color $(sq "${COLOR}") --description $(sq "${DESC}")" >> ${CMD_FILE}
      ((n_cmd+=1))
      add_rec "${NAME}" "${COLOR}" "${DESC}"
      continue
    fi

    CUR_COLOR=$(printf '%s' "${REC}" | cut -f2)
    CUR_DESC=$(printf '%s' "${REC}" | cut -f3)
    CUR_ARCH=$(printf '%s' "${REC}" | cut -f4)

    # Correct the color and description
    EDIT_CMD="gh label edit $(sq "${NAME}") -R $(sq "${SLUG}")"
    ACTION=""

    if [[ "${COLOR}" != "${CUR_COLOR}" ]]; then
      EDIT_CMD="${EDIT_CMD} --color $(sq "${COLOR}")"
      ACTION="${ACTION} [color ${CUR_COLOR} -> ${COLOR}]"
    fi

    if [[ "${DESC}" != "${CUR_DESC}" ]]; then
      EDIT_CMD="${EDIT_CMD} --description $(sq "${DESC}")"
      ACTION="${ACTION} [description]"
    fi

    if [[ -n "${ACTION}" ]]; then
      log EDIT "${SLUG} label ... ${NAME}${ACTION}"
      echo "${EDIT_CMD}" >> ${CMD_FILE}
      ((n_cmd+=1))
    fi

    # Restore a label that should not be archived
    if [[ "${WANT_ARCH}" == "false" && -n "${CUR_ARCH}" ]]; then
      LABEL_PATH="repos/${SLUG}/labels/$(urlenc "${NAME}")"
      log UNARCHIVE "${SLUG} label ... ${NAME}"
      echo "gh api --method PATCH $(sq "${LABEL_PATH}") \
-F archived=false --silent" >> ${CMD_FILE}
      ((n_cmd+=1))
      unarchive_rec "${NAME}"
    elif [[ -z "${ACTION}" ]]; then
      ((n_sync_ok+=1))
    fi

  done

  if [[ ${SYNC} -eq 1 ]]; then
    log SYNC "${SLUG} ... ${n_sync_ok} of ${#SYNC_NAME[@]} common labels already correct"
  fi

  # Create entirely new labels
  for (( i=0; i<${#CREATE_LIST[@]}; i++ )); do

    NAME="${CREATE_LIST[$i]}"
    COLOR="${CREATE_COLOR[$i]}"
    DESC="${CREATE_DESC[$i]}"

    REC=$(get_rec "${NAME}")

    if [[ -n "${REC}" ]]; then
      log SKIP "${SLUG} already defines a \"${NAME}\" label"
      echo "              Use --update \"${NAME}\" to change its color or description."
      continue
    fi

    CREATE_CMD="gh label create $(sq "${NAME}") -R $(sq "${SLUG}") --color $(sq "${COLOR}")"
    if [[ "${DESC}" != "${UNSET}" ]]; then
      CREATE_CMD="${CREATE_CMD} --description $(sq "${DESC}")"
    fi

    log CREATE "${SLUG} label ... ${NAME}"
    echo "${CREATE_CMD}" >> ${CMD_FILE}
    ((n_cmd+=1))

    if [[ "${DESC}" == "${UNSET}" ]]; then
      add_rec "${NAME}" "${COLOR}" ""
      note_new "${NAME}" "${COLOR}" ""
    else
      add_rec "${NAME}" "${COLOR}" "${DESC}"
      note_new "${NAME}" "${COLOR}" "${DESC}"
    fi

  done

  # Reassign issues/PRs from one label to another and delete the old label
  for (( i=0; i<${#MOVE_LIST[@]}; i++ )); do

    OLD=$(split_old "${MOVE_LIST[$i]}")
    NEW=$(split_new "${MOVE_LIST[$i]}")
    COLOR="${MOVE_COLOR[$i]}"
    DESC="${MOVE_DESC[$i]}"

    OLD_REC=$(get_rec "${OLD}")
    NEW_REC=$(get_rec "${NEW}")

    if [[ -z "${OLD_REC}" ]]; then
      log SKIP "no \"${OLD}\" label defined in ${SLUG}"
      continue
    fi

    if [[ -z "${NEW_REC}" ]]; then

      # Create the target label, defaulting to the color and description of
      # the label being replaced
      if [[ "${COLOR}" == "${UNSET}" ]]; then
        COLOR=$(printf '%s' "${OLD_REC}" | cut -f2)
      fi
      if [[ "${DESC}" == "${UNSET}" ]]; then
        DESC=$(printf '%s' "${OLD_REC}" | cut -f3)
      fi

      log CREATE "${SLUG} label ... ${NEW}"
      echo "gh label create $(sq "${NEW}") -R $(sq "${SLUG}") \
--color $(sq "${COLOR}") --description $(sq "${DESC}")" >> ${CMD_FILE}
      ((n_cmd+=1))
      add_rec "${NEW}" "${COLOR}" "${DESC}"
      note_new "${NEW}" "${COLOR}" "${DESC}"

    else

      # Archived labels cannot be added to issues or pull requests
      if [[ -n "$(printf '%s' "${NEW_REC}" | cut -f4)" ]]; then
        echo "  WARNING: ${SLUG} label \"${NEW}\" is archived and cannot be assigned."
        echo "           Add --unarchive \"${NEW}\" to restore it first."
        continue
      fi

      if [[ "${COLOR}" != "${UNSET}" || "${DESC}" != "${UNSET}" ]]; then

        # The target label already exists, so update it in place
        EDIT_CMD="gh label edit $(sq "${NEW}") -R $(sq "${SLUG}")"
        if [[ "${COLOR}" != "${UNSET}" ]]; then
          EDIT_CMD="${EDIT_CMD} --color $(sq "${COLOR}")"
        fi
        if [[ "${DESC}" != "${UNSET}" ]]; then
          EDIT_CMD="${EDIT_CMD} --description $(sq "${DESC}")"
        fi

        log UPDATE "${SLUG} label ... ${NEW}"
        echo "${EDIT_CMD}" >> ${CMD_FILE}
        ((n_cmd+=1))

      fi

    fi

    # The REST issues endpoint returns both issues and pull requests
    NUMBERS=$(gh api "repos/${SLUG}/issues" --paginate -X GET \
             -f state=all -f per_page=100 -f labels="${OLD}" \
             --jq '.[].number' 2>/dev/null)

    n_num=$(printf '%s' "${NUMBERS}" | grep -c '[0-9]')
    log MOVE "${SLUG} ... ${n_num} issues/PRs from \"${OLD}\" to \"${NEW}\""

    for NUM in ${NUMBERS}; do
      echo "gh api --method POST $(sq "repos/${SLUG}/issues/${NUM}/labels") \
-f $(sq "labels[]=${NEW}") --silent" >> ${CMD_FILE}
      ((n_cmd+=1))
    done

    # Deleting the old label removes it from every issue/PR
    log DELETE "${SLUG} label ... ${OLD}"
    echo "gh label delete $(sq "${OLD}") -R $(sq "${SLUG}") --yes" >> ${CMD_FILE}
    ((n_cmd+=1))
    drop_rec "${OLD}"

  done

  # Rename existing labels and/or update their color and description
  for (( i=0; i<${#EDIT_LIST[@]}; i++ )); do

    OLD=$(split_old "${EDIT_LIST[$i]}")
    NEW=$(split_new "${EDIT_LIST[$i]}")
    COLOR="${EDIT_COLOR[$i]}"
    DESC="${EDIT_DESC[$i]}"

    OLD_REC=$(get_rec "${OLD}")

    if [[ -z "${OLD_REC}" ]]; then
      log SKIP "no \"${OLD}\" label defined in ${SLUG}"
      continue
    fi

    # Build the command, including only the attributes that are changing
    EDIT_CMD="gh label edit $(sq "${OLD}") -R $(sq "${SLUG}")"
    ACTION=""

    if [[ "${OLD}" != "${NEW}" ]]; then

      NEW_REC=$(get_rec "${NEW}")

      if [[ -n "${NEW_REC}" ]]; then
        echo "  WARNING: ${SLUG} already defines a \"${NEW}\" label."
        echo "           Use --move \"${OLD}=>${NEW}\" to merge them instead of renaming."
        continue
      fi

      EDIT_CMD="${EDIT_CMD} --name $(sq "${NEW}")"
      ACTION="${OLD} -> ${NEW}"
    else
      ACTION="${OLD}"
    fi

    CUR_COLOR=$(printf '%s' "${OLD_REC}" | cut -f2)
    CUR_DESC=$(printf '%s' "${OLD_REC}" | cut -f3)

    if [[ "${COLOR}" != "${UNSET}" && "${COLOR}" != "${CUR_COLOR}" ]]; then
      EDIT_CMD="${EDIT_CMD} --color $(sq "${COLOR}")"
      ACTION="${ACTION} [color ${CUR_COLOR} -> ${COLOR}]"
    fi

    if [[ "${DESC}" != "${UNSET}" && "${DESC}" != "${CUR_DESC}" ]]; then
      EDIT_CMD="${EDIT_CMD} --description $(sq "${DESC}")"
      ACTION="${ACTION} [description updated]"
    fi

    # Nothing left to change
    if [[ "${EDIT_CMD}" != *" --name "* && \
          "${EDIT_CMD}" != *" --color "* && \
          "${EDIT_CMD}" != *" --description "* ]]; then
      log SKIP "${SLUG} label ... ${OLD} already up to date"
      continue
    fi

    log EDIT "${SLUG} label ... ${ACTION}"
    echo "${EDIT_CMD}" >> ${CMD_FILE}
    ((n_cmd+=1))

    if [[ "${OLD}" != "${NEW}" ]]; then
      rename_rec "${OLD}" "${NEW}"
    fi

  done

  # Assign a label to open issues/PRs, optionally filtered by a source label
  for (( i=0; i<${#ASSIGN_LIST[@]}; i++ )); do

    COLOR="${ASSIGN_COLOR[$i]}"
    DESC="${ASSIGN_DESC[$i]}"

    # "OLD=>NEW" filters by a source label, "NEW" applies to all open items
    if [[ "${ASSIGN_LIST[$i]}" == *"=>"* ]]; then
      OLD=$(split_old "${ASSIGN_LIST[$i]}")
      NEW=$(split_new "${ASSIGN_LIST[$i]}")
    else
      OLD=""
      NEW="${ASSIGN_LIST[$i]}"
    fi

    # A source label that does not exist here matches nothing
    if [[ -n "${OLD}" && -z "$(get_rec "${OLD}")" ]]; then
      log SKIP "no \"${OLD}\" label defined in ${SLUG}"
      continue
    fi

    NEW_REC=$(get_rec "${NEW}")

    if [[ -z "${NEW_REC}" ]]; then

      # Default the color and description of the target label to those of
      # the source label, as for --move
      if [[ -n "${OLD}" ]]; then
        OLD_REC=$(get_rec "${OLD}")
        if [[ "${COLOR}" == "${UNSET}" ]]; then
          COLOR=$(printf '%s' "${OLD_REC}" | cut -f2)
        fi
        if [[ "${DESC}" == "${UNSET}" ]]; then
          DESC=$(printf '%s' "${OLD_REC}" | cut -f3)
        fi
      fi

      # Otherwise, only create the target label when told how it should
      # look, rather than letting the API invent a random color
      if [[ "${COLOR}" == "${UNSET}" && "${DESC}" == "${UNSET}" ]]; then
        echo "  WARNING: ${SLUG} has no \"${NEW}\" label to assign."
        echo "           Add --color and/or --description to create it."
        continue
      fi

      CREATE_CMD="gh label create $(sq "${NEW}") -R $(sq "${SLUG}")"
      if [[ "${COLOR}" != "${UNSET}" ]]; then
        CREATE_CMD="${CREATE_CMD} --color $(sq "${COLOR}")"
      fi
      if [[ "${DESC}" != "${UNSET}" ]]; then
        CREATE_CMD="${CREATE_CMD} --description $(sq "${DESC}")"
      fi

      log CREATE "${SLUG} label ... ${NEW}"
      echo "${CREATE_CMD}" >> ${CMD_FILE}
      ((n_cmd+=1))

      [[ "${COLOR}" == "${UNSET}" ]] && COLOR=""
      [[ "${DESC}"  == "${UNSET}" ]] && DESC=""
      add_rec  "${NEW}" "${COLOR}" "${DESC}"
      note_new "${NEW}" "${COLOR}" "${DESC}"

    elif [[ -n "$(printf '%s' "${NEW_REC}" | cut -f4)" ]]; then

      echo "  WARNING: ${SLUG} label \"${NEW}\" is archived and cannot be assigned."
      echo "           Add --unarchive \"${NEW}\" to restore it first."
      continue

    fi

    # Query open issues/PRs, skipping any that already carry the target
    # label so that the generated commands stay idempotent
    JQ_FILTER=".[] | select([.labels[].name] | index(\"$(jq_str "${NEW}")\") | not) | .number"

    if [[ -n "${OLD}" ]]; then
      NUMBERS=$(gh api "repos/${SLUG}/issues" --paginate -X GET \
               -f state=open -f per_page=100 -f labels="${OLD}" \
               --jq "${JQ_FILTER}" 2>/dev/null)
      LABEL_DESC="open issues/PRs labelled \"${OLD}\""
    else
      NUMBERS=$(gh api "repos/${SLUG}/issues" --paginate -X GET \
               -f state=open -f per_page=100 \
               --jq "${JQ_FILTER}" 2>/dev/null)
      LABEL_DESC="open issues/PRs"
    fi

    n_num=$(printf '%s' "${NUMBERS}" | grep -c '[0-9]')
    log ASSIGN "${SLUG} ... \"${NEW}\" to ${n_num} ${LABEL_DESC}"

    for NUM in ${NUMBERS}; do
      echo "gh api --method POST $(sq "repos/${SLUG}/issues/${NUM}/labels") \
-f $(sq "labels[]=${NEW}") --silent" >> ${CMD_FILE}
      ((n_cmd+=1))
    done

  done

  # Archive the common labels that are marked archived in the label file
  for (( i=0; i<${#SYNC_NAME[@]}; i++ )); do

    [[ "${SYNC_ARCH[$i]}" == "true" ]] || continue

    NAME="${SYNC_NAME[$i]}"
    REC=$(get_rec "${NAME}")

    # Already archived
    [[ -z "$(printf '%s' "${REC}" | cut -f4)" ]] || continue

    LABEL_PATH="repos/${SLUG}/labels/$(urlenc "${NAME}")"
    log ARCHIVE "${SLUG} label ... ${NAME}"
    echo "gh api --method PATCH $(sq "${LABEL_PATH}") \
-F archived=true --silent" >> ${CMD_FILE}
    ((n_cmd+=1))
    archive_rec "${NAME}"

  done

  # Archive labels last, after any assignments that reference them
  for NAME in "${ARCHIVE_LIST[@]}"; do

    REC=$(get_rec "${NAME}")

    if [[ -z "${REC}" ]]; then
      log SKIP "no \"${NAME}\" label defined in ${SLUG}"
      continue
    fi

    if [[ -n "$(printf '%s' "${REC}" | cut -f4)" ]]; then
      log SKIP "${SLUG} label ... ${NAME} is already archived"
      continue
    fi

    log ARCHIVE "${SLUG} label ... ${NAME}"
    LABEL_PATH="repos/${SLUG}/labels/$(urlenc "${NAME}")"
    echo "gh api --method PATCH $(sq "${LABEL_PATH}") \
-F archived=true --silent" >> ${CMD_FILE}
    ((n_cmd+=1))
    archive_rec "${NAME}"

  done

  # Remove labels from the open issues/PRs, keeping the label itself and its
  # assignments on closed issues/PRs. This runs after the archive phase so
  # that --strip-archived also covers labels archived earlier in this run.
  STRIP_LIST=("${UNASSIGN_LIST[@]}")

  if [[ ${STRIP_ARCHIVED} -eq 1 ]]; then
    while IFS=$'\037' read -r name color desc arch; do
      [[ -n "${name}" && -n "${arch}" ]] || continue
      # Skip any label already named by --unassign
      SEEN=0
      for EXISTING in "${STRIP_LIST[@]}"; do
        [[ "${EXISTING}" == "${name}" ]] && SEEN=1 && break
      done
      [[ ${SEEN} -eq 1 ]] || STRIP_LIST+=("${name}")
    done < <(tr '\t' '\037' < ${TMP_FILE})
  fi

  for NAME in "${STRIP_LIST[@]}"; do

    if [[ -z "$(get_rec "${NAME}")" ]]; then
      log SKIP "no \"${NAME}\" label defined in ${SLUG}"
      continue
    fi

    NUMBERS=$(gh api "repos/${SLUG}/issues" --paginate -X GET \
             -f state=open -f per_page=100 -f labels="${NAME}" \
             --jq '.[].number' 2>/dev/null)

    n_num=$(printf '%s' "${NUMBERS}" | grep -c '[0-9]')

    if [[ ${n_num} -eq 0 ]]; then
      log SKIP "${SLUG} ... no open issues/PRs labelled \"${NAME}\""
      continue
    fi

    log STRIP "${SLUG} ... \"${NAME}\" from ${n_num} open issues/PRs"

    ENC=$(urlenc "${NAME}")
    for NUM in ${NUMBERS}; do
      echo "gh api --method DELETE $(sq "repos/${SLUG}/issues/${NUM}/labels/${ENC}") \
--silent" >> ${CMD_FILE}
      ((n_cmd+=1))
    done

  done

  # Delete labels last, since this is the one step that cannot be undone
  for NAME in "${DELETE_LIST[@]}"; do

    REC=$(get_rec "${NAME}")

    if [[ -z "${REC}" ]]; then
      log SKIP "no \"${NAME}\" label defined in ${SLUG}"
      continue
    fi

    # Report how many issues/PRs would lose the label, so that the generated
    # commands can be reviewed with that in mind
    NUMBERS=$(gh api "repos/${SLUG}/issues" --paginate -X GET \
             -f state=all -f per_page=100 -f labels="${NAME}" \
             --jq '.[].number' 2>/dev/null)
    n_num=$(printf '%s' "${NUMBERS}" | grep -c '[0-9]')

    log DELETE "${SLUG} label ... ${NAME} (removes it from ${n_num} issues/PRs)"
    echo "# Deletes \"${NAME}\" from ${n_num} issues/PRs in ${SLUG}. This cannot be undone." >> ${CMD_FILE}
    echo "gh label delete $(sq "${NAME}") -R $(sq "${SLUG}") --yes" >> ${CMD_FILE}
    ((n_cmd+=1))
    drop_rec "${NAME}"

  done

  # Delete repository labels that are absent from the label file, keeping
  # the component- and repository-specific custom labels
  if [[ ${PRUNE} -eq 1 ]]; then

    n_keep=0
    n_custom=0

    # Translate the cached tabs to a unit separator, since read would
    # otherwise collapse the empty fields and misreport the archived state
    while IFS=$'\037' read -r name color desc arch; do

      [[ -n "${name}" ]] || continue

      # Keep the common labels
      IS_COMMON=0
      for (( i=0; i<${#SYNC_NAME[@]}; i++ )); do
        if [[ "${SYNC_NAME[$i]}" == "${name}" ]]; then
          IS_COMMON=1
          break
        fi
      done

      if [[ ${IS_COMMON} -eq 1 ]]; then
        ((n_keep+=1))
        continue
      fi

      # Keep the custom, repository-specific labels
      if printf '%s' "${name}" | egrep -qi "${KEEP_PATTERN}"; then
        ((n_custom+=1))
        continue
      fi

      # Keep archived labels. Archiving is the deliberate way to retire a
      # label without losing its history, so deleting one here would throw
      # away exactly what archiving was meant to preserve.
      if [[ -n "${arch}" ]]; then
        ((n_custom+=1))
        continue
      fi

      NUMBERS=$(gh api "repos/${SLUG}/issues" --paginate -X GET \
               -f state=all -f per_page=100 -f labels="${name}" \
               --jq '.[].number' 2>/dev/null)
      n_num=$(printf '%s' "${NUMBERS}" | grep -c '[0-9]')

      log PRUNE "${SLUG} label ... ${name} (removes it from ${n_num} issues/PRs)"
      echo "# Prunes \"${name}\" from ${n_num} issues/PRs in ${SLUG}. This cannot be undone." >> ${CMD_FILE}
      echo "gh label delete $(sq "${name}") -R $(sq "${SLUG}") --yes" >> ${CMD_FILE}
      ((n_cmd+=1))

    done < <(tr '\t' '\037' < ${TMP_FILE})

    log PRUNE "${SLUG} ... kept ${n_keep} common and ${n_custom} custom labels"

  fi

  # Discard command files with nothing to do
  if [[ ${n_cmd} -eq 0 ]]; then
    echo "  Nothing to do for ${SLUG}."
    rm -f ${CMD_FILE}
    continue
  fi

  chmod +x ${CMD_FILE}
  echo "./$(basename ${CMD_FILE})" >> ${ALL_CMD_FILE}
  ((N_REPO_FILES+=1))

  echo "  Wrote ${n_cmd} commands to ${CMD_FILE}"

done

echo

if [[ ${N_REPO_FILES} -eq 0 ]]; then
  echo "No label changes are required."
  rm -f ${ALL_CMD_FILE}
  exit 0
fi

chmod +x ${ALL_CMD_FILE}

echo "Wrote command files for ${N_REPO_FILES} repositories."
echo "Review them and then apply all of the changes by running:"
echo "  ${ALL_CMD_FILE}"

# Suggest definitions for the new labels that are not already common, so
# that they can be added to the label file and kept in sync
n_new=0
for (( j=0; j<${#NEW_NAME[@]}; j++ )); do

  NAME=$(jq_str "${NEW_NAME[$j]}")
  if grep -Fq "\"name\": \"${NAME}\"" "${SYNC_FILE}" 2>/dev/null; then
    continue
  fi

  if [[ ${n_new} -eq 0 ]]; then
    echo
    echo "If the new labels should be common to all repositories, add these"
    echo "lines to ${SYNC_FILE}:"
    echo
  fi

  printf '{"name": "%s","color": "%s","description": "%s","archived": false}\n' \
    "${NAME}" "${NEW_COLOR[$j]}" "$(jq_str "${NEW_DESC[$j]}")"
  ((n_new+=1))

done
