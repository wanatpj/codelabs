from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from lib.execution import CppTaskExecutor, ResultCollector
from lib.models import RunConfig, integer, record
from lib.storage import RunStore

ROOT = Path(__file__).resolve().parents[1]


class CodelabTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="monte carlo ")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.executor = CppTaskExecutor()
        self.collector = ResultCollector()

    def cli(self, *args: object, success: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(ROOT / "cli.py"), *map(str, args)],
            text=True, capture_output=True,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def launch(self, directory: Path, workers: int = 4,
               dry: bool = True) -> subprocess.CompletedProcess[str]:
        args: list[object] = ["submit", "--run-dir", directory,
                              "--samples", 100_003, "--tasks", 7, "--workers", workers]
        if dry:
            args.append("--dry-run")
        return self.cli(*args)

    def worker(self, run: Path, index: int,
               success: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, "-m", "lib.worker", str(run)],
            cwd=ROOT, env={**os.environ, "LSB_JOBINDEX": str(index)},
            text=True, capture_output=True,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def summary(self, directory: Path) -> dict[str, object]:
        return record(RunStore(directory).read_json("summary.json"))

    def complete(self, directory: Path) -> subprocess.CompletedProcess[str]:
        self.launch(directory)
        store = RunStore(directory)
        for task in store.load_manifest().tasks:
            self.executor.execute(store, task.index)
        return self.cli("collect", "--run-dir", directory)

    def test_partition_and_retry_preserve_the_same_results(self) -> None:
        run = self.directory / "run"
        response = self.complete(run)
        summary = self.summary(run)
        self.assertEqual(integer(summary, "samples"), 100_003)
        estimate = summary["pi_estimate"]
        assert isinstance(estimate, float)
        self.assertLess(abs(estimate - 3.141592653589793), 0.04)
        event = record(json.loads(response.stderr))
        self.assertEqual(event["event"], "results_collected")
        self.assertEqual(event["level"], "info")
        self.assertEqual(response.stdout, "")
        self.worker(run, 1)
        self.assertFalse((run / "summary.json").exists())
        self.cli("collect", "--run-dir", run)
        self.assertEqual(summary, self.summary(run))

    def test_generated_lsf_payload_matches_task_inputs_without_a_scheduler(self) -> None:
        reference, array = self.directory / "reference", self.directory / "array with spaces"
        self.complete(reference)
        prepared = self.launch(array)
        self.assertEqual(record(json.loads(prepared.stderr))["event"], "prepared")
        submission = record(RunStore(array).read_json("submission.json"))
        argv = submission["argv"]
        assert isinstance(argv, list)
        self.assertIn("monte_carlo[1-7]%4", argv)
        self.assertIn(sys.executable, (array / "array.sh").read_text())
        for index in range(1, 8):
            completed = subprocess.run(
                ["sh", str(array / "array.sh")],
                env={**os.environ, "LSB_JOBINDEX": str(index)},
                text=True, capture_output=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
        self.cli("collect", "--run-dir", array)
        self.assertEqual(self.summary(reference), self.summary(array))

    def test_missing_and_invalid_results_remove_previous_summary(self) -> None:
        run = self.directory / "run"
        self.complete(run)
        path = run / "results" / "1.json"
        result = record(json.loads(path.read_text()))
        path.unlink()
        failure = self.cli("collect", "--run-dir", run, success=False)
        self.assertIn("Missing task results", failure.stderr)
        self.assertFalse((run / "summary.json").exists())
        self.worker(run, 1)
        self.cli("collect", "--run-dir", run)
        result["seed"] = integer(result, "seed") + 1
        path.write_text(json.dumps(result))
        self.cli("collect", "--run-dir", run, success=False)
        self.assertFalse((run / "summary.json").exists())

    def test_original_worker_can_change_without_changing_a_saved_run(self) -> None:
        source = self.directory / "source-worker"
        shutil.copyfile(ROOT / "job" / "build" / "monte_carlo", source)
        source.chmod(0o755)
        store = RunStore(self.directory / "snapshot-run")
        manifest = store.create(RunConfig(samples=100_000, task_count=2), source)
        first = self.executor.execute(store, 1)
        shutil.copyfile("/bin/false", source)
        second = self.executor.execute(store, 2)
        self.assertEqual(first.worker_sha256, second.worker_sha256)
        self.assertNotEqual(store.checksum(source), manifest.worker_sha256)
        self.assertEqual(self.collector.collect(store).samples, 100_000)

    def test_tampered_snapshot_fails_before_reusing_a_previous_result(self) -> None:
        run = self.directory / "tampered"
        self.complete(run)
        snapshot = run / "worker"
        snapshot.chmod(0o755)
        shutil.copyfile("/bin/false", snapshot)
        failure = self.worker(run, 1, success=False)
        self.assertIn("checksum mismatch", failure.stderr)
        self.assertFalse((run / "summary.json").exists())
        self.assertFalse((run / "results" / "1.json").exists())

    def test_failed_retry_removes_old_result_and_summary(self) -> None:
        run = self.directory / "retry"
        self.complete(run)
        store = RunStore(run)
        # Simulate a runtime failure of the unchanged worker (e.g. a missing input).
        with patch("lib.execution.subprocess.run", return_value=
                   subprocess.CompletedProcess([], 1, stdout="", stderr="missing input")):
            with self.assertRaisesRegex(RuntimeError, "Task 1 failed"):
                self.executor.execute(store, 1)
        self.assertFalse((run / "results" / "1.json").exists())
        self.assertFalse((run / "summary.json").exists())
        self.executor.execute(store, 1)
        self.assertEqual(self.collector.collect(store).samples, 100_003)

    def test_malformed_worker_json_is_a_structured_error(self) -> None:
        run = self.directory / "malformed"
        self.launch(run, dry=True)
        store = RunStore(run)
        with patch("lib.execution.subprocess.run", return_value=
                   subprocess.CompletedProcess([], 0, stdout="[]", stderr="")):
            with self.assertRaisesRegex(ValueError, "Expected a JSON object"):
                self.executor.execute(store, 1)
        self.assertFalse((run / "results" / "1.json").exists())

    def test_invalid_input_and_existing_run_directory_are_rejected(self) -> None:
        run = self.directory / "invalid"
        self.cli("submit", "--dry-run", "--run-dir", run,
                 "--samples", 2, "--tasks", 3, success=False)
        self.assertFalse(run.exists())
        self.launch(run)
        existing = self.cli("submit", "--dry-run", "--run-dir", run, success=False)
        self.assertIn("File exists", existing.stderr)
        error = record(json.loads(existing.stderr))
        self.assertEqual(error["event"], "operation_failed")

    def test_failed_cpp_worker_does_not_publish_a_result(self) -> None:
        store = RunStore(self.directory / "failed")
        store.create(RunConfig(samples=10, task_count=1), Path("/bin/false"))
        with self.assertRaisesRegex(RuntimeError, "Task 1 failed"):
            self.executor.execute(store, 1)
        self.assertFalse((store.directory / "results" / "1.json").exists())

    def test_lsf_submission_sends_script_and_records_job_id(self) -> None:
        fake_bin = self.directory / "bin"
        fake_bin.mkdir()
        received = self.directory / "received.sh"
        bsub = fake_bin / "bsub"
        bsub.write_text(
            f"#!{sys.executable}\nimport pathlib, sys\n"
            f"pathlib.Path({str(received)!r}).write_text(sys.stdin.read())\n"
            "sys.stdout.write('Job <12345> is submitted to queue <normal>.\\n')\n")
        bsub.chmod(0o755)
        run = self.directory / "submitted"
        with patch.dict(os.environ, {"PATH": str(fake_bin) + os.pathsep + os.environ["PATH"]}):
            response = self.launch(run, dry=False)
        self.assertEqual((run / "job_id.txt").read_text(), "12345\n")
        self.assertEqual(received.read_text(), (run / "array.sh").read_text())
        self.assertEqual(record(json.loads(response.stderr))["event"], "submitted")


if __name__ == "__main__":
    unittest.main()
