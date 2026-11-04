"""Prepare and submit an LSF job array."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum, auto
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

from lib.models import Manifest
from lib.storage import RunStore


class DispatchState(StrEnum):
    PREPARED = auto()
    SUBMITTED = auto()


@dataclass(frozen=True)
class DispatchReceipt:
    state: DispatchState
    command: str
    job_id: str | None = None


@dataclass(frozen=True)
class LsfOptions:
    workers: int
    python: str = sys.executable
    queue: str | None = None
    project: str | None = None
    walltime: str = "00:10"


class LsfDispatcher:
    def __init__(self, options: LsfOptions) -> None:
        self.options = options

    def dispatch(self, store: RunStore, manifest: Manifest, dry_run: bool) -> DispatchReceipt:
        if not dry_run and shutil.which("bsub") is None:
            raise ValueError("bsub is unavailable; use --dry-run or an LSF submission host")
        script = store.directory / "array.sh"
        script.write_text(
            "#!/bin/sh\nset -eu\n"
            f"cd {shlex.quote(str(Path(__file__).resolve().parents[1]))}\n"
            f"exec {shlex.quote(self.options.python)} -m lib.worker "
            f"{shlex.quote(str(store.directory))}\n"
        )
        argv = ["bsub", "-J", f"monte_carlo[1-{len(manifest.tasks)}]%{self.options.workers}",
                "-n", "1", "-W", self.options.walltime,
                "-o", str(store.directory / "logs" / "%J.%I.out"),
                "-e", str(store.directory / "logs" / "%J.%I.err")]
        if self.options.queue:
            argv += ["-q", self.options.queue]
        if self.options.project:
            argv += ["-P", self.options.project]
        command = f"{shlex.join(argv)} < {shlex.quote(str(script))}"
        store.write_json("submission.json", {"argv": argv, "stdin": str(script)})
        if dry_run:
            return DispatchReceipt(DispatchState.PREPARED, command)
        with script.open() as stdin:
            result = subprocess.run(argv, stdin=stdin, capture_output=True, text=True,
                                    env={**os.environ, "LC_ALL": "C"})
        (store.directory / "submission.log").write_text(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError(f"bsub failed: {result.stderr.strip()}; see submission.log")
        match = re.search(r"Job <(\d+)>", result.stdout)
        job_id = match[1] if match else None
        if job_id:
            (store.directory / "job_id.txt").write_text(job_id + "\n")
        return DispatchReceipt(DispatchState.SUBMITTED, command, job_id)
