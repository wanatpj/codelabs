"""Internal entry point executed by each LSF array element."""

from dataclasses import asdict
from pathlib import Path
from typing import Annotated

import typer

from lib.execution import CppTaskExecutor
from lib.logging import configure_logging, logger
from lib.storage import RunStore


def execute(
    run_dir: Annotated[Path, typer.Argument()],
    index: Annotated[int, typer.Option(envvar="LSB_JOBINDEX", min=1)],
) -> None:
    configure_logging()
    try:
        result = CppTaskExecutor().execute(RunStore(run_dir), index)
        logger.info("task_completed", **asdict(result))
    except (OSError, ValueError, RuntimeError) as error:
        logger.error("operation_failed", error=str(error))
        raise typer.Exit(code=1) from error


if __name__ == "__main__":
    typer.run(execute)
