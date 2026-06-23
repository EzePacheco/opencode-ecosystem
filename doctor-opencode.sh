#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: ./doctor-opencode.sh [target-dir]

Validates that the repo-managed native OpenCode install surfaces in target-dir
still match this repo source. This is not a general validator for arbitrary
custom localizations outside the managed surface set.
Defaults to ${XDG_CONFIG_HOME:-$HOME/.config}/opencode when target-dir is omitted.
USAGE
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  printf 'missing dependency: python3 is required for doctor-opencode.sh\n' >&2
  exit 1
fi

target="${1:-${XDG_CONFIG_HOME:-$HOME/.config}/opencode}"
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
target="$(python3 - <<'PY' "$target"
import pathlib
import sys
print(pathlib.Path(sys.argv[1]).expanduser().resolve())
PY
)"

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

check_file "$target/opencode.jsonc"
check_file "$target/AGENTS.md"
check_file "$target/GLOBAL.md"
check_dir "$target/agents"
check_dir "$target/skills"
check_dir "$target/standards"

for skill in \
  workflow-sdd \
  spec \
  architecture-decision \
  adversarial-review \
  reconcile \
  ship-check
do
  check_file "$target/skills/$skill/SKILL.md"
done

for agent in \
  mentor \
  plan \
  build \
  backend-builder \
  frontend-builder \
  database-builder \
  devops-builder \
  qa-builder \
  tech-lead \
  code-reviewer \
  architecture-reviewer \
  security-reviewer \
  reconciler \
  verifier \
  explore \
  explore-mini \
  worktree-manager \
  documentation-writer \
  memory-retriever
do
  check_file "$target/agents/$agent.md"
done

if [[ "$fail" -ne 0 ]]; then
  exit "$fail"
fi

python3 - <<'PY' "$target/opencode.jsonc"
import json
import pathlib
import re
import sys

def strip_jsonc(text: str) -> str:
    out = []
    i = 0
    in_string = False
    escape = False

    while i < len(text):
        ch = text[i]

        if in_string:
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            i += 1
            continue

        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue

        if ch == "/" and i + 1 < len(text):
            nxt = text[i + 1]
            if nxt == "/":
                i += 2
                while i < len(text) and text[i] not in "\r\n":
                    i += 1
                continue
            if nxt == "*":
                i += 2
                while i + 1 < len(text) and not (text[i] == "*" and text[i + 1] == "/"):
                    i += 1
                i += 2
                continue

        out.append(ch)
        i += 1

    text = "".join(out)
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return text

path = pathlib.Path(sys.argv[1])
try:
    data = json.loads(strip_jsonc(path.read_text(encoding="utf-8")))
except Exception as exc:
    print(f"invalid opencode.jsonc: {exc}")
    sys.exit(1)

required = {
    "$schema": "https://opencode.ai/config.json",
    "model": "openai/gpt-5.5",
    "small_model": "openai/gpt-5.4-mini",
    "default_agent": "plan",
}

for key, value in required.items():
    if data.get(key) != value:
        print(f"unexpected {key}: {data.get(key)!r}")
        sys.exit(1)

mcp = data.get("mcp", {}).get("agent-memory", {})
if mcp.get("enabled") is not False:
    print("unexpected mcp.agent-memory.enabled")
    sys.exit(1)

if data.get("permission", {}).get("agent-memory_*") != "deny":
    print("missing permission agent-memory_* = deny")
    sys.exit(1)

standards = data.get("references", {}).get("standards", {})
if standards.get("path") != "./standards":
    print(f"unexpected standards reference path: {standards.get('path')!r}")
    sys.exit(1)

for forbidden in ("approval_policy", "plan_mode_reasoning_effort", "web_search", "sandbox_mode"):
    if forbidden in data:
        print(f"unexpected Codex-only config key: {forbidden}")
        sys.exit(1)

print("ok json  opencode config validated")
PY

python3 - <<'PY' "$target/AGENTS.md" "$target/GLOBAL.md" "$script_dir/GLOBAL.md"
import pathlib
import sys

for path_str in sys.argv[1:3]:
    path = pathlib.Path(path_str)
    text = path.read_text(encoding="utf-8")
    for forbidden in ("doctor-codex", "~/.codex", "codex/AGENTS.md", "install-codex.sh"):
        if forbidden in text:
            print(f"forbidden Codex runtime reference in {path}: {forbidden}")
            sys.exit(1)

if pathlib.Path(sys.argv[1]).read_text(encoding="utf-8") != pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"):
    print("AGENTS.md and GLOBAL.md differ in installed target")
    sys.exit(1)

if pathlib.Path(sys.argv[2]).read_text(encoding="utf-8") != pathlib.Path(sys.argv[3]).read_text(encoding="utf-8"):
    print("installed GLOBAL.md differs from repo source GLOBAL.md")
    sys.exit(1)

print("ok docs  runtime instruction files validated")
PY

python3 - <<'PY' "$target/agents"
import pathlib
import re
import sys

agents_dir = pathlib.Path(sys.argv[1])
expected = {
    "mentor": ("openai/gpt-5.5", "high", "high"),
    "plan": ("openai/gpt-5.5", "xhigh", "high"),
    "build": ("openai/gpt-5.5", "high", "high"),
    "backend-builder": ("openai/gpt-5.5", "medium", "medium"),
    "frontend-builder": ("openai/gpt-5.5", "medium", "medium"),
    "database-builder": ("openai/gpt-5.5", "medium", "medium"),
    "devops-builder": ("openai/gpt-5.5", "medium", "medium"),
    "qa-builder": ("openai/gpt-5.5", "high", "high"),
    "tech-lead": ("openai/gpt-5.5", "xhigh", "high"),
    "code-reviewer": ("openai/gpt-5.5", "xhigh", "high"),
    "architecture-reviewer": ("openai/gpt-5.5", "high", "high"),
    "security-reviewer": ("openai/gpt-5.5", "high", "high"),
    "reconciler": ("openai/gpt-5.5", "high", "high"),
    "verifier": ("openai/gpt-5.5", "high", "high"),
    "explore": ("openai/gpt-5.4-mini", "medium", "medium"),
    "explore-mini": ("openai/gpt-5.4-mini", "medium", "medium"),
    "worktree-manager": ("openai/gpt-5.4-mini", "medium", "medium"),
    "documentation-writer": ("openai/gpt-5.4", "medium", "medium"),
    "memory-retriever": ("openai/gpt-5.4-mini", "medium", "medium"),
}

model_re = re.compile(r"^model:\s*(.+)$", re.M)
variant_re = re.compile(r"^variant:\s*(.+)$", re.M)
reasoning_effort_re = re.compile(r"^reasoningEffort:\s*(.+)$", re.M)

for name, pair in expected.items():
    path = agents_dir / f"{name}.md"
    text = path.read_text(encoding="utf-8")
    model = model_re.search(text)
    variant = variant_re.search(text)
    reasoning_effort = reasoning_effort_re.search(text)
    actual = (
        model.group(1).strip() if model else None,
        variant.group(1).strip() if variant else None,
        reasoning_effort.group(1).strip() if reasoning_effort else None,
    )
    if variant and not reasoning_effort:
        print(f"{name} has variant without corresponding reasoningEffort")
        sys.exit(1)
    if actual != pair:
        print(f"unexpected {name}: {actual!r}, expected {pair!r}")
        sys.exit(1)

plan_text = (agents_dir / "plan.md").read_text(encoding="utf-8")
if 'edit: allow' in plan_text:
    print("plan agent must not have broad edit allow")
    sys.exit(1)

front_matter = re.match(r"^---\n(.*?)\n---(?:\n|$)", plan_text, re.S)
if not front_matter:
    print("plan agent missing front matter")
    sys.exit(1)

front_lines = front_matter.group(1).splitlines()

def nested_block(lines, header, child_prefix):
    try:
        start = lines.index(header)
    except ValueError:
        return None

    block = []
    for line in lines[start + 1:]:
        if not line.startswith(child_prefix):
            break
        block.append(line)
    return block

permission_block = nested_block(front_lines, "permission:", "  ")
if permission_block is None:
    print("plan agent missing permission block")
    sys.exit(1)

edit_block = nested_block(permission_block, "  edit:", "    ")
expected_edit_block = [
    '    "*": deny',
    '    ".opencode/specs/*.spec.md": allow',
    '    ".opencode/specs/**/*.spec.md": allow',
    '    ".codex/specs/*.spec.md": allow',
    '    ".codex/specs/**/*.spec.md": allow',
    '    ".claude/specs/*.spec.md": allow',
    '    ".claude/specs/**/*.spec.md": allow',
    '    "docs/specs/*.spec.md": allow',
    '    "docs/specs/**/*.spec.md": allow',
    '    "*.spec.md": allow',
    '    "**/*.spec.md": allow',
]
if edit_block != expected_edit_block:
    print("plan agent edit permissions differ from expected spec-only block")
    sys.exit(1)

if "  bash: deny" not in permission_block:
    print("plan agent missing bash deny in permission block")
    sys.exit(1)

for required in (
    'task:',
    'explore: allow',
    'explore-mini: allow',
    'architecture-reviewer: allow',
    'security-reviewer: allow',
):
    if required not in plan_text:
        print(f"plan agent missing spec-only safeguard: {required}")
        sys.exit(1)

for forbidden in (
    '    code-reviewer: allow',
    '    memory-retriever: allow',
):
    if forbidden in permission_block:
        print(f"plan agent has forbidden delegation permission: {forbidden.strip()}")
        sys.exit(1)

for required in (
    'max_rework_iterations: 3',
    'allowed_test_paths',
    'verification_commands',
    '`agents`, `workflow runtime`, `worktree orchestration`, `public contracts`,',
    '`permissions`, `MCP`, `agent-memory`, `auth`, `secrets`, `privacy`,',
    'require both reviewers.',
):
    if required not in plan_text:
        print(f"plan agent missing V3 risk or QA contract: {required}")
        sys.exit(1)

mentor_text = (agents_dir / "mentor.md").read_text(encoding="utf-8")
for required in (
    'architecture-reviewer: allow',
    'security-reviewer: allow',
):
    if required not in mentor_text:
        print(f"mentor agent missing reviewer delegation permission: {required}")
        sys.exit(1)

for reviewer in ("architecture-reviewer", "security-reviewer"):
    text = (agents_dir / f"{reviewer}.md").read_text(encoding="utf-8")
    for required in (
        '"git status --short": allow',
        '"git diff": allow',
        '"git diff --stat": allow',
        '"git log --oneline -10": allow',
        '"git show --stat": allow',
    ):
        if required not in text:
            print(f"{reviewer} missing git inspection permission: {required}")
            sys.exit(1)

worktree_text = (agents_dir / "worktree-manager.md").read_text(encoding="utf-8")
for required in (
    '"git worktree list": allow',
    '"git worktree add": allow',
    '"git status --short": allow',
    'Do not run `git commit`, `git merge`, `git push`, `git reset`, `git rebase`,',
    'leave removal to the human instead of running it yourself.',
):
    if required not in worktree_text:
        print(f"worktree-manager missing safety requirement: {required}")
        sys.exit(1)

for forbidden in (
    '"git worktree remove": allow',
):
    if forbidden in worktree_text:
        print(f"worktree-manager has forbidden destructive permission: {forbidden}")
        sys.exit(1)

qa_text = (agents_dir / "qa-builder.md").read_text(encoding="utf-8")
for required in (
    'Prefer Playwright for E2E coverage only when the project already supports it',
    'files_changed;',
    'tests_added;',
    'commands_run;',
    'failures;',
    'residual_risk.',
):
    if required not in qa_text:
        print(f"qa-builder missing contract requirement: {required}")
        sys.exit(1)

build_text = (agents_dir / "build.md").read_text(encoding="utf-8")
for required in (
    'QA handoff fields required when `needs_qa=true`:',
    '`spec`',
    '`reference_files`',
    '`allowed_test_paths`',
    '`verification_commands`',
    'Capture the returned `worktrees_touched` paths and assign at most one',
    'Cleanup is report-only:',
    '`agents`, `workflow runtime`, `worktree orchestration`, `public contracts`,',
    '`permissions`, `MCP`, `agent-memory`, `auth`, `secrets`, `privacy`,',
    'Count each `reconciler -> verifier` retry as one rework iteration.',
):
    if required not in build_text:
        print(f"build agent missing V3 contract requirement: {required}")
        sys.exit(1)

for path in ("code-reviewer", "architecture-reviewer", "security-reviewer"):
    text = (agents_dir / f"{path}.md").read_text(encoding="utf-8")
    for required in (
        '"verdict": "accepted | rework-required"',
        '"findings": [',
        '"open_questions": [],',
        '"verification_gaps": []',
    ):
        if required not in text:
            print(f"{path} missing common findings schema key: {required}")
            sys.exit(1)

for path, forbidden in (
    ("architecture-reviewer", '"alternatives": []'),
    ("security-reviewer", '"residual_risk": []'),
):
    text = (agents_dir / path).with_suffix('.md').read_text(encoding="utf-8")
    if forbidden in text:
        print(f"{path} still documents schema extension key: {forbidden}")
        sys.exit(1)

memory_text = (agents_dir / "memory-retriever.md").read_text(encoding="utf-8")
for required in (
    '"agent-memory_*": deny',
    'remains disabled and denied pending separate approval',
    'Do not invoke `agent-memory` or any other persistent-memory MCP.',
):
    if required not in memory_text:
        print(f"memory-retriever missing native memory safeguard: {required}")
        sys.exit(1)

print("ok docs  agent matrix and plan permissions validated")
PY

python3 - <<'PY' "$script_dir" "$target"
import pathlib
import sys

repo = pathlib.Path(sys.argv[1])
target = pathlib.Path(sys.argv[2])

checks = [
    (repo / "opencode.jsonc", target / "opencode.jsonc"),
    (repo / "GLOBAL.md", target / "GLOBAL.md"),
    (repo / "GLOBAL.md", target / "AGENTS.md"),
]

for rel in [
    "standards/INDEX.md",
    "standards/engineering-principles.md",
    "standards/software-design-fundamentals.md",
    "standards/patterns-catalog.md",
    "standards/repository-organization-standards.md",
    "standards/technology-decision-playbook.md",
    "standards/technical-research-standards.md",
    "standards/architecture-decision-standards.md",
    "standards/development-methodologies.md",
    "standards/testing-standards.md",
    "standards/security-engineering-standards.md",
    "standards/backend-architecture-standards.md",
    "standards/api-contract-standards.md",
    "standards/database-architecture-standards.md",
    "standards/frontend-architecture-standards.md",
    "standards/distributed-systems-standards.md",
    "standards/operability-standards.md",
    "standards/ai-workflow-standards.md",
    "agents/mentor.md",
    "agents/plan.md",
    "agents/build.md",
    "agents/backend-builder.md",
    "agents/frontend-builder.md",
    "agents/database-builder.md",
    "agents/devops-builder.md",
    "agents/qa-builder.md",
    "agents/tech-lead.md",
    "agents/code-reviewer.md",
    "agents/architecture-reviewer.md",
    "agents/security-reviewer.md",
    "agents/reconciler.md",
    "agents/verifier.md",
    "agents/explore.md",
    "agents/explore-mini.md",
    "agents/worktree-manager.md",
    "agents/documentation-writer.md",
    "agents/memory-retriever.md",
    "skills/workflow-sdd/SKILL.md",
    "skills/spec/SKILL.md",
    "skills/architecture-decision/SKILL.md",
    "skills/adversarial-review/SKILL.md",
    "skills/reconcile/SKILL.md",
    "skills/ship-check/SKILL.md",
]:
    checks.append((repo / rel, target / rel))

for src, dst in checks:
    if src.read_text(encoding="utf-8") != dst.read_text(encoding="utf-8"):
        print(f"installed file differs from repo source: {dst}")
        sys.exit(1)

print("ok docs  installed files match repo source for managed root surfaces and standards")
PY

exit "$fail"
