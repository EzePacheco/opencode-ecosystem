import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "workspace_inventory.py"
REPO_SCRIPT = Path(__file__).parents[1] / "scripts" / "repo_inventory.py"


class WorkspaceInventoryTests(unittest.TestCase):
    def run_discovery(self, path: Path, *args: str):
        return subprocess.run([sys.executable, str(SCRIPT), str(path), "--json", *args], text=True, capture_output=True)

    def make_repo(self, path: Path) -> Path:
        path.mkdir(parents=True)
        subprocess.run(["git", "init", "--quiet", str(path)], check=True)
        subprocess.run(["git", "-C", str(path), "config", "user.name", "Workspace Test"], check=True)
        subprocess.run(["git", "-C", str(path), "config", "user.email", "workspace@example.test"], check=True)
        (path / "tracked.txt").write_text("content\n")
        subprocess.run(["git", "-C", str(path), "add", "tracked.txt"], check=True)
        subprocess.run(["git", "-C", str(path), "commit", "--quiet", "-m", "fixture"], check=True)
        return path

    def repositories(self, data):
        return [checkout for repo in data["repositories"] for checkout in repo["checkouts"]]

    def test_path_inside_git_resolves_current_repository(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = self.make_repo(Path(temp) / "repo")
            nested = repo / "src"
            nested.mkdir()
            data = json.loads(self.run_discovery(nested).stdout)
            self.assertTrue(data["is_git_repository"])
            self.assertEqual(self.repositories(data)[0]["git_root"], str(repo))

    def test_workspace_two_repositories_and_irrelevant_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            self.make_repo(workspace / "repo-b")
            self.make_repo(workspace / "repo-a")
            (workspace / "notes" / "nested").mkdir(parents=True)
            data = json.loads(self.run_discovery(workspace).stdout)
            self.assertFalse(data["is_git_repository"])
            self.assertEqual([x["relative_path"] for x in self.repositories(data)], ["repo-a", "repo-b"])

    def test_worktree_shares_repository_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            repo = self.make_repo(workspace / "project")
            subprocess.run(["git", "-C", str(repo), "worktree", "add", "--quiet", "-b", "feature", str(workspace / "project-feature")], check=True)
            data = json.loads(self.run_discovery(workspace).stdout)
            self.assertEqual(len(data["repositories"]), 1)
            checkouts = data["repositories"][0]["checkouts"]
            self.assertEqual(len(checkouts), 2)
            self.assertTrue(any(item["is_worktree"] for item in checkouts))
            self.assertEqual(len({item["git_common_dir"] for item in checkouts}), 1)

    def test_depth_boundary_and_reporting(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            self.make_repo(workspace / "level-one")
            (workspace / "outer").mkdir()
            self.make_repo(workspace / "outer" / "level-two")
            (workspace / "one" / "two" / "three").mkdir(parents=True)
            self.make_repo(workspace / "one" / "two" / "three" / "too-deep")
            data = json.loads(self.run_discovery(workspace).stdout)
            roots = {x["relative_path"] for x in self.repositories(data)}
            self.assertIn("level-one", roots)
            self.assertIn("outer/level-two", roots)
            self.assertNotIn("one/two/three/too-deep", roots)
            self.assertTrue(data["limits"]["depth_limit_reached"])

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            external = Path(tempfile.mkdtemp())
            self.make_repo(external / "outside")
            (workspace / "linked").symlink_to(external / "outside", target_is_directory=True)
            data = json.loads(self.run_discovery(workspace).stdout)
            self.assertEqual(self.repositories(data), [])

    def test_order_stable_and_no_fetch(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            self.make_repo(workspace / "zeta")
            self.make_repo(workspace / "alpha")
            subprocess.run(["git", "-C", str(workspace / "alpha"), "remote", "add", "origin", "file:///no-such-remote"], check=True)
            for _ in range(2):
                result = self.run_discovery(workspace)
                self.assertEqual(result.returncode, 0)
                data = json.loads(result.stdout)
                self.assertEqual([x["relative_path"] for x in self.repositories(data)], ["alpha", "zeta"])
                self.assertFalse(result.stderr)

    def test_invalid_input_is_nonzero_and_partial_scan_is_success(self):
        missing = Path(tempfile.gettempdir()) / "workspace-inventory-does-not-exist"
        self.assertNotEqual(self.run_discovery(missing).returncode, 0)
        with tempfile.TemporaryDirectory() as temp:
            repo = self.make_repo(Path(temp) / "repo")
            (repo / ".env").write_text("secret=value\n")
            result = subprocess.run([sys.executable, str(REPO_SCRIPT), str(repo), "--json", "--max-files", "0"], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0)
            data = json.loads(result.stdout)
            self.assertTrue(data["warnings"] or any(data["limits"].values()))

    def test_sensitive_path_warning_keeps_valid_json_and_zero_exit(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = self.make_repo(Path(temp) / "repo")
            (repo / ".env").write_text("secret=value\n")
            result = subprocess.run([sys.executable, str(REPO_SCRIPT), str(repo), "--json"], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0)
            data = json.loads(result.stdout)
            self.assertTrue(data["warnings"])


if __name__ == "__main__":
    unittest.main()
