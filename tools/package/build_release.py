#!/usr/bin/env python3
"""Build deterministic ARGUS Intelligence repository snapshots."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import stat
import subprocess
import sys
import tarfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import yaml


def _run(command: list[str], cwd: Path) -> str:
    completed = subprocess.run(command, cwd=cwd, check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tracked_files(root: Path) -> list[Path]:
    output = _run(["git", "ls-files", "-z"], root)
    return sorted(root / name for name in output.split("\0") if name)


def _assert_clean(root: Path) -> None:
    changes = _run(["git", "status", "--porcelain", "--untracked-files=no"], root)
    if changes:
        raise RuntimeError("tracked files are dirty; commit intended source before packaging")


def _payload(root: Path, files: list[Path]) -> list[dict[str, object]]:
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
            "sha256": _sha256(path),
        }
        for path in files
    ]


def _build_tar(root: Path, output: Path, prefix: str, files: list[Path], epoch: int) -> None:
    with output.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for path in files:
                    relative = path.relative_to(root).as_posix()
                    info = archive.gettarinfo(str(path), arcname=f"{prefix}/{relative}")
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    info.mtime = epoch
                    with path.open("rb") as handle:
                        archive.addfile(info, handle)


def _build_zip(root: Path, output: Path, prefix: str, files: list[Path], epoch: int) -> None:
    moment = datetime.fromtimestamp(max(epoch, 315532800), tz=UTC)
    stamp = (moment.year, moment.month, moment.day, moment.hour, moment.minute, moment.second)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(f"{prefix}/{relative}", stamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = stat.S_IFREG | (0o755 if os.access(path, os.X_OK) else 0o644)
            info.external_attr = mode << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build(root: Path, output_dir: Path) -> list[Path]:
    root = root.resolve()
    output_dir = (root / output_dir).resolve() if not output_dir.is_absolute() else output_dir.resolve()
    _assert_clean(root)

    manifest = yaml.safe_load((root / "argus-intelligence.yaml").read_text(encoding="utf-8"))
    product = manifest["product"]
    version = str(product["version"])
    status = str(product["status"])
    commit = _run(["git", "rev-parse", "HEAD"], root)
    epoch = int(_run(["git", "show", "-s", "--format=%ct", "HEAD"], root))
    files = _tracked_files(root)
    output_dir.mkdir(parents=True, exist_ok=True)

    prefix = f"argus-intelligence-{version}"
    tar_path = output_dir / f"{prefix}.tar.gz"
    zip_path = output_dir / f"{prefix}.zip"
    manifest_path = output_dir / f"{prefix}.manifest.json"
    checksums_path = output_dir / "SHA256SUMS"

    _build_tar(root, tar_path, prefix, files, epoch)
    _build_zip(root, zip_path, prefix, files, epoch)
    release_manifest = {
        "product": "argus-intelligence",
        "version": version,
        "status": status,
        "source_commit": commit,
        "source_date_epoch": epoch,
        "payload": _payload(root, files),
        "artifacts": [
            {"name": tar_path.name, "sha256": _sha256(tar_path)},
            {"name": zip_path.name, "sha256": _sha256(zip_path)},
        ],
    }
    manifest_path.write_text(json.dumps(release_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checksum_targets = [tar_path, zip_path, manifest_path]
    checksums_path.write_text(
        "".join(f"{_sha256(path)}  {path.name}\n" for path in checksum_targets), encoding="utf-8"
    )
    return [tar_path, zip_path, manifest_path, checksums_path]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("output", nargs="?", default="dist", type=Path)
    args = parser.parse_args(argv)
    try:
        outputs = build(args.root, args.output)
    except (RuntimeError, subprocess.CalledProcessError, KeyError, OSError) as exc:
        print(f"ARGUS snapshot build FAILED: {exc}", file=sys.stderr)
        return 1
    for output in outputs:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
