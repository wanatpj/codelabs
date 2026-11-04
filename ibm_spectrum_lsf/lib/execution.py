"""Execute one task and aggregate a complete run."""

from __future__ import annotations

from dataclasses import asdict
import json
import socket
import subprocess
import time

from lib.models import Summary, TaskResult, integer, record
from lib.storage import RunStore


class CppTaskExecutor:
    def execute(self, store: RunStore, index: int) -> TaskResult:
        manifest = store.load_manifest()
        task = manifest.task(index)
        store.begin_task(index)
        store.verify_worker(manifest)
        started = time.perf_counter()
        completed = subprocess.run(
            [manifest.binary, str(task.samples), str(task.seed)],
            capture_output=True, text=True,
        )
        (store.directory / "logs" / f"worker-{index}.stderr").write_text(completed.stderr)
        if completed.returncode:
            raise RuntimeError(f"Task {index} failed: {completed.stderr.strip()}")
        data = record(json.loads(completed.stdout))
        result = TaskResult(index, integer(data, "samples"), integer(data, "seed"),
                            integer(data, "hits"), socket.gethostname(),
                            time.perf_counter() - started, manifest.worker_sha256)
        result.validate(task, manifest.worker_sha256)
        store.verify_worker(manifest)
        store.publish(result)
        return result


class ResultCollector:
    def collect(self, store: RunStore) -> Summary:
        # Serialize collection with result invalidation/publication across processes.
        with store.locked():
            store.invalidate_summary()
            manifest = store.load_manifest()
            store.verify_worker(manifest)
            results: list[TaskResult] = []
            missing: list[int] = []
            for task in manifest.tasks:
                filename = f"results/{task.index}.json"
                if not (store.directory / filename).exists():
                    missing.append(task.index)
                    continue
                result = TaskResult.from_json(store.read_json(filename))
                result.validate(task, manifest.worker_sha256)
                results.append(result)
            if missing:
                raise RuntimeError(f"Missing task results: {missing}. Check logs and scheduler status.")
            summary = Summary.from_results(results)
            store.write_json("summary.json", asdict(summary))
            return summary
