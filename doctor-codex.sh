#!/usr/bin/env bash
set -euo pipefail

codex_home="${CODEX_HOME:-$HOME/.codex}"
agents_home="$HOME/.agents"

fail=0

check_file() {
  local path="$1"
  if [[ -f "$path" ]]; then
    printf 'ok file  %s\n' "$path"
  else
    printf 'missing  %s\n' "$path"
    fail=1
  fi
}

check_dir() {
  local path="$1"
  if [[ -d "$path" ]]; then
    printf 'ok dir   %s\n' "$path"
  else
    printf 'missing  %s\n' "$path"
    fail=1
  fi
}

check_file "$codex_home/AGENTS.md"
check_file "$codex_home/config.toml"
check_dir "$codex_home/harness/standards"
check_dir "$codex_home/agents"
check_dir "$agents_home/skills"
check_file "$agents_home/skills/spec/SKILL.md"
check_file "$agents_home/skills/workflow-sdd/SKILL.md"
check_file "$agents_home/skills/architecture-decision/SKILL.md"
check_file "$agents_home/skills/adversarial-review/SKILL.md"
check_file "$agents_home/skills/reconcile/SKILL.md"
check_file "$agents_home/skills/ship-check/SKILL.md"
check_file "$codex_home/harness/standards/INDEX.md"
check_file "$codex_home/harness/standards/ai-workflow-standards.md"

python3 - <<'PY' "$codex_home/config.toml"
import pathlib
import sys
import tomllib

path = pathlib.Path(sys.argv[1])
try:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
except Exception as exc:
    print(f"invalid config.toml: {exc}")
    sys.exit(1)

required = [
    ("model", "gpt-5.5"),
    ("model_reasoning_effort", "high"),
    ("plan_mode_reasoning_effort", "xhigh"),
    ("approval_policy", "on-request"),
    ("sandbox_mode", "workspace-write"),
    ("web_search", "cached"),
]
for key, value in required:
    if data.get(key) != value:
        print(f"unexpected {key}: {data.get(key)!r}")
        sys.exit(1)

features = data.get("features", {})
if features.get("goals") is not True:
    print("missing features.goals = true")
    sys.exit(1)
if features.get("memories") is not False:
    print("unexpected features.memories")
    sys.exit(1)

if "agentMemory" not in data.get("mcp_servers", {}):
    print("missing mcp_servers.agentMemory")
    sys.exit(1)

print("ok toml  config parses and managed keys are present")
PY

python3 - <<'PY' "$codex_home/agents"
import pathlib
import sys
import tomllib

agents_dir = pathlib.Path(sys.argv[1])
expected = {
    "build-coordinator": ("gpt-5.5", "high"),
    "backend-builder": ("gpt-5.5", "medium"),
    "frontend-builder": ("gpt-5.5", "medium"),
    "database-builder": ("gpt-5.5", "medium"),
    "devops-builder": ("gpt-5.5", "medium"),
    "code-reviewer": ("gpt-5.5", "high"),
    "architecture-reviewer": ("gpt-5.5", "high"),
    "security-reviewer": ("gpt-5.5", "high"),
    "reconciler": ("gpt-5.5", "high"),
    "verifier": ("gpt-5.5", "high"),
    "explorer": ("gpt-5.4-mini", "low"),
    "documentation-writer": ("gpt-5.4-mini", "low"),
    "memory-retriever": ("gpt-5.4-mini", "low"),
}

found = {}
for path in agents_dir.glob("*.toml"):
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    name = data.get("name")
    if not name:
        print(f"agent missing name: {path}")
        sys.exit(1)
    found[name] = (data.get("model"), data.get("model_reasoning_effort"))

missing = sorted(set(expected) - set(found))
extra = sorted(set(found) - set(expected))
if missing or extra:
    print(f"unexpected agents missing={missing} extra={extra}")
    sys.exit(1)

for name, pair in expected.items():
    if found[name] != pair:
        print(f"unexpected {name}: {found[name]!r}, expected {pair!r}")
        sys.exit(1)

print("ok toml  agent matrix matches expected models and efforts")
PY

python3 - <<'PY' "$codex_home/AGENTS.md" "$codex_home/harness/standards"
import pathlib
import sys

agents_md = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
standards_dir = pathlib.Path(sys.argv[2])
required = {
    "engineering-principles.md",
    "software-design-fundamentals.md",
    "patterns-catalog.md",
    "repository-organization-standards.md",
    "technology-decision-playbook.md",
    "technical-research-standards.md",
    "architecture-decision-standards.md",
    "development-methodologies.md",
    "testing-standards.md",
    "security-engineering-standards.md",
    "backend-architecture-standards.md",
    "api-contract-standards.md",
    "database-architecture-standards.md",
    "frontend-architecture-standards.md",
    "distributed-systems-standards.md",
    "operability-standards.md",
    "ai-workflow-standards.md",
}
found = {p.name for p in standards_dir.glob("*.md") if p.name != "INDEX.md"}
if found != required:
    print(f"unexpected standards set missing={sorted(required - found)} extra={sorted(found - required)}")
    sys.exit(1)
for stale in ("opencode", "Orc Plan", "Del Build"):
    if stale in agents_md:
        print(f"stale term in AGENTS.md: {stale}")
        sys.exit(1)
print("ok docs  AGENTS.md and standards inventory validated")
PY

if command -v codex >/dev/null 2>&1; then
  codex features list >/tmp/codex-ecosystem-features.txt || fail=1
  printf 'ok cmd   codex features list\n'
else
  printf 'missing  codex command not found\n'
  fail=1
fi

exit "$fail"
