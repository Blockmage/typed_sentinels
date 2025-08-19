# shellcheck shell=bash

SOURCED=${SOURCED:-"0"}
ARG0="${BASH_SOURCE[0]:-"$0"}"

SCRIPTS_DIR="$(cd "$(dirname -- "$ARG0")" && pwd)"
WORKSPACE_ROOT="$(cd "$(dirname -- "$SCRIPTS_DIR")" && pwd)"

ENV_FILE="${ENV_FILE:-}"
VENV_DIR="${VENV_DIR:-}"

export SOURCED ENV_FILE VENV_DIR SCRIPTS_DIR WORKSPACE_ROOT

cmd_exists() {
  if [ $# -eq 1 ]; then
    command -v "$1" >/dev/null 2>&1
  elif [ $# -gt 1 ]; then
    for cmd in "$@"; do
      if ! command -v "$cmd" >/dev/null 2>&1; then
        return 1
      fi
    done
  fi
  return $?
}

walk_tree() {
  local current target depth=0 max=9
  local startdir="${1:-"${SCRIPTS_DIR:-}"}"
  local fname="${2:-".env"}"
  local ftype="${3:-"f"}"

  current="$startdir"
  while [ "$current" != "/" ] && [ "$depth" -lt "$max" ]; do
    target="${current}/${fname}"

    case "$ftype" in
      f) [ -f "$target" ] && printf '%s\n' "$target" && return 0 ;;
      d) [ -d "$target" ] && printf '%s\n' "$target" && return 0 ;;
      *) [ -e "$target" ] && printf '%s\n' "$target" && return 0 ;;
    esac

    current="$(dirname -- "$current")"
    ((depth++))
  done

  return 1
}

_get_log_label() {
  local level="$1"
  case "$level" in
    0* | x | X) level="[ EMERG   ]" ;;
    10 | a | A) level="[ ALERT   ]" ;;
    20 | c | C) level="[ CRIT    ]" ;;
    30 | e | E) level="[ ERROR   ]" ;;
    40 | w | W) level="[ WARN    ]" ;;
    50 | n | N) level="[ NOTICE  ]" ;;
    55 | s | S) level="[ SUCCESS ]" ;;
    60 | i | I) level="[ INFO    ]" ;;
    70 | d | D) level="[ DEBUG   ]" ;;
    *) return 1 ;;
  esac
  echo -en "$level"
}

log_msg() {
  local level tstamp msg src=""

  if ! level="$(_get_log_label "${1:-}")"; then
    level="$(_get_log_label "i")"
  else
    shift
  fi

  [ "$level" = '[ DEBUG   ]' ] && [ "${DEBUG:-}" = "" ] && return
  [ "${CTX_LOGCALLER:-}" != "" ] && src="[ ${CTX_LOGCALLER} ]"

  tstamp="[ $(date -u +"%Y-%m-%dT%H:%M:%S%z") ]"
  msg="$(echo -e "$*" | tr -s '[:blank:]')"

  if [ "$src" != "" ]; then
    msg="$tstamp $level $src $msg"
  else
    msg="$tstamp $level $msg"
  fi

  if [ "${SCRIPTS_LOGFILE:="/dev/null"}" != "/dev/null" ]; then
    echo -e "$msg" | tee -a "$SCRIPTS_LOGFILE"
  else
    echo -e "$msg"
  fi
}

_demo_logging() {
  local levels=(
    70 d D
    60 i I
    55 s S
    50 n N
    40 w W
    30 e E
    20 c C
    10 a A
    00 x X
  )
  for i in "${levels[@]}"; do
    log_msg "$i" "Test at level $i"
  done
}

setup_dotenv() {
  if [ "${ENV_FILE:-}" = "" ]; then
    ENV_FILE="$(walk_tree "$SCRIPTS_DIR" ".env")"
    if [ "$ENV_FILE" = "" ]; then
      ENV_FILE="${WORKSPACE_ROOT}/.env"
    fi
  fi

  # shellcheck disable=SC1090
  { touch "$ENV_FILE" && source "$ENV_FILE"; } 2>/dev/null
  if ! grep -q 'WORKSPACE_ROOT=' "$ENV_FILE" 2>/dev/null; then
    echo "export WORKSPACE_ROOT=\"${WORKSPACE_ROOT}\"" >>"$ENV_FILE"
  fi
}

_check_pre_commit_last_update() {
  local now last fp key max

  fp="${ENV_FILE:-"$WORKSPACE_ROOT/.env"}"
  key="${1:-"PRE_COMMIT_LAST_UPDATE"}"
  max="${2:-"86400"}"
  now="$(date +'%s')"

  [ -e "$fp" ] || return

  last="$(awk -F'=' \
    '/^[[:space:]]*(export[[:space:]]+)?'"$key"'[[:space:]]*=/ \
    {gsub(/^[[:space:]]*|[[:space:]]*$/, "", $2); \
    gsub(/^["'\'']*|["'\'']*$/, "", $2); print $2}' "$fp" 2>/dev/null)"

  if [ "$last" = "" ] || ((now - last > max)); then
    if ! grep -q "^[[:space:]]*\(export[[:space:]]\+\)\?${key}[[:space:]]*=" \
      "$fp" 2>/dev/null; then
      echo "export ${key}=${now}" >>"$fp"
    else
      awk '/^[[:space:]]*(export[[:space:]]+)?'"$key"'[[:space:]]*=/ \
        {print "export '"$key"'='"$now"'"; next} {print}' \
        "$fp" >"${fp}.tmp" && mv "${fp}.tmp" "$fp"
    fi
    return 0
  fi

  return 1
}

# shellcheck disable=SC2120
setup_pre_commit() {
  local root="${WORKSPACE_ROOT:-}"
  local hooks=(pre-push commit-msg)

  if [ $# -ge 1 ] && [ -d "$1" ]; then
    root="${1:-}"
    shift 1
  fi

  if [ "$*" != "" ]; then
    hooks=("$@")
  fi

  if ! cmd_exists pre-commit; then
    log_msg 'd' "Command not found: 'pre-commit'"
    return
  elif [ ! -d "$root/.git" ]; then
    log_msg 'd' "Not a Git repository: '$root/.git' does not exist"
    return
  elif [ ! -f "$root/.pre-commit-config.yaml" ]; then
    log_msg 'd' "No '.pre-commit-config.yaml' found in '$root'"
    return
  fi

  if [ ! -e "$root/.git/hooks/pre-commit" ]; then
    if ! pre-commit install --install-hooks; then
      log_msg 'e' "Failed to install pre-commit hooks"
      return 1
    fi
  fi

  for hook in "${hooks[@]}"; do
    if [ "$hook" != "" ] && [ ! -e "$root/.git/hooks/$hook" ]; then
      if ! pre-commit install --hook-type "$hook" >/dev/null 2>&1; then
        log_msg 'w' "Failed to install hook: $hook"
      fi
    fi
  done

  if _check_pre_commit_last_update "PRE_COMMIT_LAST_UPDATE" "259200"; then
    log_msg 'i' "Updating pre-commit hooks (this may take a minute)..."

    if pre-commit autoupdate >/dev/null 2>&1; then
      log_msg 's' "...done!"
    else
      log_msg 'e' "Failed to update pre-commit hooks"
    fi
  fi
}

setup_virtual_env() {
  local venv_dir="${WORKSPACE_ROOT:?}/.venv"
  local pyproject="${WORKSPACE_ROOT:?}/pyproject.toml"

  if [ "$VENV_DIR" = "" ] || [ ! -d "$VENV_DIR" ]; then
    local _basename
    _basename="$(basename -- "${VENV_DIR:-".venv"}")"
    VENV_DIR="$(walk_tree "$SCRIPTS_DIR" "$_basename" "d")"
    if [ "$VENV_DIR" != "" ] && [ -f "${VENV_DIR}/bin/activate" ]; then
      venv_dir="$VENV_DIR"
    fi
  fi

  if [ -s "$venv_dir/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$venv_dir/bin/activate"

  elif [ ! -d "$venv_dir" ] && [ -s "$pyproject" ]; then
    if cmd_exists uv; then
      if cd "$WORKSPACE_ROOT"; then
        touch "$WORKSPACE_ROOT/README.md"

        log_msg 'i' \
          "Setting up Python environment (this may take a minute)..."

        if uv sync --all-groups 2>/dev/null; then
          log_msg 's' "...done!"
        else
          log_msg 'e' "...something went wrong!"
        fi

      fi
    else
      log_msg 'd' "Exit function - 'uv' not available"
    fi
  else
    log_msg 'd' "Exit function - No 'pyproject.toml' (tried: '$pyproject')"
  fi
}

# ================================= Begin Main =================================

setup_dotenv
setup_pre_commit
setup_virtual_env
