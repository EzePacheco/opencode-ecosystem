#!/usr/bin/env python3
"""Bounded, read-only mechanical hints for architecture audit hotspot selection.

Inspect a stable authorized checkout: path checks reject existing symlinks and
escapes, but are not a sandbox against concurrent filesystem replacement.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import os
from pathlib import Path, PurePosixPath
import selectors
import subprocess
import sys
import time


SOURCE_EXTENSIONS = {
    ".py": "python", ".js": "javascript", ".jsx": "javascript", ".ts": "typescript",
    ".tsx": "typescript", ".go": "go", ".rs": "rust", ".java": "java",
    ".kt": "kotlin", ".kts": "kotlin", ".cs": "csharp", ".c": "c",
    ".h": "c", ".cpp": "cpp", ".cc": "cpp", ".hpp": "cpp",
    ".rb": "ruby", ".php": "php", ".swift": "swift", ".m": "objc",
    ".scala": "scala", ".ex": "elixir", ".exs": "elixir", ".sh": "shell",
    ".sql": "sql", ".vue": "vue", ".svelte": "svelte", ".dart": "dart",
}
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip",
    ".gz", ".wasm", ".so", ".dll", ".exe", ".bin", ".pyc", ".class",
    ".jar", ".lock", ".sqlite", ".db",
}
IGNORED_DIRS = {
    ".git", "node_modules", "vendor", "vendors", "third_party", "dist", "build",
    "out", "target", "coverage", ".cache", ".next", "__pycache__", ".venv",
    "venv",
}
GENERATED_DIRS = {"generated", "gen", "dist", "build", "out", "target"}
MANIFESTS = {
    "package.json", "pyproject.toml", "go.mod", "cargo.toml", "pom.xml",
    "build.gradle", "build.gradle.kts", "composer.json", "gemfile", "mix.exs",
    "requirements.txt", "tsconfig.json", "setup.py", "settings.gradle",
}
MAX_GIT_OUTPUT_BYTES = 4_000_000


class ScanFailure(Exception):
    pass


class Inventory:
    def __init__(self, root: Path, args: argparse.Namespace):
        self.root = root
        self.args = args
        self.path_scopes = tuple(sorted(set(scope for scope in (args.path_scope or ()) if scope != ".")))
        self.started = time.monotonic()
        self.warnings: list[str] = []
        self.limits = {
            "max_files": args.max_files,
            "max_source_files": args.max_source_files,
            "max_history_commits": args.max_history_commits,
            "max_hotspots": args.max_hotspots,
            "max_context_paths": args.max_context_paths,
            "max_file_bytes": args.max_file_bytes,
            "max_total_bytes": args.max_total_bytes,
            "max_git_output_bytes": MAX_GIT_OUTPUT_BYTES,
            "timeout_seconds": args.timeout_seconds,
            "files_enumerated": 0,
            "source_files_analyzed": 0,
            "bytes_processed": 0,
            "history_commits_inspected": 0,
            "reached": [],
        }

    def remaining(self) -> float:
        return self.args.timeout_seconds - (time.monotonic() - self.started)

    def reached(self, name: str) -> None:
        if name not in self.limits["reached"]:
            self.limits["reached"].append(name)
            self.warnings.append(f"{name} reached; inventory is partial")

    def git(self, *arguments: str, max_bytes: int = MAX_GIT_OUTPUT_BYTES) -> bytes | None:
        if self.remaining() <= 0:
            self.reached("timeout_seconds")
            return None
        try:
            process = subprocess.Popen(
                ["git", "-C", str(self.root), *arguments],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                env={**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_CONFIG_NOSYSTEM": "1"},
            )
        except OSError:
            return None
        assert process.stdout is not None
        output = bytearray()
        deadline = time.monotonic() + self.remaining()
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            while True:
                wait = deadline - time.monotonic()
                if wait <= 0:
                    self.reached("timeout_seconds")
                    process.kill()
                    break
                if not selector.select(wait):
                    self.reached("timeout_seconds")
                    process.kill()
                    break
                chunk = os.read(process.stdout.fileno(), min(65536, max_bytes + 1 - len(output)))
                if not chunk:
                    break
                output.extend(chunk)
                if len(output) > max_bytes:
                    self.reached("git_output_bytes")
                    process.kill()
                    break
        process.stdout.close()
        try:
            process.wait(timeout=max(0.01, min(0.2, self.remaining())))
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            self.reached("timeout_seconds")
        if process.returncode != 0 or len(output) > max_bytes:
            return None
        return bytes(output)

    def file_paths(self) -> list[tuple[str, bool]]:
        tracked = self.git("ls-files", "-z", "--cached")
        others = self.git("ls-files", "-z", "--others", "--exclude-standard")
        if tracked is None or others is None:
            if self.limits["reached"]:
                return []
            raise ScanFailure("cannot enumerate Git files")
        paths = {os.fsdecode(raw): True for raw in tracked.split(b"\0") if raw}
        paths.update({os.fsdecode(raw): False for raw in others.split(b"\0") if raw and os.fsdecode(raw) not in paths})
        if self.path_scopes:
            paths = {
                name: is_tracked
                for name, is_tracked in paths.items()
                if any(name == scope or name.startswith(scope.rstrip("/") + "/") for scope in self.path_scopes)
            }
        ordered = sorted(paths.items())
        if len(ordered) > self.args.max_files:
            self.reached("max_files")
            ordered = ordered[:self.args.max_files]
        self.limits["files_enumerated"] = len(ordered)
        return ordered

    def source_path(self, name: str) -> Path | None:
        relative = PurePosixPath(name)
        if (not name or "\x00" in name or relative.is_absolute()
                or relative.as_posix() != name or name == "." or ".." in relative.parts):
            self.warnings.append("unsafe path skipped")
            return None
        path = self.root
        # Check each component before resolving or following it for target metadata.
        # The selected root is canonicalized by preflight; do not inspect its parents.
        for part in relative.parts:
            path = path / part
            if path.is_symlink():
                self.warnings.append("symlink path skipped")
                return None
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(self.root):
            self.warnings.append("path outside Git root skipped")
            return None
        return resolved

    @staticmethod
    def test_file(path: PurePosixPath) -> bool:
        name = path.name.lower()
        parts = {part.lower() for part in path.parts}
        return (
            bool(parts & {"tests", "test", "__tests__", "spec", "specs"})
            or name.startswith("test_") or name.endswith("_test.py")
            or name.endswith((".test.js", ".test.ts", ".test.tsx", ".spec.js", ".spec.ts", ".spec.tsx"))
            or name.endswith("test.go") or name.endswith("test.java")
        )

    @staticmethod
    def context_kind(path: PurePosixPath) -> str | None:
        name = path.name.lower()
        parts = {part.lower() for part in path.parts}
        if name == "agents.md":
            return "agents"
        if name in MANIFESTS or name.endswith((".csproj", ".sln", ".gradle")):
            return "manifest"
        if "adr" in parts or "adrs" in parts or "decisions" in parts or name.startswith("adr-"):
            return "decision"
        if "architecture" in name or "architecture" in parts or name in {"readme.md", "arch.md"}:
            return "architecture_or_readme"
        return None

    @staticmethod
    def generated(path: PurePosixPath) -> bool:
        name = path.name.lower()
        return bool({part.lower() for part in path.parts} & GENERATED_DIRS) or name.endswith((".min.js", ".min.css", ".generated.ts", ".g.py", ".pb.go"))

    def read_source(self, path: Path, size: int) -> int | None:
        if size > self.args.max_file_bytes:
            self.reached("max_file_bytes")
            return None
        if self.limits["bytes_processed"] + size > self.args.max_total_bytes:
            self.reached("max_total_bytes")
            return None
        try:
            with path.open("rb") as handle:
                data = handle.read(size + 1)
        except OSError:
            self.warnings.append("source file unreadable")
            return None
        if len(data) != size or b"\0" in data:
            return None
        self.limits["bytes_processed"] += size
        return data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)

    def history(self, eligible: set[str]) -> tuple[dict[str, dict], bool]:
        head = self.git("rev-parse", "--verify", "HEAD", max_bytes=256)
        if head is None:
            return {}, False
        history_command = [
            "log", "--no-renames", f"--max-count={self.args.max_history_commits + 1}",
            "--format=@@COMMIT:%aN", "--name-only", "HEAD", "--",
        ]
        history_command.extend(f":(literal){scope}" for scope in self.path_scopes)
        output = self.git(*history_command)
        if output is None:
            self.warnings.append("history unavailable within limits")
            return {}, False
        counts: dict[str, int] = defaultdict(int)
        authors: dict[str, set[str]] = defaultdict(set)
        author = None
        commits = 0
        seen: set[str] = set()
        for line in output.decode("utf-8", "replace").splitlines():
            if line.startswith("@@COMMIT:"):
                commits += 1
                author = line[len("@@COMMIT:"):]
                seen = set()
            elif commits <= self.args.max_history_commits and line in eligible and line not in seen and author is not None:
                counts[line] += 1
                authors[line].add(author)
                seen.add(line)
        self.limits["history_commits_inspected"] = min(commits, self.args.max_history_commits)
        if commits > self.args.max_history_commits:
            self.reached("max_history_commits")
        return {path: {"commits": count, "authors": len(authors[path])} for path, count in counts.items()}, True

    def run(self) -> dict:
        files = self.file_paths()
        source: list[dict] = []
        generated: list[dict] = []
        tests: list[dict] = []
        source_metadata: list[dict] = []
        context: list[dict] = []
        roots: Counter[str] = Counter()
        module_roots: set[str] = set()
        languages: Counter[str] = Counter()
        totals = Counter()
        for name, tracked in files:
            if self.remaining() <= 0:
                self.reached("timeout_seconds")
                break
            relative = PurePosixPath(name)
            try:
                path = self.source_path(name)
                if path is None or not path.is_file():
                    continue
                size = path.stat().st_size
            except (OSError, RuntimeError):
                self.warnings.append("file stat unavailable")
                continue
            totals["tracked" if tracked else "untracked"] += 1
            kind = self.context_kind(relative)
            if kind:
                context.append({"path": name, "kind": kind})
                if kind == "manifest":
                    module_roots.add(str(relative.parent))
            ext = relative.suffix.lower()
            if ext in BINARY_EXTENSIONS or ext not in SOURCE_EXTENSIONS:
                continue
            if any(part.lower() in IGNORED_DIRS for part in relative.parts[:-1]):
                totals["excluded_source_paths"] += 1
                continue
            if len(source) + len(generated) >= self.args.max_source_files:
                self.reached("max_source_files")
                continue
            if self.args.metadata_only:
                item = {"path": name, "tracked": tracked, "bytes": size,
                        "extension": ext, "language": SOURCE_EXTENSIONS[ext],
                        "generated": self.generated(relative), "test": self.test_file(relative)}
                source_metadata.append(item)
            else:
                loc = self.read_source(path, size)
                if loc is None:
                    totals["source_unanalyzed"] += 1
                    continue
                item = {"path": name, "tracked": tracked, "bytes": size, "loc": loc,
                        "extension": ext, "language": SOURCE_EXTENSIONS[ext]}
            self.limits["source_files_analyzed"] += 1
            if self.generated(relative):
                generated.append(item)
                continue
            source.append(item)
            roots[relative.parts[0] if len(relative.parts) > 1 else "."] += 1
            languages[item["language"]] += 1
            if self.test_file(relative):
                tests.append(item)
        churn, history_available = self.history({item["path"] for item in source}) if self.remaining() > 0 else ({}, False)
        for item in source:
            if history_available:
                item["history"] = churn.get(item["path"], {"commits": 0, "authors": 0})
        metadata_history = {item["path"]: churn.get(item["path"], {"commits": 0, "authors": 0}) for item in source_metadata}
        if history_available:
            for item in source_metadata:
                item["history"] = metadata_history[item["path"]]
        largest = [] if self.args.metadata_only else sorted(source, key=lambda x: (-x["loc"], -x["bytes"], x["path"]))[:self.args.max_hotspots]
        changed = sorted((item for item in source if item.get("history", {}).get("commits", 0) > 0),
                         key=lambda x: (-x["history"]["commits"], x["path"]))[:self.args.max_hotspots] if history_available else []
        if self.args.metadata_only and history_available:
            changed = sorted((item for item in source_metadata if item.get("history", {}).get("commits", 0) > 0),
                             key=lambda x: (-x["history"]["commits"], x["path"]))[:self.args.max_hotspots]
        # These labels describe inventory rank/threshold signals, not architecture.
        hints = []
        large_paths = {item["path"] for item in largest}
        changed_paths = {item["path"] for item in changed}
        by_path = {item["path"]: item for item in (source_metadata if self.args.metadata_only else source)}
        for name in sorted(large_paths | changed_paths):
            item = by_path[name]
            signals = (["top_size"] if name in large_paths else []) + (["top_churn"] if name in changed_paths else [])
            if not self.args.metadata_only and item["loc"] >= 1000:
                signals.append("large")
            if item.get("history", {}).get("commits", 0) >= 3:
                signals.append("high_churn")
            hint = {"path": name, "signals": signals,
                    "commits": item.get("history", {}).get("commits")}
            if not self.args.metadata_only:
                hint["loc"] = item["loc"]
            hints.append(hint)
        hints = sorted(hints, key=lambda x: (-len(x["signals"]), -x["commits"] if x["commits"] is not None else 0,
                                             -x.get("loc", 0), x["path"]))[:self.args.max_hotspots]
        test_paths = {item["path"] for item in tests}
        test_hints = []
        for item in sorted(tests, key=lambda x: x["path"])[:self.args.max_hotspots]:
            stem = PurePosixPath(item["path"]).stem.replace("test_", "").replace("_test", "").replace(".test", "").replace(".spec", "")
            nearby = sorted(x["path"] for x in source if x["path"] not in test_paths and PurePosixPath(x["path"]).stem == stem)[:3]
            test_hints.append({"path": item["path"], "related_path_hints": nearby})
        if len(context) > self.args.max_context_paths:
            self.reached("max_context_paths")
        result = {
            "schema_version": 1, "root": str(self.root),
            "history": {"available": history_available, "commits_inspected": self.limits["history_commits_inspected"],
                        "scope": f"HEAD, at most {self.args.max_history_commits} local commits; no fetch"},
            "counts": {**dict(totals), "source": len(source), "generated_source": len(generated), "test_source": len(tests)},
            "languages": dict(sorted(languages.items())),
            "layout": {
                "source_roots": [{"path": path, "source_files": count} for path, count in sorted(roots.items(), key=lambda x: (-x[1], x[0]))[:self.args.max_hotspots]],
                "manifest_module_roots": sorted(module_roots)[:self.args.max_hotspots],
            },
            "largest_source": largest,
            "highest_churn": changed,
            "hotspot_hints": hints,
            "generated_source_examples": [] if self.args.metadata_only else sorted(generated, key=lambda x: (-x["loc"], x["path"]))[:self.args.max_hotspots],
            "test_hints": test_hints,
            "context_paths": sorted(context, key=lambda x: (x["kind"], x["path"]))[:self.args.max_context_paths],
            "limits": self.limits,
            "warnings": sorted(set(self.warnings)),
        }
        if self.path_scopes or self.args.metadata_only:
            result["scan_scope"] = {
                "paths": list(self.path_scopes) if self.path_scopes else ["."],
                "metadata_only": self.args.metadata_only,
            }
        if self.args.metadata_only:
            result["scan_scope"]["signals_unavailable"] = [
                "line counts", "LOC-based size ranking", "content-derived source signals",
            ]
            result["source_metadata"] = source_metadata
        return result


def root_relative_scope(value: str) -> str:
    candidate = PurePosixPath(value)
    if not value or "\\" in value or candidate.is_absolute() or ".." in candidate.parts:
        raise argparse.ArgumentTypeError("scope must be a root-relative file or directory path")
    return candidate.as_posix().rstrip("/") or "."


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("path", nargs="?", default=".")
    result.add_argument("--json", action="store_true")
    result.add_argument(
        "--path",
        dest="path_scope",
        action="append",
        type=root_relative_scope,
        default=[],
        metavar="PATH",
        help="limit inventory to this root-relative file or directory subtree; repeatable",
    )
    result.add_argument(
        "--metadata-only",
        action="store_true",
        help="inspect Git and filesystem metadata without opening source file bodies",
    )
    result.add_argument("--max-files", type=int, default=10000)
    result.add_argument("--max-source-files", type=int, default=5000)
    result.add_argument("--max-history-commits", type=int, default=100)
    result.add_argument("--max-hotspots", type=int, default=20)
    result.add_argument("--max-context-paths", type=int, default=40)
    result.add_argument("--max-file-bytes", type=int, default=2_000_000)
    result.add_argument("--max-total-bytes", type=int, default=40_000_000)
    result.add_argument("--timeout-seconds", type=float, default=10.0)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if any(getattr(args, name) <= 0 for name in ("max_files", "max_source_files", "max_history_commits", "max_hotspots", "max_context_paths", "max_file_bytes", "max_total_bytes", "timeout_seconds")):
        print("all limits must be positive", file=sys.stderr)
        return 3
    requested = Path(args.path).expanduser()
    if not requested.is_dir():
        print("path must be an accessible directory", file=sys.stderr)
        return 2
    root = requested.resolve()
    try:
        check = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"],
                               capture_output=True, timeout=min(2.0, args.timeout_seconds),
                               env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"})
    except (OSError, subprocess.TimeoutExpired):
        print("Git root unavailable", file=sys.stderr)
        return 2
    if check.returncode != 0:
        print("path is not in a Git repository", file=sys.stderr)
        return 2
    root = Path(os.fsdecode(check.stdout.strip())).resolve()
    try:
        result = Inventory(root, args).run()
    except ScanFailure as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
