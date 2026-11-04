"""Validated, immutable data shared by execution and dispatch."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import cast

UINT64_MAX = 2**64 - 1


def record(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ValueError("Expected a JSON object")
    return cast(dict[str, object], value)


def integer(data: dict[str, object], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{key} must be an integer")
    return value


def string(data: dict[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a nonempty string")
    return value


@dataclass(frozen=True)
class TaskSpec:
    index: int
    samples: int
    seed: int

    @classmethod
    def from_json(cls, value: object) -> TaskSpec:
        data = record(value)
        task = cls(integer(data, "index"), integer(data, "samples"), integer(data, "seed"))
        if task.index < 1 or not 1 <= task.samples <= UINT64_MAX or not 0 <= task.seed <= UINT64_MAX:
            raise ValueError("Invalid task index, sample count, or seed")
        return task


@dataclass(frozen=True)
class RunConfig:
    samples: int = 1_000_000
    task_count: int = 8
    seed: int = 42

    def __post_init__(self) -> None:
        if not 1 <= self.samples <= UINT64_MAX:
            raise ValueError("samples must be in [1, 2^64-1]")
        if not 1 <= self.task_count <= self.samples:
            raise ValueError("tasks must be positive and no greater than samples")
        if not 0 <= self.seed <= UINT64_MAX - self.task_count + 1:
            raise ValueError("seed range would exceed uint64")

    def partition(self) -> tuple[TaskSpec, ...]:
        quotient, remainder = divmod(self.samples, self.task_count)
        return tuple(TaskSpec(i + 1, quotient + (i < remainder), self.seed + i)
                     for i in range(self.task_count))


@dataclass(frozen=True)
class Manifest:
    binary: str
    worker_sha256: str
    tasks: tuple[TaskSpec, ...]
    total_samples: int
    schema_version: int = 1

    @classmethod
    def from_json(cls, value: object) -> Manifest:
        data = record(value)
        if data.get("schema_version") != 1:
            raise ValueError("Unsupported manifest schema; prepare a new run")
        raw_tasks = data.get("tasks")
        if not isinstance(raw_tasks, list) or not raw_tasks:
            raise ValueError("Manifest must contain tasks")
        tasks = tuple(TaskSpec.from_json(task) for task in raw_tasks)
        manifest = cls(string(data, "binary"), string(data, "worker_sha256"),
                       tasks, integer(data, "total_samples"))
        if [task.index for task in tasks] != list(range(1, len(tasks) + 1)):
            raise ValueError("Manifest task indices must be consecutive")
        if sum(task.samples for task in tasks) != manifest.total_samples:
            raise ValueError("Manifest sample total does not match its tasks")
        return manifest

    def task(self, index: int) -> TaskSpec:
        if not 1 <= index <= len(self.tasks):
            raise ValueError("Task index is outside the manifest")
        return self.tasks[index - 1]


@dataclass(frozen=True)
class TaskResult:
    index: int
    samples: int
    seed: int
    hits: int
    host: str
    elapsed_seconds: float
    worker_sha256: str

    def validate(self, task: TaskSpec, worker_sha256: str) -> None:
        if (self.index, self.samples, self.seed) != (task.index, task.samples, task.seed):
            raise ValueError("Result does not match the task's index, sample count, and seed")
        if not 0 <= self.hits <= self.samples:
            raise ValueError("Result hit count is out of range")
        if self.worker_sha256 != worker_sha256:
            raise ValueError("Result worker checksum does not match the manifest")

    @classmethod
    def from_json(cls, value: object) -> TaskResult:
        data = record(value)
        elapsed = data.get("elapsed_seconds")
        if (not isinstance(elapsed, (int, float)) or isinstance(elapsed, bool)
                or not math.isfinite(elapsed) or elapsed < 0):
            raise ValueError("elapsed_seconds must be finite and nonnegative")
        return cls(integer(data, "index"), integer(data, "samples"), integer(data, "seed"),
                   integer(data, "hits"), string(data, "host"), float(elapsed),
                   string(data, "worker_sha256"))


@dataclass(frozen=True)
class Summary:
    tasks: int
    samples: int
    hits: int
    pi_estimate: float
    estimated_standard_error: float
    hosts: tuple[str, ...]

    @classmethod
    def from_results(cls, results: list[TaskResult]) -> Summary:
        samples = sum(result.samples for result in results)
        hits = sum(result.hits for result in results)
        probability = hits / samples
        return cls(len(results), samples, hits, 4 * probability,
                   4 * math.sqrt(probability * (1 - probability) / samples),
                   tuple(sorted({result.host for result in results})))
