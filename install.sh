#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: ./install.sh [--force] [<target-dir>]

Installs the portable opencode setup into <target-dir>.

Defaults:
  - target-dir defaults to ${XDG_CONFIG_HOME:-$HOME/.config}/opencode
  - existing managed items are backed up before overwrite unless --force is set

Examples:
  ./install.sh                  # install to default config dir
  ./install.sh /tmp/opencode-config  # install to a custom path
  ./install.sh --force ~/.config/opencode  # overwrite without backup
USAGE
}

make_absolute() {
  case "$1" in
    /*) printf '%s\n' "$1" ;;
    *) printf '%s\n' "$PWD/$1" ;;
  esac
}

strip_trailing_slashes() {
  local path="$1"
  while [[ "$path" != "/" && "$path" == */ ]]; do
    path="${path%/}"
  done
  printf '%s\n' "$path"
}

canonicalize_path() {
  local path probe suffix leaf parent resolved
  path="$(strip_trailing_slashes "$(make_absolute "$1")")"

  if [[ -e "$path" ]]; then
    if [[ -d "$path" ]]; then
      cd -P -- "$path" && pwd -P
    else
      parent="$(dirname -- "$path")"
      leaf="$(basename -- "$path")"
      resolved="$(cd -P -- "$parent" && pwd -P)"
      if [[ "$resolved" == "/" ]]; then
        printf '/%s\n' "$leaf"
      else
        printf '%s/%s\n' "$resolved" "$leaf"
      fi
    fi
    return
  fi

  probe="$path"
  suffix=""
  while [[ ! -e "$probe" ]]; do
    leaf="$(basename -- "$probe")"
    suffix="/$leaf$suffix"
    parent="$(dirname -- "$probe")"
    if [[ "$parent" == "$probe" ]]; then
      printf 'Cannot resolve path ancestor: %s\n' "$path" >&2
      return 1
    fi
    probe="$parent"
  done

  if [[ ! -d "$probe" ]]; then
    printf 'Nearest existing target ancestor is not a directory: %s\n' "$probe" >&2
    return 1
  fi

  resolved="$(cd -P -- "$probe" && pwd -P)"
  if [[ "$resolved" == "/" ]]; then
    printf '%s\n' "$suffix"
  else
    printf '%s%s\n' "$resolved" "$suffix"
  fi
}

is_same_or_child() {
  local candidate="$1"
  local parent="$2"
  [[ "$candidate" == "$parent" || "$candidate" == "$parent/"* ]]
}

assert_no_source_target_overlap() {
  local candidate="$1"
  if is_same_or_child "$candidate" "$source_dir"; then
    printf 'Refusing to install into source tree: %s\n' "$candidate" >&2
    exit 1
  fi
  if is_same_or_child "$source_dir" "$candidate"; then
    printf 'Refusing to install into a target that contains the source tree: %s\n' "$candidate" >&2
    exit 1
  fi
}

assert_destination_safe() {
  local destination="$1"
  local destination_canon
  destination_canon="$(canonicalize_path "$destination")"

  if ! is_same_or_child "$destination_canon" "$target"; then
    printf 'Refusing destination outside target: %s\n' "$destination_canon" >&2
    exit 1
  fi

  assert_no_source_target_overlap "$destination_canon"
}

force=false
target=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --force)
      force=true
      shift
      ;;
    --)
      shift
      break
      ;;
    --*)
      printf 'Unknown option: %s\n' "$1" >&2
      usage
      exit 1
      ;;
    *)
      if [[ -z "$target" ]]; then
        target="$1"
      else
        printf 'Unexpected extra argument: %s\n' "$1" >&2
        usage
        exit 1
      fi
      shift
      ;;
  esac
done

if [[ $# -gt 0 ]]; then
  if [[ -z "$target" ]]; then
    target="$1"
    shift
  fi
  if [[ $# -gt 0 ]]; then
    printf 'Unexpected extra argument: %s\n' "$1" >&2
    usage
    exit 1
  fi
fi

if [[ -z "$target" ]]; then
  target="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
fi

source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
target="$(canonicalize_path "$target")"

if [[ "$target" == "/" ]]; then
  printf 'Refusing to install into filesystem root: %s\n' "$target" >&2
  exit 1
fi

assert_no_source_target_overlap "$target"

if [[ -e "$target" && ! -d "$target" ]]; then
  printf 'Target exists but is not a directory: %s\n' "$target" >&2
  exit 1
fi

managed_labels=(
  "opencode.jsonc"
  "AGENTS.md"
  "GLOBAL.md"
  "agents"
  "skills"
  "standards"
)

managed_mappings=(
  "opencode.jsonc:opencode.jsonc"
  "GLOBAL.md:AGENTS.md"
  "GLOBAL.md:GLOBAL.md"
  "agents:agents"
  "skills:skills"
  "standards:standards"
)

for mapping in "${managed_mappings[@]}"; do
  IFS=':' read -r src_name dest_name <<<"$mapping"
  if [[ ! -e "$source_dir/$src_name" ]]; then
    printf 'Missing source item: %s\n' "$source_dir/$src_name" >&2
    exit 1
  fi
done

mkdir -p -- "$target"
target="$(cd -P -- "$target" && pwd -P)"

stale_items=(
  "opencode.json"
  "config.json"
  "commands"
  "plugins"
  "modes"
  "agent"
  "skill"
)

for stale in "${stale_items[@]}"; do
  if [[ -e "$target/$stale" || -L "$target/$stale" ]]; then
    printf 'Warning: existing opencode surface kept untouched and may still be loaded/merged by opencode: %s\n' "$target/$stale"
  fi
done

printf 'Managed items will be replaced in %s: %s\n' "$target" "${managed_labels[*]}"

if [[ "$force" == true ]]; then
  printf 'Overwrite mode: --force active, replacements will not be backed up.\n'
else
  printf 'Safe mode: existing managed items will be moved to a timestamped backup before replacement.\n'
fi

timestamp="$(date +%Y%m%d-%H%M%S)-$$"
backup_root="$target/.opencode-install-backup/$timestamp"

for mapping in "${managed_mappings[@]}"; do
  IFS=':' read -r src_name dest_name <<<"$mapping"
  from="$source_dir/$src_name"
  to="$target/$dest_name"
  assert_destination_safe "$to"

  if [[ -e "$to" || -L "$to" ]]; then
    if [[ "$force" == true ]]; then
      rm -rf -- "$to"
    else
      backup="$backup_root/$dest_name"
      assert_destination_safe "$backup"
      mkdir -p -- "$(dirname -- "$backup")"
      mv -- "$to" "$backup"
      printf 'Backed up %s -> %s\n' "$to" "$backup"
    fi
  fi

  cp -a -- "$from" "$to"
done

printf 'Installed opencode ecosystem to %s\n' "$target"
printf 'Restart opencode to load the new config.\n'
