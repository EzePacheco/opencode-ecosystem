#!/usr/bin/env python3
"""Bounded, read-only discovery of Git checkouts in a non-Git workspace."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


class DiscoveryFailure(Exception):
    pass


def git(path: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), *args], text=True, capture_output=True,
            timeout=3, check=False, env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def checkout(path: Path, workspace: Path) -> dict | None:
    root_text = git(path, "rev-parse", "--show-toplevel")
    if root_text is None:
        return None
    root = Path(root_text).resolve()
    git_dir_text = git(root, "rev-parse", "--absolute-git-dir")
    common_text = git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if not git_dir_text or not common_text:
        return None
    git_dir = Path(git_dir_text).resolve()
    common_dir = Path(common_text).resolve()
    branch = git(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    head = git(root, "rev-parse", "--verify", "HEAD")
    shallow_text = git(root, "rev-parse", "--is-shallow-repository")
    marker = root / ".git"
    try:
        marker_is_file = marker.is_file()
    except OSError:
        marker_is_file = False
    try:
        relative = str(root.relative_to(workspace))
    except ValueError:
        relative = "."
    dirty_status = git(root, "status", "--porcelain", "--untracked-files=normal")
    return {
        "path": str(root),
        "relative_path": relative,
        "git_root": str(root),
        "branch": branch,
        "head": head,
        "dirty": None if dirty_status is None else dirty_status != "",
        "shallow": shallow_text == "true",
        "is_worktree": marker_is_file or git_dir != common_dir,
        "git_common_dir": str(common_dir),
        "repository_id": str(common_dir),
    }


def discover(workspace: Path, max_depth: int, max_directories: int) -> dict:
    if not workspace.exists() or not workspace.is_dir():
        raise DiscoveryFailure(f"workspace path is not an accessible directory: {workspace}")
    workspace = workspace.resolve()
    warnings: list[str] = []
    errors: list[str] = []
    limits = {"max_depth": max_depth, "max_directories": max_directories, "directories_inspected": 0,
              "depth_limit_reached": False, "directory_limit_reached": False}
    found: dict[str, dict] = {}
    root_checkout = checkout(workspace, workspace)
    is_git_repository = root_checkout is not None
    if root_checkout:
        found[str(Path(root_checkout["git_root"]))] = root_checkout
    else:
        stack: list[tuple[Path, int]] = [(workspace, 0)]
        while stack:
            if limits["directories_inspected"] >= max_directories:
                limits["directory_limit_reached"] = True
                break
            directory, depth = stack.pop()
            limits["directories_inspected"] += 1
            if depth >= max_depth:
                try:
                    has_child_dirs = any(
                        entry.is_dir(follow_symlinks=False)
                        for entry in os.scandir(directory)
                        if not entry.is_symlink()
                    )
                except OSError as exc:
                    warnings.append(f"directory unreadable: {directory.relative_to(workspace) or '.'}")
                    continue
                if has_child_dirs:
                    limits["depth_limit_reached"] = True
                continue
            try:
                entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
            except OSError:
                warnings.append(f"directory unreadable: {directory.relative_to(workspace) or '.'}")
                continue
            for entry in entries:
                if entry.is_symlink():
                    continue
                try:
                    if not entry.is_dir(follow_symlinks=False):
                        continue
                except OSError:
                    continue
                child = Path(entry.path)
                marker = child / ".git"
                if marker.exists() and not marker.is_symlink():
                    item = checkout(child, workspace)
                    if item:
                        found[item["git_root"]] = item
                    continue
                stack.append((child, depth + 1))

    groups: dict[str, list[dict]] = {}
    for item in found.values():
        groups.setdefault(item["repository_id"], []).append(item)
    repositories = []
    for repository_id in sorted(groups):
        checkouts = sorted(groups[repository_id], key=lambda item: item["git_root"])
        repositories.append({"repository_id": repository_id, "git_common_dir": repository_id, "checkouts": checkouts})
    return {
        "workspace": str(workspace),
        "is_git_repository": is_git_repository,
        "repositories": repositories,
        "limits": limits,
        "warnings": sorted(set(warnings)),
        "errors": errors,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Bounded, read-only Git checkout discovery")
    result.add_argument("path", nargs="?", default=".", help="workspace directory; default: cwd")
    result.add_argument("--max-depth", type=int, default=2, help="directory levels below workspace (default: 2)")
    result.add_argument("--max-directories", type=int, default=1000, help="maximum non-Git directories inspected (default: 1000)")
    result.add_argument("--json", action="store_true", help="emit JSON only on stdout")
    result.add_argument("--pretty", action="store_true", help="indent JSON (valid with --json)")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.pretty and not args.json:
        print("--pretty is valid only with --json", file=sys.stderr)
        return 3
    if args.max_depth < 0 or args.max_directories < 1:
        print("--max-depth must be non-negative and --max-directories positive", file=sys.stderr)
        return 3
    try:
        data = discover(Path(args.path).expanduser().absolute(), args.max_depth, args.max_directories)
    except DiscoveryFailure as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2 if args.pretty else None))
    else:
        print(f"Workspace: {data['workspace']} (Git repository: {data['is_git_repository']})")
        for repository in data["repositories"]:
            print(f"Repository {repository['repository_id']}: {len(repository['checkouts'])} checkout(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
