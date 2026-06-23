#!/usr/bin/env python3
from __future__ import annotations

import argparse
import pathlib
import re
import sys
import tomllib


TOP_LEVEL = {
    "model": '"gpt-5.5"',
    "model_reasoning_effort": '"high"',
    "plan_mode_reasoning_effort": '"xhigh"',
    "approval_policy": '"on-request"',
    "sandbox_mode": '"workspace-write"',
    "web_search": '"cached"',
    "project_doc_max_bytes": "65536",
}

SECTION_KEYS = {
    "features": {
        "goals": "true",
        "memories": "false",
    },
    "agents": {
        "max_threads": "6",
        "max_depth": "1",
        "job_max_runtime_seconds": "1800",
    },
}

AGENT_MEMORY_SECTION = [
    "[mcp_servers.agentMemory]",
    'command = "/home/phreak/.agent-memory/bin/agent-memory"',
    'args = ["mcp"]',
    "startup_timeout_sec = 5",
    "tool_timeout_sec = 10",
    "enabled = true",
    "required = false",
    'default_tools_approval_mode = "prompt"',
    'enabled_tools = ["search_memory", "session_context"]',
]


SECTION_RE = re.compile(r"^\s*\[([^\]]+)\]\s*(?:#.*)?$")
KEY_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*=")


def section_name(line: str) -> str | None:
    match = SECTION_RE.match(line)
    return match.group(1).strip() if match else None


def key_name(line: str) -> str | None:
    match = KEY_RE.match(line)
    return match.group(1).strip() if match else None


def remove_managed(lines: list[str]) -> list[str]:
    result: list[str] = []
    current_section = ""
    skip_section = False

    for line in lines:
        found_section = section_name(line)
        if found_section is not None:
            current_section = found_section
            skip_section = current_section == "mcp_servers.agentMemory"
            if skip_section:
                continue

        if skip_section:
            continue

        key = key_name(line)
        if key:
            if current_section == "" and key in TOP_LEVEL:
                continue
            if current_section in SECTION_KEYS and key in SECTION_KEYS[current_section]:
                continue

        result.append(line.rstrip("\n"))

    return trim_excess_blank_lines(result)


def trim_excess_blank_lines(lines: list[str]) -> list[str]:
    trimmed: list[str] = []
    blank = 0
    for line in lines:
        if line.strip():
            blank = 0
            trimmed.append(line)
        else:
            blank += 1
            if blank <= 2:
                trimmed.append("")
    while trimmed and not trimmed[-1].strip():
        trimmed.pop()
    return trimmed


def insert_top_level(lines: list[str]) -> list[str]:
    insert_at = 0
    while insert_at < len(lines):
        stripped = lines[insert_at].strip()
        if stripped.startswith("["):
            break
        insert_at += 1

    block = [f"{key} = {value}" for key, value in TOP_LEVEL.items()]
    if insert_at > 0 and lines[insert_at - 1].strip():
        block.append("")
    return lines[:insert_at] + block + lines[insert_at:]


def find_section(lines: list[str], name: str) -> tuple[int, int] | None:
    start = None
    for i, line in enumerate(lines):
        found = section_name(line)
        if found == name:
            start = i
            continue
        if start is not None and found is not None:
            return start, i
    if start is not None:
        return start, len(lines)
    return None


def upsert_section_keys(lines: list[str], name: str, keys: dict[str, str]) -> list[str]:
    block = [f"{key} = {value}" for key, value in keys.items()]
    span = find_section(lines, name)
    if span is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append(f"[{name}]")
        lines.extend(block)
        return lines

    _, end = span
    if end > 0 and lines[end - 1].strip():
        block = [""] + block
    return lines[:end] + block + lines[end:]


def append_agent_memory(lines: list[str]) -> list[str]:
    if lines and lines[-1].strip():
        lines.append("")
    lines.extend(AGENT_MEMORY_SECTION)
    return lines


def merge(path: pathlib.Path) -> None:
    original = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    lines = remove_managed(original)
    lines = insert_top_level(lines)
    for section, keys in SECTION_KEYS.items():
        lines = upsert_section_keys(lines, section, keys)
    lines = append_agent_memory(lines)
    text = "\n".join(trim_excess_blank_lines(lines)) + "\n"

    try:
        tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        print(f"Refusing to write invalid TOML: {exc}", file=sys.stderr)
        sys.exit(1)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=pathlib.Path)
    args = parser.parse_args()
    merge(args.config.expanduser())


if __name__ == "__main__":
    main()
