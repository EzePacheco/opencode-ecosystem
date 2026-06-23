#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: ./install-codex.sh [--force]

Installs the Codex-native ecosystem:
  - codex/AGENTS.md -> ~/.codex/AGENTS.md
  - codex/harness -> ~/.codex/harness
  - codex/agents -> ~/.codex/agents
  - codex/skills -> ~/.agents/skills
  - managed config keys -> ~/.codex/config.toml

Existing managed items are backed up unless --force is set.
USAGE
}

force=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --force)
      force=true
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      usage
      exit 1
      ;;
  esac
done

source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
codex_home="${CODEX_HOME:-$HOME/.codex}"
agents_home="$HOME/.agents"
timestamp="$(date +%Y%m%d-%H%M%S)-$$"
backup_root="$codex_home/.codex-ecosystem-backup/$timestamp"

backup_or_replace() {
  local target="$1"
  if [[ -e "$target" || -L "$target" ]]; then
    if [[ "$force" == true ]]; then
      rm -rf -- "$target"
    else
      local backup="$backup_root/${target#$HOME/}"
      mkdir -p -- "$(dirname -- "$backup")"
      mv -- "$target" "$backup"
      printf 'Backed up %s -> %s\n' "$target" "$backup"
    fi
  fi
}

install_dir() {
  local from="$1"
  local to="$2"
  if [[ ! -d "$from" ]]; then
    printf 'Missing source directory: %s\n' "$from" >&2
    exit 1
  fi
  mkdir -p -- "$(dirname -- "$to")"
  backup_or_replace "$to"
  cp -a -- "$from" "$to"
}

install_file() {
  local from="$1"
  local to="$2"
  if [[ ! -f "$from" ]]; then
    printf 'Missing source file: %s\n' "$from" >&2
    exit 1
  fi
  mkdir -p -- "$(dirname -- "$to")"
  backup_or_replace "$to"
  cp -a -- "$from" "$to"
}

mkdir -p -- "$codex_home" "$agents_home/skills"

install_file "$source_dir/codex/AGENTS.md" "$codex_home/AGENTS.md"
install_dir "$source_dir/codex/harness" "$codex_home/harness"
install_dir "$source_dir/codex/agents" "$codex_home/agents"

for skill in "$source_dir"/codex/skills/*; do
  [[ -d "$skill" ]] || continue
  install_dir "$skill" "$agents_home/skills/$(basename -- "$skill")"
done

python3 "$source_dir/codex/scripts/merge_codex_config.py" "$codex_home/config.toml"

printf 'Installed Codex ecosystem.\n'
printf 'Codex home: %s\n' "$codex_home"
printf 'Skills home: %s\n' "$agents_home/skills"
printf 'Restart Codex to load AGENTS.md, skills, custom agents, and MCP config.\n'
