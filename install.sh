#!/usr/bin/env bash
set -euo pipefail

target="${1:-$HOME/.config/opencode}"
source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

items=(
  "opencode.jsonc"
  "GLOBAL.md"
  "agents"
  "skills"
  "standards"
)

mkdir -p -- "$target"

for item in "${items[@]}"; do
  from="$source_dir/$item"
  to="$target/$item"

  if [[ ! -e "$from" ]]; then
    printf 'Missing source item: %s\n' "$from" >&2
    exit 1
  fi

  rm -rf -- "$to"
  cp -a -- "$from" "$to"
done

printf 'Installed opencode ecosystem to %s\n' "$target"
printf 'Restart opencode to load the new config.\n'
