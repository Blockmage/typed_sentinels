#!/usr/bin/env bash

set -e

DEBUG=1

ARG0="${BASH_SOURCE[0]:-"$0"}"
HERE="$(cd "$(dirname -- "$ARG0")" && pwd)"
WORKSPACE_ROOT="$(cd "$(dirname -- "$HERE")" && pwd)"

ENV_FILE="$WORKSPACE_ROOT/.env"

LOCKDIR="$WORKSPACE_ROOT/.on_save.lock"
mkdir "$LOCKDIR" || exit 0

# shellcheck source=/dev/null
[ -f "$ENV_FILE" ] && source "$ENV_FILE"

cleanup() {
  if [ -d "$LOCKDIR" ]; then
    [ "${DEBUG:-}" -eq 1 ] && echo -e "Removing lock:\n\tlock_dir='$LOCKDIR'"
    rmdir "$LOCKDIR"
  fi
}

trap cleanup EXIT INT TERM

_docformatter="$WORKSPACE_ROOT/.venv/bin/docformatter"
_markdownlint_cli2="/opt/homebrew/bin/markdownlint-cli2"
_prettier="${XDG_DATA_HOME:="$HOME/.local/share"}/bun/bin/prettier"
_shellharden="$XDG_DATA_HOME/cargo/bin/shellharden"
_shfmt="/opt/homebrew/bin/shfmt"
_taplo="/opt/homebrew/bin/taplo"
_yamlfmt="$HOME/go/bin/yamlfmt"

debug_log() {
  [ "${DEBUG:-}" -eq 1 ] && echo -e "$@"
}

get_cmd() {
  local cmd="$1"
  [ -x "$cmd" ] && echo "$cmd" && return 0
  cmd="$(basename -- "$cmd")"
  command -v "$cmd" >/dev/null 2>&1 && echo "$cmd" && return 0
  return 1
}

run_cmd() {
  local cmd="$1" target="$2" args=("${@:3}")

  [ ! -f "$target" ] && [ ! -L "$target" ] && return 1

  if [ -L "$target" ]; then
    target="$(readlink "$target")"
  fi

  if cmd="$(get_cmd "$cmd")"; then
    debug_log "Executing command:\n" \
      "\tcmd='${cmd:-}'\n" \
      "\targs='${args[*]}'\n" \
      "\ttarget='${target:-}'\n" \
      "\tfull_cmd='$cmd ${args[*]} $target'"

    if [ ${#args[@]} -gt 0 ]; then
      "$cmd" "${args[@]}" "$target"
    else
      "$cmd" "$target"
    fi

  else
    debug_log "Command not found:\n" \
      "\tcmd='${cmd:-}'\n" \
      "\targs='${args[*]}'\n" \
      "\ttarget='${target:-}'\n" \
      "\tfull_cmd='$cmd ${args[*]} $target'"
    return 1
  fi
}

increment_filename() {
  local file="$1" dir base
  dir=$(dirname "$file")
  base=$(basename "$file")

  case "$base" in
    .*.*) lead_dot="." name="${base#*.}" ;;
    .*) lead_dot="." name="${base#.}" ;;
    *) lead_dot="" name="$base" ;;
  esac

  local stem="${name%.*}"
  local ext="${name##*.}"
  [ "$stem" = "$ext" ] && ext="" || ext=".${ext}"

  i=1
  new="${dir}/${lead_dot}${stem}${ext}"
  while [ -e "$new" ]; do
    new="${dir}/${lead_dot}${stem}_${i}${ext}"
    i=$((i + 1))
  done

  printf '%s\n' "$new"
}

fmt_md() {
  local file="$1"
  local args cfg w_cfg p_cfg

  args=(
    "--prose-wrap" "always"
    "--print-width" "100"
    "--end-of-line" "auto"
    "--parser" "markdown"
    "--tab-width" "4"
    "--write"
  )

  p_cfg="$("$_prettier" --find-config-path "$file" 2>/dev/null)"
  w_cfg=$(find "$WORKSPACE_ROOT" -maxdepth 1 -mindepth 1 \
    -iname "*prettier*" 2>/dev/null | head -n1)

  [ -L "$p_cfg" ] && p_cfg=$(readlink "$p_cfg")
  [ -L "$w_cfg" ] && w_cfg=$(readlink "$w_cfg")

  if [ -f "$p_cfg" ]; then
    cfg="$p_cfg"
  elif [ -f "$w_cfg" ]; then
    cfg="$w_cfg"
  fi

  if [ "${cfg:-}" != "" ]; then
    args=("--config" "$cfg" "--write")
  fi

  run_cmd "$_prettier" "$file" "${args[@]}"
  run_cmd "$_markdownlint_cli2" "$file" "--fix"
}

fmt_sh() {
  run_cmd "$_shfmt" "$1" "-s" "-ci" "-i" "2" "--write"
  run_cmd "$_shellharden" "$1" "--replace"
}

case "$1" in
  *.py) run_cmd "$_docformatter" "$1" "--in-place" ;;
  *.md) fmt_md "$1" ;;
  *.toml) run_cmd "$_taplo" "$1" "format" ;;
  *.yml | *.yaml) run_cmd "$_yamlfmt" "$1" "format" ;;
  *.sh | *.bash | *activate*) fmt_sh "$1" ;;
  *) exit 0 ;;
esac
