# Monte Carlo on IBM Spectrum LSF

A C++ program estimates pi. Python splits the work into tasks, submits them to
IBM Spectrum **LSF (Load Sharing Facility)**, and combines the results.

The public CLI has two commands: **submit** and **collect**.

## Build

Requires Linux, a C++11 compiler, Make, Python 3.11+, and Poetry.
Run commands from `ibm_spectrum_lsf/`:

```sh
make setup
```

`make setup` installs the locked Python dependencies using Poetry and builds
the C++ worker. Make, a C++ compiler, Python 3.11+, and Poetry must already be
installed on the machine.

To install a new LSF cluster, obtain the installer packages and entitlement
file from IBM, extract the installer, and edit its `install.config` for your
cluster. IBM's installer runs as root. From this directory, run:

```sh
make install-lsf LSF_INSTALL_DIR=/path/to/extracted/lsf10.1_lsfinstall
```

The target runs `sudo ./lsfinstall -f install.config` in that directory, so
sudo will prompt you. To use a differently named config file, pass
`LSF_INSTALL_CONFIG=your-file`. IBM's install guide lists the required config
values and package files; this target does not download or configure them.
[IBM LSF installation guide](https://www.ibm.com/docs/en/spectrum-lsf/10.1.0?topic=linux-installing-new-lsf-cluster-lsfinstall-unix).

If you are joining an existing cluster, ask its administrator for the client
and cluster configuration instead. Without an LSF cluster, use `--dry-run` to
prepare a submission. IBM LSF Simulator is a separate scheduling-analysis tool
and cannot execute this Monte Carlo worker.

The C++ source, Makefile, and executable are under `job/`. To run the C++
program directly with 100,000 samples and seed 42:

```sh
./job/build/monte_carlo 100000 42
```

## Submit and collect

From an LSF submission host:

```sh
poetry run python cli.py submit --run-dir runs/example
```

The default run uses one million samples split into eight tasks, with at most
four tasks executing at once. LSF selects the execution hosts. Submission returns
before the tasks finish; its structured log reports the job ID.

```sh
bjobs -a JOB_ID
```

Once all tasks finish successfully:

```sh
poetry run python cli.py collect --run-dir runs/example
```

The estimate is logged and saved to `runs/example/summary.json`. It is computed
as `4 * sum(hits) / sum(samples)`, so tasks with different sizes are weighted
correctly. The reported standard error is an approximation.

### Submission options

| Option | Default |
| --- | --- |
| `--run-dir` | Required; use a new directory for each run. |
| `--samples` | `1000000` total samples. |
| `--tasks` | `8` array elements. |
| `--workers` | `4` concurrent elements. |
| `--dry-run` | Off; enable to prepare files without submitting. |

Example:

```sh
poetry run python cli.py submit --run-dir runs/larger \
    --samples 100000000 --tasks 32 --workers 8
```

The worker path, base seed (42), ten-minute walltime, and Python interpreter
have defaults in code. Queue and project use the cluster defaults. If your
site requires explicit settings, change `LsfOptions` in `lib/lsf_dispatcher.py`.

## Check the payload without LSF

Prepare a submission without an IBM account or an LSF installation:

```sh
poetry run python cli.py submit --run-dir runs/preview --dry-run
cat runs/preview/array.sh
```

To check all eight task payloads on your machine, supply the array index that
LSF would normally set:

```sh
for index in 1 2 3 4 5 6 7 8; do
    LSB_JOBINDEX="$index" sh runs/preview/array.sh
done
poetry run python cli.py collect --run-dir runs/preview
```

This checks execution and collection. It does not emulate an LSF scheduler.
Task execution lives in `lib/worker.py`; it is an internal entry point called
by the generated script, not another command in `cli.py`.

## Cluster requirements

Every compute host must see this code, the Python environment, and the run
directory at the same absolute paths, normally through shared storage. The
script uses the active Poetry environment's Python. The hosts need compatible
Python runtimes and runtime dependencies; they do not need Poetry itself.
Compile the C++ executable for the compute hosts' architecture and libraries.

The dispatcher does not transfer files. Shared storage must support file
locking and atomic rename. There are no automatic retries or cancellation;
use `bkill JOB_ID` to cancel an accepted array. An array can run several tasks
on one host; inspect the summary's `hosts` field to see where they ran.

Each run copies its executable and records a checksum. Rebuilding the source
executable cannot change a queued run. Collection validates task inputs and
worker identity. Failed or incomplete collection removes any old summary;
results and summaries are published atomically.

## Tests and cleanup

```sh
make check
make clean
```

`make check` builds the worker, runs strict mypy, then tests the worker,
generated payload, submission handoff, and correctness safeguards without an
IBM cluster. The submission test uses a stub, not IBM software.

`make clean` calls `make -C job clean` and preserves run results.

```sh
poetry run python cli.py --help
poetry run python cli.py submit --help
```

## Files

- `cli.py`: public commands, parsed by Typer.
- `job/`: C++ Monte Carlo worker and build rules.
- `lib/lsf_dispatcher.py`: LSF job-array submission.
- `lib/worker.py`: internal entry point for one array element.
- `lib/execution.py`: worker execution and result collection.
- `lib/storage.py`: snapshots, checksums, locks, and result files.
- `lib/models.py`: typed task inputs and results.
- `lib/logging.py`: structlog configuration and logger; JSON logs go to stderr.

## IBM test environments

For installation steps and the current preflight, see [Trying IBM LSF Simulator](SIMULATOR.md).
The simulator replays scheduling workloads; it does not execute this Monte
Carlo program. For real execution on your own test hosts, investigate
[LSF Community Edition](https://www.ibm.com/support/pages/where-can-i-download-ibm-spectrum-lsf-community-edition-linux).
Its download guidance requires IBM login. A public anonymous IBM job-submission
endpoint has not been identified, and no actual IBM cluster has been tested here.

References: [LSF submission](https://www.ibm.com/docs/en/spectrum-lsf/10.1.0?topic=bsub-description)
and [job monitoring](https://www.ibm.com/docs/en/spectrum-lsf/10.1.0?topic=bjobs-description).
