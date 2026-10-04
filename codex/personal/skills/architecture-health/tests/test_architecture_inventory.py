from __future__ import annotations

import importlib.util
from contextlib import redirect_stderr
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "architecture_inventory.py"
SPEC = importlib.util.spec_from_file_location("architecture_inventory", SCRIPT)
assert SPEC and SPEC.loader
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode() if isinstance(content, str) else content)

    def scan(self, *args):
        run = subprocess.run([sys.executable, str(SCRIPT), str(self.root), "--json", *args], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        return json.loads(run.stdout)

    def commit(self, message="one"):
        self.git("-c", "user.name=A", "-c", "user.email=a@example.test", "commit", "-qm", message)

    def test_tracked_untracked_ignored_and_no_history(self):
        self.write(".gitignore", "dist/\nnode_modules/\nbuild/\n")
        self.write("src/a.py", "a = 1\n")
        self.git("add", ".gitignore", "src/a.py")
        self.write("src/b.py", "b = 2\n")
        self.write("dist/generated.py", "x = 3\n")
        self.write("node_modules/vendor.js", "x = 3\n")
        self.write("build/artifact.py", "x = 3\n")
        data = self.scan()
        self.assertFalse(data["history"]["available"])
        self.assertEqual([(x["path"], x["tracked"]) for x in data["largest_source"]],
                         [("src/a.py", True), ("src/b.py", False)])
        self.assertEqual(data["counts"]["source"], 2)
        self.assertEqual(data["highest_churn"], [])

    def test_path_scope_reads_only_selected_source_paths(self):
        self.write("app/orders/domain/policy.py", "rule = 'synthetic'\n")
        self.write("app/users/domain/policy.py", "rule = 'synthetic'\n")
        args = inventory.parser().parse_args([str(self.root), "--path", "app/orders"])
        scanner = inventory.Inventory(self.root, args)
        opened = []
        original_open = Path.open

        def guarded_open(path, *open_args, **open_kwargs):
            if path.is_relative_to(self.root):
                opened.append(path.relative_to(self.root).as_posix())
                if not path.relative_to(self.root).as_posix().startswith("app/orders/"):
                    raise AssertionError(f"source outside selected path opened: {path.name}")
            return original_open(path, *open_args, **open_kwargs)

        with patch.object(Path, "open", guarded_open):
            data = scanner.run()
        self.assertEqual(opened, ["app/orders/domain/policy.py"])
        self.assertEqual(data["counts"]["source"], 1)
        self.assertEqual(data["scan_scope"]["paths"], ["app/orders"])

    def test_metadata_only_never_opens_file_bodies(self):
        self.write("src/policy.py", "rule = 'synthetic'\n")
        self.write("tests/test_policy.py", "assert True\n")
        self.write("README.md", "Synthetic architecture notes\n")
        self.write("pyproject.toml", "[project]\nname='synthetic'\n")
        self.git("add", "src/policy.py", "tests/test_policy.py", "README.md", "pyproject.toml")
        self.commit("metadata fixture")
        args = inventory.parser().parse_args([str(self.root), "--metadata-only"])
        scanner = inventory.Inventory(self.root, args)
        original_open = Path.open

        def forbidden_open(path, *open_args, **open_kwargs):
            if path.is_relative_to(self.root):
                raise AssertionError(f"metadata-only opened file body: {path.name}")
            return original_open(path, *open_args, **open_kwargs)

        with patch.object(Path, "open", forbidden_open):
            data = scanner.run()
        self.assertEqual(data["limits"]["bytes_processed"], 0)
        self.assertEqual(data["largest_source"], [])
        self.assertEqual(data["generated_source_examples"], [])
        self.assertEqual({item["path"] for item in data["source_metadata"]}, {"src/policy.py", "tests/test_policy.py"})
        self.assertEqual(data["scan_scope"]["paths"], ["."])
        self.assertIn("LOC-based size ranking", data["scan_scope"]["signals_unavailable"])
        self.assertTrue(data["history"]["available"])

    def test_path_scope_rejects_absolute_and_parent_traversal(self):
        for scope in ("/tmp/private", "../outside", "src/../../outside"):
            with self.subTest(scope=scope), redirect_stderr(StringIO()), self.assertRaises(SystemExit):
                inventory.parser().parse_args([str(self.root), "--path", scope])

    def test_largest_loc_binary_generated_tests_context_and_order(self):
        self.write("src/z.py", "a\nb\nc")
        self.write("src/a.py", "a\nb\nc")
        self.write("src/empty.py", "")
        self.write("src/bin.py", b"a\0b")
        self.write("src/image.png", b"\x89PNG")
        self.write("generated/code.py", "a\nb\nc\nd\n")
        self.write("tests/test_a.py", "assert True\n")
        self.write("AGENTS.md", "instructions")
        self.write("docs/architecture.md", "architecture")
        self.write("docs/adr/001.md", "decision")
        self.write("pyproject.toml", "[project]")
        data = self.scan()
        self.assertEqual(data["largest_source"][0]["path"], "src/a.py")
        self.assertEqual(data["largest_source"][0]["loc"], 3)
        self.assertEqual(data["largest_source"][1]["path"], "src/z.py")
        self.assertEqual(data["counts"]["source_unanalyzed"], 1)
        self.assertEqual(data["generated_source_examples"][0]["path"], "generated/code.py")
        self.assertEqual(data["test_hints"][0]["related_path_hints"], ["src/a.py"])
        self.assertEqual({x["kind"] for x in data["context_paths"]},
                         {"agents", "architecture_or_readme", "decision", "manifest"})
        self.assertEqual(data["layout"]["manifest_module_roots"], ["."])
        self.assertEqual(data, self.scan())

    def test_bounded_top_n_and_file_limit_are_recoverable(self):
        for index in range(5):
            self.write(f"src/{index}.py", "line\n" * (index + 1))
        data = self.scan("--max-hotspots", "2", "--max-files", "3")
        self.assertEqual(data["limits"]["files_enumerated"], 3)
        self.assertIn("max_files", data["limits"]["reached"])
        self.assertTrue(data["warnings"])
        self.assertLessEqual(len(data["largest_source"]), 2)
        self.assertLessEqual(len(data["hotspot_hints"]), 2)

    def test_history_churn_and_author_counts(self):
        self.write("a.py", "one\n")
        self.git("add", "a.py")
        self.commit()
        self.write("a.py", "one\ntwo\n")
        self.git("add", "a.py")
        self.commit("two")
        data = self.scan("--max-history-commits", "2")
        self.assertTrue(data["history"]["available"])
        self.assertEqual(data["history"]["commits_inspected"], 2)
        self.assertEqual(data["highest_churn"][0]["history"], {"commits": 2, "authors": 1})
        self.assertIn("top_churn", data["hotspot_hints"][0]["signals"])
        self.assertNotIn("high_churn", data["hotspot_hints"][0]["signals"])
        self.assertNotIn("max_history_commits", data["limits"]["reached"])
        self.write("a.py", "one\ntwo\nthree\n")
        self.git("add", "a.py")
        self.commit("three")
        capped = self.scan("--max-history-commits", "2")
        self.assertIn("max_history_commits", capped["limits"]["reached"])
        self.assertEqual(capped["highest_churn"][0]["history"]["commits"], 2)

    def test_source_bytes_and_source_count_limits(self):
        self.write("a.py", "a\n")
        self.write("b.py", "b\n")
        data = self.scan("--max-source-files", "1", "--max-total-bytes", "2")
        self.assertEqual(data["counts"]["source"], 1)
        self.assertIn("max_source_files", data["limits"]["reached"])
        data = self.scan("--max-file-bytes", "1")
        self.assertEqual(data["counts"]["source"], 0)
        self.assertIn("max_file_bytes", data["limits"]["reached"])

    def test_large_source_is_only_a_mechanical_hint(self):
        self.write("large.py", "line\n" * 1001)
        data = self.scan()
        self.assertEqual(data["largest_source"][0]["loc"], 1001)
        self.assertIn("large", data["hotspot_hints"][0]["signals"])
        self.assertNotIn("god_file", json.dumps(data))

    def test_timeout_is_recoverable_json(self):
        args = inventory.parser().parse_args([str(self.root), "--timeout-seconds", "1"])
        scanner = inventory.Inventory(self.root, args)
        scanner.started = time.monotonic() - 2
        with patch.object(scanner, "file_paths", return_value=[("a.py", False)]):
            data = scanner.run()
        self.assertIn("timeout_seconds", data["limits"]["reached"])
        self.assertTrue(data["warnings"])
        json.dumps(data)

    def test_invalid_input_fails(self):
        bad = subprocess.run([sys.executable, str(SCRIPT), str(self.root), "--max-files", "0", "--json"], capture_output=True)
        self.assertNotEqual(bad.returncode, 0)
        with tempfile.TemporaryDirectory() as outside:
            bad = subprocess.run([sys.executable, str(SCRIPT), outside, "--json"], capture_output=True)
            self.assertNotEqual(bad.returncode, 0)

    def test_no_network_or_writes(self):
        self.write("a.py", "value = 1\n")
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        args = inventory.parser().parse_args([str(self.root)])
        commands = []
        original_popen = subprocess.Popen

        def guarded_popen(command, *positional, **keywords):
            commands.append(command)
            self.assertEqual(command[0], "git")
            self.assertNotIn("fetch", command)
            self.assertNotIn("push", command)
            return original_popen(command, *positional, **keywords)

        with patch.object(inventory.subprocess, "Popen", side_effect=guarded_popen):
            data = inventory.Inventory(self.root, args).run()
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertTrue(commands)
        self.assertIn("no fetch", data["history"]["scope"])


if __name__ == "__main__":
    unittest.main()
