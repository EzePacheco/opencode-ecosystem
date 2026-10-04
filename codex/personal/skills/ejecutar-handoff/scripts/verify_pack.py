#!/usr/bin/env python3
"""Read-only verification of an explicitly supplied JSON manifest and pack.

Manifest format: {"files": [{"path": "relative/file", "sha256": "64 hex chars"}]}.
The manifest itself is allowed inside the root but must not list itself.
Optional ZIP must contain exactly the same files plus the manifest, under prefix.
No extraction, repair, network, authority inference or semantic contract validation.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import stat
import zipfile


def digest(stream):
    h = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        h.update(block)
    return h.hexdigest()


def verify(root, manifest, archive=None, prefix=""):
    root = Path(root).resolve(strict=True)
    manifest = Path(manifest).absolute()
    if not root.is_dir() or manifest.is_symlink():
        raise ValueError("root must be a directory and manifest must not be a symlink")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("files"), list):
        raise ValueError("manifest must declare files as a list")
    expected = {}
    for entry in data["files"]:
        if not isinstance(entry, dict):
            raise ValueError("file entries must be objects")
        name, sha = entry.get("path"), entry.get("sha256")
        if not isinstance(name, str) or not name or "\\" in name:
            raise ValueError("paths must be nonempty relative POSIX paths")
        path = PurePosixPath(name)
        if path.is_absolute() or path.as_posix() != name or any(x in (".", "..") for x in path.parts):
            raise ValueError("path is absolute, ambiguous or escapes root")
        if name in expected or not isinstance(sha, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", sha):
            raise ValueError("duplicate path or invalid SHA256")
        expected[name] = sha.lower()
    actual = {}
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError("pack contains a symlink")
        if path.is_file():
            actual[path.relative_to(root).as_posix()] = path
    manifest_name = None
    if manifest.is_relative_to(root):
        manifest_name = manifest.relative_to(root).as_posix()
        if manifest_name in expected:
            raise ValueError("manifest must not list itself")
    allowed = set(expected) | ({manifest_name} if manifest_name else set())
    if set(actual) != allowed:
        raise ValueError(f"inventory differs: missing={sorted(allowed-set(actual))}, extra={sorted(set(actual)-allowed)}")
    hashes = {}
    for name, path in actual.items():
        with path.open("rb") as stream:
            hashes[name] = digest(stream)
        if name in expected and hashes[name] != expected[name]:
            raise ValueError(f"hash mismatch: {name}")
    if archive is not None:
        if prefix and (not prefix.endswith("/") or PurePosixPath(prefix).is_absolute() or ".." in PurePosixPath(prefix).parts or "\\" in prefix):
            raise ValueError("ZIP prefix must be relative and end with /")
        with zipfile.ZipFile(archive) as zipped:
            if any(stat.S_ISLNK(entry.external_attr >> 16) for entry in zipped.infolist()):
                raise ValueError("ZIP contains a symlink entry")
            names = zipped.namelist()
            if len(names) != len(set(names)) or set(names) != {prefix+n for n in allowed}:
                raise ValueError("ZIP inventory differs or contains duplicate entries")
            for name, sha in hashes.items():
                with zipped.open(prefix+name) as stream:
                    if digest(stream) != sha:
                        raise ValueError(f"ZIP hash mismatch: {name}")
    return {"status": "PASS", "declared_files": len(expected), "root_files": len(actual), "zip_checked": archive is not None, "scope": "inventory and bytes only; manifest authority and semantics not verified"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="authorized pack directory")
    parser.add_argument("manifest", help="explicit manifest JSON")
    parser.add_argument("--zip", dest="archive", help="optional ZIP, read without extraction")
    parser.add_argument("--zip-prefix", default="", help="e.g. PERSONAL/")
    args = parser.parse_args()
    try:
        result = verify(args.root, args.manifest, args.archive, args.zip_prefix)
    except (ValueError, OSError, zipfile.BadZipFile, RuntimeError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
