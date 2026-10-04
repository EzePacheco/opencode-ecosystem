#!/usr/bin/env python3
"""Bounded, read-only repository inventory for repo-readiness."""

from __future__ import annotations

import argparse
import json
import os
import re
import selectors
import subprocess
import sys
import time
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_VERSION = "2"
SCANNER_VERSION = "0.1.0"
DEFAULT_MAX_DEPTH = 6
DEFAULT_MAX_FILES = 10000
DEFAULT_MAX_BYTES = 2_000_000
DEFAULT_TIMEOUT = 5.0
MAX_OPENAPI_PROBES = 128
MAX_OPENAPI_PROBE_BYTES = 64 * 1024
OPENAPI_PROBE_SIZE = 4096
MAX_HISTORY_COMMITS = 50
MAX_HISTORY_BYTES = 64 * 1024
MAX_IGNORED_PATH_BYTES = 4_000_000

DIRECTORY_IGNORES = {
    ".git", ".hg", ".svn", "node_modules", "vendor", "vendors", "third_party",
    "dist", "build", "out", "target", "coverage", ".coverage", ".cache", ".next", ".pnpm-store",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv",
    "venv", "env", "eggs", ".tox", "tmp", "temp", "generated", "gen",
}
SENSITIVE_NAMES = {
    ".env", ".env.local", ".env.production", ".env.development",
    "credentials", "credential", "secrets", "secret", "private", "id_rsa",
    "id_ed25519", "token", "tokens", "password", "passwd", "shadow",
    "memory", "memories", "rag", "chunks", "embeddings", "embedding",
    "vectors", "vector", "vectordb", "vectorstore", "chroma", "faiss",
}
SENSITIVE_SUFFIXES = (".pem", ".key", ".p12", ".pfx", ".sqlite", ".db", ".duckdb")
BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz",
    ".tar", ".wasm", ".so", ".dll", ".exe", ".bin", ".pyc", ".class", ".jar",
}
MANIFEST_NAMES = {
    "package.json": "node",
    "pyproject.toml": "python",
    "requirements.txt": "python-requirements",
    "requirements-dev.txt": "python-requirements",
    "go.mod": "go",
    "cargo.toml": "rust",
    "pom.xml": "java-maven",
    "build.gradle": "java-gradle",
    "build.gradle.kts": "java-gradle",
    "composer.json": "php",
    "gemfile": "ruby",
    "mix.exs": "elixir",
}
CONTRACT_SUFFIXES = {
    ".proto": "protobuf", ".graphql": "graphql", ".gql": "graphql",
    ".dbml": "dbml", ".prisma": "prisma", ".avsc": "avro",
}
CONTRACT_NAMES = {
    "openapi.yaml": "openapi", "openapi.yml": "openapi", "openapi.json": "openapi",
    "asyncapi.yaml": "asyncapi", "asyncapi.yml": "asyncapi", "asyncapi.json": "asyncapi",
}
TEST_CONFIG_NAMES = {
    "pytest.ini",
    "tox.ini",
    ".mocharc.json",
    ".mocharc.js",
    ".mocharc.cjs",
    ".mocharc.mjs",
    ".mocharc.ts",
    "phpunit.xml",
    "phpunit.xml.dist",
    ".rspec",
}
TEST_CONFIG_STEMS = {
    "jest.config",
    "vitest.config",
    "playwright.config",
    "cypress.config",
    "karma.conf",
}
TEST_CONFIG_SUFFIXES = {".js", ".cjs", ".mjs", ".ts", ".cts", ".mts"}
LINK_RE = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")


class ScanFailure(Exception):
    """Expected failure with a CLI exit code."""

    def __init__(self, message: str, code: int = 2):
        super().__init__(message)
        self.code = code


class Scanner:
    def __init__(self, requested: Path, args: argparse.Namespace):
        self.requested = requested
        self.args = args
        self.started = time.monotonic()
        self.files_seen = 0
        self.bytes_read = 0
        self.stop_reason: str | None = None
        self.warnings: list[str] = []
        self.errors: list[str] = []
        self.file_records: list[tuple[Path, int]] = []
        self.markdown_files: list[Path] = []
        self.openapi_probes = 0
        self.openapi_probe_bytes = 0
        self.openapi_probe_limit_reached = False
        self.explicit_exclusions = tuple(args.exclude_path or ())
        self.ignored_untracked_paths: set[str] = set()

    def remaining_seconds(self) -> float:
        return max(0.0, self.args.timeout_seconds - (time.monotonic() - self.started))

    def git_output(self, root: Path, args: list[str], limit: int = 4096) -> tuple[bytes | None, bool]:
        """Read bounded local Git output; the bool reports output truncation."""
        remaining = self.remaining_seconds()
        if remaining <= 0:
            self.stop_reason = "timeout_reached"
            return None, False
        try:
            process = subprocess.Popen(
                ["git", "-C", str(root), *args], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            )
        except OSError:
            return None, False
        assert process.stdout is not None
        output = bytearray()
        truncated = False
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                deadline = time.monotonic() + min(remaining, 1.0)
                while True:
                    wait = deadline - time.monotonic()
                    if wait <= 0:
                        process.kill()
                        break
                    events = selector.select(wait)
                    if not events:
                        process.kill()
                        break
                    chunk = os.read(process.stdout.fileno(), min(4096, limit + 1 - len(output)))
                    if not chunk:
                        break
                    output.extend(chunk)
                    if len(output) > limit:
                        truncated = True
                        process.kill()
                        break
            process.wait(timeout=0.05)
        except (OSError, subprocess.TimeoutExpired):
            process.kill()
            process.wait()
        if process.stdout is not None:
            process.stdout.close()
        if process.returncode != 0 or truncated:
            return (bytes(output) if truncated else None), truncated
        return bytes(output), False

    def git_facts(self, root: Path) -> dict[str, Any]:
        facts: dict[str, Any] = {"branch": None, "head": None, "detached": None, "working_tree": None, "shallow": None}
        unknown: list[str] = []
        for key, args in (
            ("branch", ["symbolic-ref", "--quiet", "--short", "HEAD"]),
            ("head", ["rev-parse", "--verify", "HEAD"]),
            ("shallow", ["rev-parse", "--is-shallow-repository"]),
        ):
            output, _ = self.git_output(root, args, 256)
            if output is None:
                if key != "branch":
                    unknown.append(key)
                continue
            value = output.decode("utf-8", "replace").strip()
            if key == "branch":
                facts[key] = value or None
            elif key == "head":
                facts[key] = value or None
            else:
                facts[key] = value == "true" if value in {"true", "false"} else None
                if facts[key] is None:
                    unknown.append(key)
        facts["detached"] = True if facts["branch"] is None and facts["head"] is not None else (
            False if facts["branch"] is not None else None
        )

        # status output is consumed only until its first byte: any porcelain row means dirty.
        remaining = self.remaining_seconds()
        if remaining > 0:
            process = None
            try:
                process = subprocess.Popen(
                    ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=normal"],
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                )
                assert process.stdout is not None
                with selectors.DefaultSelector() as selector:
                    selector.register(process.stdout, selectors.EVENT_READ)
                    ready = selector.select(min(remaining, 1.0))
                    if ready:
                        facts["working_tree"] = bool(os.read(process.stdout.fileno(), 1))
                    if facts["working_tree"] is True:
                        process.kill()
                    try:
                        process.wait(timeout=0.05)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                    if facts["working_tree"] is False and process.returncode != 0:
                        facts["working_tree"] = None
            except OSError:
                facts["working_tree"] = None
            finally:
                if process is not None and process.stdout is not None:
                    process.stdout.close()
        if facts["working_tree"] is None:
            unknown.append("working_tree")
        if unknown:
            self.warnings.append("Git facts unavailable: " + ", ".join(sorted(set(unknown))))
        return facts

    def contributor_history(self, root: Path) -> dict[str, Any]:
        output, truncated = self.git_output(
            root,
            ["log", "--use-mailmap", f"-n{MAX_HISTORY_COMMITS}", "--format=%aN%x00%aE%x00"],
            MAX_HISTORY_BYTES,
        )
        counts: dict[tuple[str, str], int] = {}
        inspected = 0
        if output is not None:
            fields = output.split(b"\0")
            complete = len(fields) - (len(fields) % 2)
            # Only complete name/email pairs are counted; each pair represents one commit.
            for index in range(0, complete, 2):
                name = fields[index].decode("utf-8", "replace").strip()
                email = fields[index + 1].decode("utf-8", "replace").strip()
                if not name and not email:
                    continue
                key = (name, email)
                counts[key] = counts.get(key, 0) + 1
                inspected += 1
        if truncated:
            self.warnings.append("Git author history output limit reached")
        elif output is None:
            self.warnings.append("Git author history unavailable")
        authors = [
            {"name": name, "email": email, "commits": count}
            for (name, email), count in sorted(counts.items(), key=lambda item: (item[0][0].casefold(), item[0][1].casefold(), item[0]))
        ]
        return {
            "shallow": None,
            "commits_inspected": inspected,
            "limit_reached": inspected >= MAX_HISTORY_COMMITS or truncated,
            "authors": authors,
        }

    @staticmethod
    def declares_openapi_yaml(data: bytes) -> bool:
        try:
            text = data.decode("utf-8-sig", "strict")
        except UnicodeDecodeError:
            return False
        for line in text.splitlines():
            if line.lstrip().startswith("#") or not line.strip() or line.strip() == "---":
                continue
            if re.match(r"^(?:['\"]?openapi['\"]?\s*:\s*['\"]?3\.\d+(?:\.\d+)?['\"]?|['\"]?swagger['\"]?\s*:\s*['\"]?2\.0['\"]?)(?:\s*(?:#.*)?)?$", line):
                return True
        return False

    @staticmethod
    def declares_openapi_json(data: bytes) -> bool:
        try:
            text = data.decode("utf-8-sig", "strict")
        except UnicodeDecodeError:
            return False
        decoder = json.JSONDecoder()
        depth = 0
        index = 0
        while index < len(text):
            char = text[index]
            if char == '"':
                try:
                    value, end = decoder.raw_decode(text, index)
                except ValueError:
                    return False
                if depth == 1 and isinstance(value, str):
                    cursor = end
                    while cursor < len(text) and text[cursor].isspace():
                        cursor += 1
                    if cursor < len(text) and text[cursor] == ':':
                        cursor += 1
                        while cursor < len(text) and text[cursor].isspace():
                            cursor += 1
                        if value in {"openapi", "swagger"} and cursor < len(text) and text[cursor] == '"':
                            try:
                                version, _ = decoder.raw_decode(text, cursor)
                            except ValueError:
                                return False
                            if value == "openapi" and isinstance(version, str) and re.match(r"^3\.\d+(?:\.\d+)?$", version):
                                return True
                            if value == "swagger" and version == "2.0":
                                return True
                index = end
                continue
            if char in "{[":
                depth += 1
            elif char in "}]":
                depth -= 1
            index += 1
        return False

    def probe_openapi(self, path: Path) -> bool:
        if self.openapi_probes >= MAX_OPENAPI_PROBES or self.openapi_probe_bytes >= MAX_OPENAPI_PROBE_BYTES:
            self.openapi_probe_limit_reached = True
            return False
        if self.is_sensitive(path):
            return False
        self.check_budget()
        remaining_global = self.args.max_bytes - self.bytes_read
        remaining_probe = MAX_OPENAPI_PROBE_BYTES - self.openapi_probe_bytes
        amount = min(OPENAPI_PROBE_SIZE, remaining_global, remaining_probe)
        if amount <= 0:
            self.openapi_probe_limit_reached = True
            return False
        self.openapi_probes += 1
        try:
            with path.open("rb") as stream:
                data = stream.read(amount)
        except OSError as exc:
            self.errors.append(f"partial read failure: {type(exc).__name__}")
            return False
        self.openapi_probe_bytes += len(data)
        self.bytes_read += len(data)
        if path.suffix.lower() in {".yaml", ".yml"}:
            return self.declares_openapi_yaml(data)
        return self.declares_openapi_json(data)

    def check_budget(self) -> None:
        if time.monotonic() - self.started > self.args.timeout_seconds:
            self.stop_reason = "timeout_reached"
            raise StopIteration
        if self.files_seen >= self.args.max_files:
            self.stop_reason = "files_limit_reached"
            raise StopIteration

    @staticmethod
    def is_sensitive(path: Path) -> bool:
        for part in path.parts:
            lower = part.lower()
            if lower in SENSITIVE_NAMES or lower.endswith(SENSITIVE_SUFFIXES):
                return True
            if lower.startswith(".env"):
                return True
        return False

    @staticmethod
    def rel(path: Path, root: Path) -> str:
        try:
            return path.relative_to(root).as_posix() or "."
        except ValueError:
            return path.as_posix()

    def git_root(self) -> tuple[Path, str, bool]:
        if not self.requested.exists() or not self.requested.is_dir():
            raise ScanFailure("path is not an accessible directory", 2)
        for candidate in (self.requested, *self.requested.parents):
            marker = candidate / ".git"
            if marker.is_dir():
                return candidate.resolve(), "directory", False
            if marker.is_file():
                return candidate.resolve(), "file", True
        raise ScanFailure("path does not belong to a Git repository", 2)

    def load_ignored_untracked_paths(self, root: Path) -> set[str]:
        """Return ignored untracked paths, collapsing fully ignored directories."""
        output, truncated = self.git_output(
            root,
            ["ls-files", "--others", "--ignored", "--exclude-standard", "--directory", "-z"],
            MAX_IGNORED_PATH_BYTES,
        )
        if output is None or truncated:
            raise ScanFailure("cannot safely resolve Git-ignored untracked paths", 2)
        return {
            os.fsdecode(raw).rstrip("/")
            for raw in output.split(b"\0")
            if raw
        }

    def path_excluded(self, relative: str) -> bool:
        """Apply explicit subtree exclusions and optional Git ignore filtering."""
        path = relative.rstrip("/")
        for excluded in self.explicit_exclusions:
            if path == excluded or path.startswith(excluded + "/"):
                return True
        for ignored in self.ignored_untracked_paths:
            if path == ignored or path.startswith(ignored + "/"):
                return True
        return False

    def safe_read(self, path: Path) -> bytes | None:
        self.check_budget()
        if self.is_sensitive(path):
            self.warnings.append("sensitive path omitted")
            return None
        try:
            size = path.stat().st_size
            remaining = self.args.max_bytes - self.bytes_read
            if remaining <= 0 or size > remaining:
                self.stop_reason = "bytes_limit_reached"
                raise StopIteration
            data = path.read_bytes()
        except StopIteration:
            raise
        except (OSError, UnicodeError) as exc:
            self.errors.append(f"partial read failure: {type(exc).__name__}")
            return None
        self.bytes_read += len(data)
        return data

    @staticmethod
    def is_test_config_name(name: str) -> bool:
        if name in TEST_CONFIG_NAMES:
            return True
        for stem in TEST_CONFIG_STEMS:
            if name.startswith(f"{stem}.") and name[len(stem):] in TEST_CONFIG_SUFFIXES:
                return True
        return False

    def classify_file(self, path: Path, root: Path, size: int) -> None:
        rel = self.rel(path, root)
        name = path.name.lower()
        suffix = path.suffix.lower()
        self.file_records.append((path, size))
        if name in {"readme", "readme.md", "readme.rst", "readme.txt"} or name.startswith("readme."):
            self.result["documentation"]["readmes"].append({"path": rel, "bytes": size})
        if name in {"agents.md", "agents.override.md", "llm_context.md", "llm-context.md"}:
            if name == "agents.override.md":
                key = "override_files"
            elif name.startswith("agents"):
                key = "agents_files"
            else:
                key = "llm_context_files"
            self.result["context"][key].append({"path": rel, "bytes": size})
        if name in MANIFEST_NAMES:
            self.result["manifests"].append({"path": rel, "kind": MANIFEST_NAMES[name]})
        if name in CONTRACT_NAMES:
            self.result["contracts"].append({"path": rel, "kind": CONTRACT_NAMES[name]})
        elif suffix in CONTRACT_SUFFIXES:
            self.result["contracts"].append({"path": rel, "kind": CONTRACT_SUFFIXES[suffix]})
        elif suffix in {".yaml", ".yml", ".json"} and self.probe_openapi(path):
            self.result["contracts"].append({"path": rel, "kind": "openapi"})
        collaboration = self.result["collaboration"]
        if name == "contributing" or (name.startswith("contributing.") and suffix in {".md", ".markdown", ".rst", ".txt", ".adoc"}):
            collaboration["contributor_guides"].append({"path": rel, "bytes": size})
        if name == "codeowners" and rel.lower() in {"codeowners", ".github/codeowners", "docs/codeowners", ".gitlab/codeowners"}:
            collaboration["codeowners"].append({"path": rel, "bytes": size})
        lower_rel = rel.lower()
        if lower_rel in {"pull_request_template.md", "docs/pull_request_template.md", ".github/pull_request_template.md"} or (
            lower_rel.startswith(".github/pull_request_template/") and suffix in {".md", ".markdown"}
        ) or (
            (lower_rel.startswith("pull_request_template/") or lower_rel.startswith("docs/pull_request_template/"))
            and suffix in {".md", ".markdown"}
        ) or (
            (lower_rel.startswith(".gitlab/merge_request_templates/") or lower_rel.startswith("merge_request_templates/"))
            and suffix in {".md", ".markdown"}
        ):
            collaboration["pull_request_templates"].append({"path": rel, "bytes": size})
        if rel == ".mailmap":
            collaboration["mailmap"] = {"path": rel, "bytes": size}
        if suffix in {".md", ".markdown", ".mdx", ".rst"}:
            self.markdown_files.append(path)
        if name.startswith(("dockerfile", "compose.")) or name in {"docker-compose.yml", "docker-compose.yaml"}:
            self.result["automation"]["container_configs"].append(rel)
        if name in {"makefile", "justfile", "taskfile.yml", "taskfile.yaml"} or "build" in name:
            self.result["automation"]["build_configs"].append(rel)
        if any(token in name for token in ("eslint", "ruff", "flake8", "pylint", "prettier", "lint")):
            self.result["automation"]["lint_configs"].append(rel)
        if self.is_test_config_name(name):
            self.result["automation"]["test_configs"].append(rel)
        if re.search(r"(^|[._-])(test|spec)([._-]|$)", name) or "/tests/" in f"/{rel.lower()}/":
            self.result["automation"]["test_files"].append(rel)
        if name in {".gitlab-ci.yml", "jenkinsfile", "azure-pipelines.yml", "buildkite.yml"}:
            self.result["automation"]["ci"].append(rel)
        if "hook" in name:
            self.result["harness"]["hooks"].append(rel)
        if "observ" in name or "sentry" in name or "otel" in name:
            self.result["harness"]["observability_configs"].append(rel)
        if "diagnostic" in name or name in {"doctor.json", "healthcheck.yml", "healthcheck.yaml"}:
            self.result["harness"]["diagnostic_configs"].append(rel)
        if name == "package.json":
            data = self.safe_read(path)
            if data is not None:
                try:
                    parsed = json.loads(data.decode("utf-8"))
                    scripts = parsed.get("scripts", {})
                    if isinstance(scripts, dict):
                        self.result["automation"]["package_scripts"].extend(sorted(str(k) for k in scripts))
                except (ValueError, UnicodeError):
                    self.warnings.append("package manifest could not be parsed")

    def scan(self) -> dict[str, Any]:
        root, git_kind, worktree = self.git_root()
        git_facts = self.git_facts(root)
        git_history = self.contributor_history(root)
        git_history["shallow"] = git_facts["shallow"]
        self.result = {
            "schema_version": SCHEMA_VERSION,
            "scanner_version": SCANNER_VERSION,
            "requested_path": str(self.requested),
            "git": {"root": str(root), "git_dir_kind": git_kind, "worktree": worktree, "nested_roots": [], **git_facts},
            "repository": {"name": root.name, "approx_file_count": 0, "approx_total_bytes": 0},
            "manifests": [],
            "context": {"agents_files": [], "override_files": [], "llm_context_files": []},
            "documentation": {"readmes": [], "docs_roots": [], "specs": [], "adrs": [], "runbooks": [], "approx_files": 0, "approx_bytes": 0},
            "contracts": [],
            "collaboration": {"contributor_guides": [], "codeowners": [], "pull_request_templates": [], "mailmap": None, "git_history": git_history},
            "automation": {"package_scripts": [], "lint_configs": [], "test_configs": [], "test_files": [], "ci": [], "build_configs": [], "container_configs": []},
            "harness": {"skills": [], "hooks": [], "diagnostic_configs": [], "observability_configs": []},
            "links": {"markdown_files_checked": 0, "internal_links": 0, "broken_relative_links": [], "skipped_links": 0},
            "limits": {"files_limit_reached": False, "depth_limit_reached": False, "timeout_reached": False, "bytes_limit_reached": False, "openapi_probe_limit_reached": False},
            "warnings": self.warnings,
            "errors": self.errors,
            "timing_ms": 0,
        }
        if self.args.respect_gitignore:
            self.ignored_untracked_paths = self.load_ignored_untracked_paths(root)
            self.warnings.append(
                "Git ignore filtering applied to ignored untracked paths only; tracked paths remain eligible unless explicitly excluded"
            )
        if self.explicit_exclusions:
            self.warnings.append(
                f"explicit root-relative path exclusions applied ({len(self.explicit_exclusions)} rule(s))"
            )
        try:
            self.walk(root)
            self.check_links(root)
        except StopIteration:
            pass
        if self.stop_reason:
            self.result["limits"][self.stop_reason] = True
        self.result["limits"]["openapi_probe_limit_reached"] = self.openapi_probe_limit_reached
        self.result["repository"]["approx_file_count"] = len(self.file_records)
        self.result["repository"]["approx_total_bytes"] = sum(size for _, size in self.file_records)
        self.result["documentation"]["approx_files"] = sum(
            1 for path, _ in self.file_records if path.suffix.lower() in {".md", ".markdown", ".mdx", ".rst"}
        )
        self.result["documentation"]["approx_bytes"] = sum(
            size for path, size in self.file_records if path.suffix.lower() in {".md", ".markdown", ".mdx", ".rst"}
        )
        for key in ("manifests", "contracts"):
            self.result[key] = sorted(self.result[key], key=lambda item: (item.get("path", ""), item.get("kind", "")))
        for key in ("contributor_guides", "codeowners", "pull_request_templates"):
            self.result["collaboration"][key] = sorted(
                {item["path"]: item for item in self.result["collaboration"][key]}.values(),
                key=lambda item: item["path"],
            )
        self.warnings[:] = sorted(set(self.warnings))
        self.errors[:] = sorted(set(self.errors))
        self.result["timing_ms"] = int((time.monotonic() - self.started) * 1000)
        return self.result

    def walk(self, root: Path) -> None:
        def visit(directory: Path, depth: int) -> None:
            self.check_budget()
            try:
                entries = sorted(directory.iterdir(), key=lambda item: item.name.lower())
            except OSError as exc:
                self.errors.append(f"directory read failure: {type(exc).__name__}")
                return
            for entry in entries:
                self.check_budget()
                relative = self.rel(entry, root)
                if self.path_excluded(relative):
                    continue
                if entry.is_symlink():
                    self.warnings.append("symlink omitted")
                    continue
                if self.is_sensitive(entry):
                    self.warnings.append("sensitive path omitted")
                    continue
                if entry.is_dir():
                    if entry.name.lower() in DIRECTORY_IGNORES:
                        continue
                    marker = entry / ".git"
                    if entry != root and (marker.is_dir() or marker.is_file()):
                        nested = self.rel(entry, root)
                        self.result["git"]["nested_roots"].append(nested)
                        if not self.args.include_nested_git:
                            continue
                        continue
                    if depth >= self.args.max_depth:
                        self.stop_reason = "depth_limit_reached"
                        continue
                    if entry.name.lower() in {"docs", "documentation", "spec", "specs"}:
                        self.result["documentation"]["docs_roots"].append(self.rel(entry, root))
                        if entry.name.lower() in {"spec", "specs"}:
                            self.result["documentation"]["specs"].append(self.rel(entry, root))
                    if entry.name.lower() in {"adr", "adrs", "decisions"}:
                        self.result["documentation"]["adrs"].append(self.rel(entry, root))
                    if entry.name.lower() in {"runbook", "runbooks", "playbooks"}:
                        self.result["documentation"]["runbooks"].append(self.rel(entry, root))
                    if entry.name.lower() in {"skills", ".skills"}:
                        self.result["harness"]["skills"].append(self.rel(entry, root))
                    if entry.name.lower() == ".github":
                        workflows = entry / "workflows"
                        workflows_rel = self.rel(workflows, root)
                        if not self.path_excluded(workflows_rel) and workflows.is_dir():
                            self.result["automation"]["ci"].append(workflows_rel)
                    visit(entry, depth + 1)
                    continue
                if not entry.is_file():
                    continue
                try:
                    size = entry.stat().st_size
                except OSError:
                    self.errors.append("file metadata failure")
                    continue
                if entry.suffix.lower() in BINARY_SUFFIXES:
                    continue
                self.files_seen += 1
                self.classify_file(entry, root, size)

        try:
            visit(root, 0)
        except StopIteration:
            pass

    def check_links(self, root: Path) -> None:
        for path in sorted(self.markdown_files):
            try:
                self.check_budget()
                data = self.safe_read(path)
            except StopIteration:
                break
            if data is None:
                continue
            self.result["links"]["markdown_files_checked"] += 1
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                self.result["links"]["skipped_links"] += 1
                continue
            for raw in LINK_RE.findall(text):
                target = raw.strip().split()[0].strip("<>")
                if not target or target.startswith(("#", "/", "//")) or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
                    self.result["links"]["skipped_links"] += 1
                    continue
                target = target.split("#", 1)[0].split("?", 1)[0]
                if not target:
                    self.result["links"]["skipped_links"] += 1
                    continue
                self.result["links"]["internal_links"] += 1
                candidate = (path.parent / target).resolve()
                try:
                    candidate.relative_to(root)
                except ValueError:
                    self.result["links"]["skipped_links"] += 1
                    continue
                if not candidate.exists():
                    self.result["links"]["broken_relative_links"].append({"source": self.rel(path, root), "target": target})


def root_relative_path(value: str) -> str:
    candidate = PurePosixPath(value)
    if (
        not value
        or "\\" in value
        or candidate.is_absolute()
        or candidate.as_posix() in {"", "."}
        or ".." in candidate.parts
    ):
        raise argparse.ArgumentTypeError("path must be a non-empty root-relative file or directory")
    return candidate.as_posix().rstrip("/")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Bounded, read-only Git repository inventory")
    p.add_argument("path", nargs="?", default=".", help="repository directory; default: cwd")
    p.add_argument("--json", action="store_true", help="emit JSON only on stdout")
    p.add_argument("--pretty", action="store_true", help="indent JSON; valid only with --json")
    p.add_argument("--max-depth", type=int, default=DEFAULT_MAX_DEPTH, help=f"maximum directory depth (default: {DEFAULT_MAX_DEPTH})")
    p.add_argument("--max-files", type=int, default=DEFAULT_MAX_FILES, help=f"maximum files inspected (default: {DEFAULT_MAX_FILES})")
    p.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES, help=f"maximum bytes read (default: {DEFAULT_MAX_BYTES})")
    p.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT, help=f"wall-clock budget (default: {DEFAULT_TIMEOUT})")
    p.add_argument("--include-nested-git", action="store_true", help="report nested Git roots for discovery; never merge their contents")
    p.add_argument(
        "--respect-gitignore",
        action="store_true",
        help="skip Git-ignored untracked paths before traversal; tracked paths remain eligible",
    )
    p.add_argument(
        "--exclude-path",
        action="append",
        type=root_relative_path,
        default=[],
        metavar="PATH",
        help="exclude a root-relative file or directory subtree before traversal (repeatable)",
    )
    p.add_argument("--schema-version", action="store_true", help="print the JSON schema version and exit")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.schema_version:
        if args.pretty:
            print("--pretty is valid only with --json", file=sys.stderr)
            return 3
        print(SCHEMA_VERSION)
        return 0
    if args.pretty and not args.json:
        print("--pretty is valid only with --json", file=sys.stderr)
        return 3
    if min(args.max_depth, args.max_files, args.max_bytes) < 0 or args.timeout_seconds <= 0:
        print("limits must be non-negative and timeout must be positive", file=sys.stderr)
        return 3
    requested = Path(args.path).expanduser().absolute()
    try:
        result = Scanner(requested, args).scan()
    except ScanFailure as exc:
        print(str(exc), file=sys.stderr)
        return exc.code
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        print(f"internal scanner error: {type(exc).__name__}", file=sys.stderr)
        return 4
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=False))
    else:
        print(f"Git root: {result['git']['root']}")
        print(f"Files: ~{result['repository']['approx_file_count']}; bytes: ~{result['repository']['approx_total_bytes']}")
        print(f"Manifests: {len(result['manifests'])}; contracts: {len(result['contracts'])}")
        if result["warnings"] or result["errors"]:
            print(f"Warnings: {len(result['warnings'])}; errors: {len(result['errors'])}", file=sys.stderr)
    # Recoverable omissions and bounded partial results remain represented in JSON.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
