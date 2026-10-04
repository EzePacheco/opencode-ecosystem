import json
import importlib.util
from contextlib import redirect_stderr
from io import StringIO
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "repo_inventory.py"
SPEC = importlib.util.spec_from_file_location("repo_inventory", SCRIPT)
assert SPEC and SPEC.loader
repo_inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(repo_inventory)


class InventoryTests(unittest.TestCase):
    def run_scan(self, root: Path, *args: str):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(root), "--json", *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def make_repo(self) -> Path:
        root = Path(tempfile.mkdtemp(prefix="repo-readiness-"))
        subprocess.run(["git", "init", "--quiet", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "Scanner Test"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "scanner@example.test"], check=True)
        return root

    def commit(self, root: Path, filename: str = "tracked.txt", content: str = "tracked\n") -> str:
        (root / filename).write_text(content, encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", filename], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "--quiet", "-m", "fixture"], check=True)
        return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True, text=True, capture_output=True).stdout.strip()

    def test_d1_facts_and_json_stdout(self):
        root = self.make_repo()
        (root / "README.md").write_text("See [missing](docs/missing.md) and [local](guide.md).\n", encoding="utf-8")
        (root / "guide.md").write_text("guide\n", encoding="utf-8")
        (root / "AGENTS.md").write_text("local rules\n", encoding="utf-8")
        (root / "AGENTS.override.md").write_text("override\n", encoding="utf-8")
        (root / "package.json").write_text('{"scripts":{"test":"pytest","lint":"ruff"}}', encoding="utf-8")
        result = self.run_scan(root)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr.count("{"), 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["schema_version"], "2")
        self.assertEqual(data["context"]["agents_files"][0]["path"], "AGENTS.md")
        self.assertEqual(data["context"]["override_files"][0]["path"], "AGENTS.override.md")
        self.assertEqual(sorted(data["automation"]["package_scripts"]), ["lint", "test"])
        self.assertEqual(data["links"]["internal_links"], 2)
        self.assertEqual(data["links"]["broken_relative_links"][0]["target"], "docs/missing.md")

    def test_nested_git_is_reported_but_not_merged(self):
        root = self.make_repo()
        nested = root / "nested"
        nested.mkdir()
        (nested / ".git").mkdir()
        (nested / "nested-only.md").write_text("not part of parent\n", encoding="utf-8")
        result = self.run_scan(root)
        data = json.loads(result.stdout)
        self.assertEqual(data["git"]["nested_roots"], ["nested"])
        self.assertNotIn("nested-only.md", json.dumps(data))

    def test_paths_inside_same_root_resolve_to_same_git_root(self):
        root = self.make_repo()
        child = root / "src" / "module"
        child.mkdir(parents=True)
        first = json.loads(self.run_scan(root).stdout)
        second = json.loads(self.run_scan(child, "--pretty").stdout)
        self.assertEqual(first["git"]["root"], second["git"]["root"])

    def test_git_file_worktree_marker(self):
        root = Path(tempfile.mkdtemp(prefix="repo-readiness-worktree-"))
        (root / ".git").write_text("gitdir: /tmp/opaque-worktree-git\n", encoding="utf-8")
        result = self.run_scan(root)
        data = json.loads(result.stdout)
        self.assertEqual(data["git"]["git_dir_kind"], "file")
        self.assertTrue(data["git"]["worktree"])

    def test_symlink_and_sensitive_paths_are_omitted(self):
        root = self.make_repo()
        outside = Path(tempfile.mkdtemp(prefix="repo-readiness-outside-"))
        (outside / "outside.md").write_text("outside\n", encoding="utf-8")
        (root / "outside-link.md").symlink_to(outside / "outside.md")
        (root / "outside-dir").symlink_to(outside, target_is_directory=True)
        (root / ".env").write_text("TOKEN=do-not-read\n", encoding="utf-8")
        (root / "memory-store").mkdir()
        (root / "memory-store" / "chunk.txt").write_text("do-not-read\n", encoding="utf-8")
        result = self.run_scan(root)
        data = json.loads(result.stdout)
        rendered = json.dumps(data)
        self.assertNotIn("TOKEN=", rendered)
        self.assertNotIn("chunk.txt", rendered)
        self.assertGreaterEqual(len(data["warnings"]), 2)
        self.assertEqual(result.returncode, 0)

    def test_gitignore_and_explicit_exclusions_precede_content_reads(self):
        root = self.make_repo()
        (root / ".gitignore").write_text("excluded-tree/\n", encoding="utf-8")
        fixtures = {
            "README.md": "# Allowed\n",
            "package.json": '{"scripts":{"test":"synthetic"}}',
            "excluded-tree/locked/package.json": '{"scripts":{"local":"synthetic"}}',
            ".github/workflows/package.json": '{"scripts":{"ci":"synthetic"}}',
            "excluded-tree/ignored.txt": "SYNTHETIC_IGNORED_CONTENT\n",
            "excluded-tree/ignored-dir/package.json": '{"scripts":{"ignored":"synthetic"}}',
            "credentials/config.yaml": "SYNTHETIC_SENSITIVE_CONTENT\n",
            ".env": "SYNTHETIC_ENV_CONTENT\n",
        }
        for relative, content in fixtures.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", ".gitignore", "README.md", "package.json", ".github/workflows/package.json"], check=True)
        subprocess.run(["git", "-C", str(root), "add", "-f", "excluded-tree/locked/package.json"], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "--quiet", "-m", "synthetic fixtures"], check=True)

        respect_only = self.run_scan(root, "--respect-gitignore")
        self.assertEqual(respect_only.returncode, 0, respect_only.stderr)
        respect_data = json.loads(respect_only.stdout)
        manifest_paths = {item["path"] for item in respect_data["manifests"]}
        self.assertIn("excluded-tree/locked/package.json", manifest_paths)
        self.assertIn(".github/workflows/package.json", manifest_paths)
        self.assertNotIn("excluded-tree/ignored.txt", json.dumps(respect_data))
        self.assertNotIn("SYNTHETIC_IGNORED_CONTENT", respect_only.stdout)
        self.assertTrue(any("tracked paths remain eligible" in warning for warning in respect_data["warnings"]))

        args = repo_inventory.parser().parse_args([
            str(root), "--respect-gitignore",
            "--exclude-path", "excluded-tree/locked",
            "--exclude-path", ".github/workflows",
        ])
        scanner = repo_inventory.Scanner(root, args)
        forbidden = {
            root / "excluded-tree/ignored.txt",
            root / "excluded-tree/ignored-dir/package.json",
            root / "excluded-tree/locked/package.json",
            root / ".github/workflows/package.json",
            root / "credentials/config.yaml",
            root / ".env",
        }
        opened: list[str] = []
        traversed: list[str] = []
        original_open = Path.open
        original_iterdir = Path.iterdir

        def guarded_open(path, *open_args, **open_kwargs):
            if path in forbidden:
                raise AssertionError(f"excluded path content opened: {path.name}")
            if path.is_relative_to(root):
                opened.append(path.relative_to(root).as_posix())
            return original_open(path, *open_args, **open_kwargs)

        def guarded_iterdir(path):
            if path in {root / "excluded-tree/ignored-dir", root / "excluded-tree/locked", root / ".github/workflows"}:
                raise AssertionError(f"excluded directory traversed: {path.name}")
            if path.is_relative_to(root):
                traversed.append(path.relative_to(root).as_posix())
            return original_iterdir(path)

        with patch.object(Path, "open", guarded_open), patch.object(Path, "iterdir", guarded_iterdir):
            result = scanner.scan()
        self.assertIn("README.md", opened)
        self.assertIn("package.json", opened)
        self.assertNotIn("excluded-tree/locked/package.json", json.dumps(result))
        self.assertNotIn(".github/workflows/package.json", json.dumps(result))
        self.assertNotIn(".github/workflows", json.dumps(result))
        self.assertNotIn("SYNTHETIC_SENSITIVE_CONTENT", json.dumps(result))
        self.assertNotIn("SYNTHETIC_ENV_CONTENT", json.dumps(result))
        self.assertNotIn("excluded-tree/ignored-dir", traversed)
        self.assertNotIn("excluded-tree/locked", traversed)
        self.assertNotIn(".github/workflows", traversed)
        self.assertTrue(any("explicit root-relative path exclusions applied" in warning for warning in result["warnings"]))

    def test_gitignore_resolution_failure_stops_before_walk(self):
        root = self.make_repo()
        args = repo_inventory.parser().parse_args([str(root), "--respect-gitignore"])
        scanner = repo_inventory.Scanner(root, args)
        with patch.object(scanner, "load_ignored_untracked_paths", side_effect=repo_inventory.ScanFailure("synthetic Git failure")):
            with patch.object(scanner, "walk", side_effect=AssertionError("walk should not start")):
                with self.assertRaises(repo_inventory.ScanFailure):
                    scanner.scan()

    def test_bounds_are_reported(self):
        root = self.make_repo()
        for index in range(4):
            (root / f"file-{index}.txt").write_text("12345", encoding="utf-8")
        (root / "README.md").write_text("content\n", encoding="utf-8")
        result = self.run_scan(root, "--max-files", "2")
        data = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(data["limits"]["files_limit_reached"])

        (root / "subdir").mkdir()
        (root / "subdir" / "nested.txt").write_text("nested\n", encoding="utf-8")
        result = self.run_scan(root, "--max-depth", "0")
        data = json.loads(result.stdout)
        self.assertTrue(data["limits"]["depth_limit_reached"])

        result = self.run_scan(root, "--max-bytes", "1")
        data = json.loads(result.stdout)
        self.assertTrue(data["limits"]["bytes_limit_reached"])

    def test_contracts_ci_and_configs(self):
        root = self.make_repo()
        (root / "openapi.yaml").write_text("openapi: 3.0.0\n", encoding="utf-8")
        (root / "schema.proto").write_text("syntax = \"proto3\";\n", encoding="utf-8")
        (root / "docs" / "adr").mkdir(parents=True)
        (root / ".github" / "workflows").mkdir(parents=True)
        (root / ".github" / "workflows" / "ci.yml").write_text("name: ci\n", encoding="utf-8")
        result = self.run_scan(root)
        data = json.loads(result.stdout)
        kinds = {item["kind"] for item in data["contracts"]}
        self.assertEqual(kinds, {"openapi", "protobuf"})
        self.assertIn("docs/adr", data["documentation"]["adrs"])
        self.assertIn(".github/workflows", data["automation"]["ci"])

    def test_openapi_detection_by_content_and_name_fast_paths(self):
        root = self.make_repo()
        fixtures = {
            "openapi.yaml": "openapi: 3.1.0\n",
            "api/openapi.yml": "openapi: '3.0.3'\n",
            "openapi/pokerbase.yaml": "info:\n  title: API\nopenapi: 3.0.0\n",
            "contracts/public.yml": "swagger: \"2.0\"\ninfo:\n  title: Legacy\n",
            "docs/api/spec.json": '{"openapi":"3.1.0","info":{"title":"API"}}',
            "foo/bar/service-contract.yaml": "swagger: 2.0\n",
            "ordinary.yaml": "name: openapi\nmetadata:\n  swagger: 2.0\n",
            "ordinary.json": '{"info":{"openapi":"3.0.0"},"name":"service"}',
            "text-mention.yml": "description: this mentions openapi: 3.0.0\n",
        }
        for relative, content in fixtures.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        data = json.loads(self.run_scan(root).stdout)
        contracts = {item["path"]: item["kind"] for item in data["contracts"]}
        self.assertEqual(
            contracts,
            {
                "api/openapi.yml": "openapi",
                "contracts/public.yml": "openapi",
                "docs/api/spec.json": "openapi",
                "foo/bar/service-contract.yaml": "openapi",
                "openapi.yaml": "openapi",
                "openapi/pokerbase.yaml": "openapi",
            },
        )

    def test_generated_directories_do_not_count_toward_inventory_or_limits(self):
        root = self.make_repo()
        for directory in (".next", ".pnpm-store"):
            generated = root / directory
            generated.mkdir()
            (generated / "large.js").write_text("generated\n" * 100, encoding="utf-8")
        (root / "visible.txt").write_text("visible\n", encoding="utf-8")
        data = json.loads(self.run_scan(root, "--max-files", "1").stdout)
        self.assertEqual(data["repository"]["approx_file_count"], 1)
        self.assertEqual(data["repository"]["approx_total_bytes"], len(b"visible\n"))
        self.assertFalse(data["limits"]["files_limit_reached"])
        self.assertNotIn(".next", json.dumps(data))
        self.assertNotIn(".pnpm-store", json.dumps(data))

    def test_openapi_probe_budget_is_bounded_and_reported(self):
        root = self.make_repo()
        for index in range(130):
            (root / f"ordinary-{index:03}.yaml").write_text("name: ordinary\n", encoding="utf-8")
        data = json.loads(self.run_scan(root).stdout)
        self.assertEqual(data["contracts"], [])
        self.assertTrue(data["limits"]["openapi_probe_limit_reached"])

    def test_collaboration_paths_and_mailmap_are_factual(self):
        root = self.make_repo()
        files = {
            "docs/CONTRIBUTING.rst": "guide\n",
            ".github/CODEOWNERS": "* @team\n",
            ".gitlab/merge_request_templates/default.md": "template\n",
            ".mailmap": "Canonical Author <canonical@example.test> Alias Author <alias@example.test>\n",
        }
        for relative, content in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        data = json.loads(self.run_scan(root).stdout)
        collaboration = data["collaboration"]
        self.assertEqual([item["path"] for item in collaboration["contributor_guides"]], ["docs/CONTRIBUTING.rst"])
        self.assertEqual([item["path"] for item in collaboration["codeowners"]], [".github/CODEOWNERS"])
        self.assertEqual([item["path"] for item in collaboration["pull_request_templates"]], [".gitlab/merge_request_templates/default.md"])
        self.assertEqual(collaboration["mailmap"]["path"], ".mailmap")

    def test_git_state_history_mailmap_and_detached_head(self):
        root = self.make_repo()
        self.commit(root, "one.txt", "one\n")
        subprocess.run(["git", "-C", str(root), "config", "user.name", "Alias Author"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "alias@example.test"], check=True)
        self.commit(root, "two.txt", "two\n")
        (root / ".mailmap").write_text("Canonical Author <canonical@example.test> Alias Author <alias@example.test>\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", ".mailmap"], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "--quiet", "-m", "mailmap"], check=True)
        head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True, text=True, capture_output=True).stdout.strip()
        (root / "untracked.txt").write_text("dirty\n", encoding="utf-8")
        data = json.loads(self.run_scan(root).stdout)
        self.assertTrue(data["git"]["branch"])
        self.assertEqual(data["git"]["head"], head)
        self.assertFalse(data["git"]["detached"])
        self.assertTrue(data["git"]["working_tree"])
        self.assertFalse(data["git"]["shallow"])
        history = data["collaboration"]["git_history"]
        self.assertEqual(history["commits_inspected"], 3)
        self.assertEqual(history["shallow"], False)
        self.assertFalse(history["limit_reached"])
        self.assertEqual(history["authors"], [{"name": "Canonical Author", "email": "canonical@example.test", "commits": 2}, {"name": "Scanner Test", "email": "scanner@example.test", "commits": 1}])
        subprocess.run(["git", "-C", str(root), "add", "untracked.txt"], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "--quiet", "-m", "clean checkout"], check=True)
        clean = json.loads(self.run_scan(root).stdout)["git"]
        self.assertFalse(clean["working_tree"])
        subprocess.run(["git", "-C", str(root), "checkout", "--quiet", "--detach", "HEAD"], check=True)
        detached = json.loads(self.run_scan(root).stdout)["git"]
        self.assertIsNone(detached["branch"])
        self.assertTrue(detached["detached"])

    def test_git_shallow_clone_fact(self):
        source = self.make_repo()
        self.commit(source)
        clone_parent = Path(tempfile.mkdtemp(prefix="repo-readiness-shallow-"))
        clone = clone_parent / "clone"
        try:
            subprocess.run(["git", "clone", "--quiet", "--depth", "1", source.resolve().as_uri(), str(clone)], check=True)
            data = json.loads(self.run_scan(clone).stdout)
            self.assertTrue(data["git"]["shallow"])
            self.assertEqual(data["collaboration"]["git_history"]["shallow"], True)
            self.assertEqual(data["collaboration"]["git_history"]["commits_inspected"], 1)
        finally:
            import shutil
            shutil.rmtree(clone_parent, ignore_errors=True)

    def test_test_configs_require_structural_names(self):
        root = self.make_repo()
        for relative in (
            "docs/testing-strategy.md",
            "docs/test-plan.md",
            "docs/vitest-guide.md",
            "specs/testing-contract.md",
            "README-testing.md",
        ):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("documentation\n", encoding="utf-8")
        for relative in (
            "vitest.config.js",
            "jest.config.ts",
            "playwright.config.ts",
            "pytest.ini",
            "tox.ini",
        ):
            (root / relative).write_text("config\n", encoding="utf-8")
        (root / "tests" / "test_inventory.py").parent.mkdir()
        (root / "tests" / "test_inventory.py").write_text("def test_fact(): pass\n", encoding="utf-8")

        result = self.run_scan(root)
        data = json.loads(result.stdout)

        self.assertEqual(
            sorted(data["automation"]["test_configs"]),
            [
                "jest.config.ts",
                "playwright.config.ts",
                "pytest.ini",
                "tox.ini",
                "vitest.config.js",
            ],
        )
        self.assertIn("tests/test_inventory.py", data["automation"]["test_files"])
        for documentary in (
            "docs/testing-strategy.md",
            "docs/test-plan.md",
            "docs/vitest-guide.md",
            "specs/testing-contract.md",
            "README-testing.md",
        ):
            self.assertNotIn(documentary, data["automation"]["test_configs"])

    def test_exit_codes_and_schema_version(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--schema-version"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "2")
        result = subprocess.run([sys.executable, str(SCRIPT), ".", "--pretty"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 3)
        missing = Path(tempfile.mkdtemp(prefix="repo-readiness-missing-")) / "none"
        result = self.run_scan(missing)
        self.assertEqual(result.returncode, 2)

    def test_exclude_path_requires_root_relative_literal_path(self):
        for excluded in ("/tmp/outside", "../outside", "src/../../outside"):
            with self.subTest(excluded=excluded), redirect_stderr(StringIO()), self.assertRaises(SystemExit):
                repo_inventory.parser().parse_args([".", "--exclude-path", excluded])

    def test_timeout_is_bounded(self):
        root = self.make_repo()
        (root / "README.md").write_text("readme\n", encoding="utf-8")
        result = self.run_scan(root, "--timeout-seconds", "0.000001")
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertTrue(data["limits"]["timeout_reached"])


if __name__ == "__main__":
    unittest.main()
