"""Run artifacts, executable snapshots, and synchronized result publication."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Iterator

from lib.models import Manifest, RunConfig, TaskResult


class RunStore:
    def __init__(self, directory: Path) -> None:
        self.directory = directory.resolve()

    @staticmethod
    def checksum(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    def create(self, config: RunConfig, source: Path) -> Manifest:
        tasks = config.partition()
        source = source.resolve()
        if not source.is_file() or not os.access(source, os.X_OK):
            raise ValueError(f"Worker is not executable: {source}; run make first")
        self.directory.mkdir(parents=True, exist_ok=False)
        (self.directory / "results").mkdir()
        (self.directory / "logs").mkdir()
        snapshot = self.directory / "worker"
        shutil.copyfile(source, snapshot)
        snapshot.chmod(0o555)
        manifest = Manifest(str(snapshot), self.checksum(snapshot), tasks, config.samples)
        self.write_json("manifest.json", asdict(manifest))
        return manifest

    def load_manifest(self) -> Manifest:
        manifest = Manifest.from_json(self.read_json("manifest.json"))
        if Path(manifest.binary) != self.directory / "worker":
            raise ValueError("Manifest must refer to this run's worker snapshot")
        return manifest

    def verify_worker(self, manifest: Manifest) -> None:
        if self.checksum(Path(manifest.binary)) != manifest.worker_sha256:
            raise ValueError("Worker snapshot checksum mismatch; prepare a new run")

    def read_json(self, filename: str) -> object:
        with (self.directory / filename).open() as source:
            value: object = json.load(source)
        return value

    def write_json(self, filename: str, value: object) -> None:
        path = self.directory / filename
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as out:
                temporary = Path(out.name)
                json.dump(value, out, indent=2)
                out.write("\n")
            os.replace(temporary, path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    @contextmanager
    def locked(self) -> Iterator[None]:
        with (self.directory / ".lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def invalidate_summary(self) -> None:
        """Caller holds the run lock when results or summary can change."""
        (self.directory / "summary.json").unlink(missing_ok=True)

    def begin_task(self, index: int) -> None:
        with self.locked():
            self.invalidate_summary()
            # A failed retry must not leave an earlier success looking current.
            (self.directory / "results" / f"{index}.json").unlink(missing_ok=True)

    def publish(self, result: TaskResult) -> None:
        with self.locked():
            self.invalidate_summary()
            self.write_json(f"results/{result.index}.json", asdict(result))
