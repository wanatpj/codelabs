"""Submit the Monte Carlo job and collect its results."""

from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Annotated, Iterator

import typer

from lib.execution import ResultCollector
from lib.logging import configure_logging, logger
from lib.lsf_dispatcher import LsfDispatcher, LsfOptions
from lib.models import RunConfig
from lib.storage import RunStore

WORKER = Path(__file__).resolve().parent / "job" / "build" / "monte_carlo"
app = typer.Typer()


@app.callback()
def initialize_cli() -> None:
    """Submit Monte Carlo tasks to LSF, then collect their results."""
    configure_logging()


@contextmanager
def report_errors() -> Iterator[None]:
    try:
        yield
    except (OSError, ValueError, RuntimeError) as error:
        logger.error("operation_failed", error=str(error))
        raise typer.Exit(code=1) from error


@app.command()
def submit(
    run_dir: Annotated[Path, typer.Option(help="New directory for this run")],
    samples: Annotated[int, typer.Option(min=1, help="Total samples")] = 1_000_000,
    tasks: Annotated[int, typer.Option(min=1, help="Number of LSF tasks")] = 8,
    workers: Annotated[int, typer.Option(min=1, help="Maximum concurrent tasks")] = 4,
    dry_run: Annotated[bool, typer.Option(help="Prepare files without submitting")] = False,
) -> None:
    """Submit the bundled Monte Carlo job to LSF."""
    with report_errors():
        store = RunStore(run_dir)
        manifest = store.create(RunConfig(samples=samples, task_count=tasks), WORKER)
        receipt = LsfDispatcher(LsfOptions(workers)).dispatch(store, manifest, dry_run)
        logger.info(receipt.state, run_dir=str(store.directory),
                    command=receipt.command, job_id=receipt.job_id)


@app.command()
def collect(run_dir: Annotated[Path, typer.Option(help="Directory of a completed run")]) -> None:
    """Validate task outputs and calculate the Monte Carlo estimate."""
    with report_errors():
        summary = ResultCollector().collect(RunStore(run_dir))
        logger.info("results_collected", **asdict(summary))


if __name__ == "__main__":
    app()
