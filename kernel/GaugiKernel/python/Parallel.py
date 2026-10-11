"""
Parallel execution engine and CLI generator using Typer and isolated subprocesses.

This module provides high-performance parallel execution for Lorenzetti physics
generators and event processors while maintaining total memory, C++, and ROOT
decoupling across processes.

Architecture Overview:
----------------------
Traditional Python multiprocessing often fails when interacting with heavy C++
frameworks (such as ROOT, Geant4, or Pythia8) due to pickling limitations,
shared global state, or symbol collisions (e.g., `_Py_HashPointer`).
`GaugiKernel.Parallel` solves this through a dual-mode Orchestrator/Worker pattern:

1. **Orchestrator Mode** (Invoked when running from CLI without internal worker flags):
   - Computes event partitions (chunks) and generates isolated pseudo-random seeds.
   - Prints a formatted execution plan (using `rich`) displaying jobs, seeds, and ranges.
   - Dispatches independent worker subprocesses concurrently via `ThreadPoolExecutor`.
   - Optionally streams worker logs in real time (`--show-output` / `-v`).
   - Automatically merges chunk outputs (`.0.root`, `.1.root`, ...) using ROOT `hadd`.

2. **Worker Mode** (Invoked internally by subprocesses with `--is-worker`):
   - Receives chunk-specific parameters (`--output-file`, `--nov`, `--seed`, etc.).
   - Directly executes the decorated user function in a clean, isolated memory space.
   - Exits cleanly upon completion with standard Unix exit codes.

Examples:
---------
Basic usage in a generator script:

    from typing import List
    from typing_extensions import Annotated
    import typer
    from GaugiKernel import parallel_job

    @parallel_job(ntuple_name="particles")
    def main(
        events: List[int],
        output_file: str,
        seed: int,
        energy: Annotated[float, typer.Option("--energy", help="Beam energy in GeV")] = 50.0,
    ):
        \"\"\"Generate single particle events.\"\"\"
        print(f"Generating {len(events)} events with seed {seed} into {output_file}")
        # Initialize EventTape, configure Pythia/Geant4, and process events:
        # tape = EventTape("Tape", OutputFile=output_file)
        # tape.run(events)

    if __name__ == "__main__":
        main()

Command-Line Usage:
-------------------
Run 100 events across 4 parallel processes:
    $ python3 gen_script.py -o output.root --nov 100 -nt 4

View execution plan without running (Dry Run):
    $ python3 gen_script.py -o output.root --nov 100 -nt 4 --dry-run

Enable real-time log streaming from worker processes:
    $ python3 gen_script.py -o output.root --nov 100 -nt 4 -v
"""

from __future__ import annotations

import inspect
import json
import os
import random
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from math import ceil
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated

import typer
import ROOT

from GaugiKernel import Logger, LoggingLevel


__all__ = [
    "ParallelJob",
    "parallel_job",
    "append_index_to_file",
    "check_file_exists",
    "merge_root_files",
]


def append_index_to_file(output_file: Union[str, Path], index: int) -> str:
    """
    Inserts a numerical chunk index before the file extension.

    Args:
        output_file: The destination filename or Path (e.g. 'output.root').
        index: The chunk index (e.g. 0).

    Returns:
        The modified file path as a string (e.g. 'output.0.root').

    Example:
        >>> append_index_to_file("data/events.root", 2)
        'data/events.2.root'
    """
    p = Path(output_file)
    suffix = p.suffix
    if suffix:
        return str(p.parent / f"{p.stem}.{index}{suffix}")
    return f"{str(p)}.{index}"


def check_file_exists(path: Union[str, Path], ntuple_name: str = "") -> bool:
    """
    Checks if a ROOT file exists, is non-empty, and contains valid entries.

    Args:
        path: Path to the ROOT file to verify.
        ntuple_name: Optional TTree or TObject name to inspect for entries.
                     If empty, only verifies that the file exists and is > 0 bytes.

    Returns:
        True if the file is valid and contains entries, False otherwise.
    """
    path_str = str(path)
    if not os.path.exists(path_str):
        return False
    if not ntuple_name:
        return os.path.getsize(path_str) > 0
    try:
        f = ROOT.TFile.Open(path_str, "READ")
        if not f or f.IsZombie():
            return False
        obj = f.Get(ntuple_name)
        entries = obj.GetEntries() if obj else 0
        f.Close()
        return entries > 0
    except Exception:
        return False


def merge_root_files(output_file: Union[str, Path], chunk_files: List[str]) -> None:
    """
    Merges intermediate chunk ROOT files into a single destination file via ROOT `hadd`.

    Upon successful merge, the intermediate chunk files are automatically cleaned up.

    Args:
        output_file: Target merged ROOT file path.
        chunk_files: List of paths to existing chunk ROOT files.

    Raises:
        RuntimeError: If `hadd` fails with a non-zero exit code.
    """
    output_str = str(output_file)
    if not chunk_files:
        return
    if len(chunk_files) == 1:
        if chunk_files[0] != output_str:
            shutil.move(chunk_files[0], output_str)
        return

    cmd = f"hadd -f {output_str} {' '.join(chunk_files)}"
    ret = os.system(cmd)
    if ret != 0:
        raise RuntimeError(f"hadd failed with exit code {ret}: {cmd}")
    for f in chunk_files:
        if os.path.exists(f) and f != output_str:
            try:
                os.remove(f)
            except OSError:
                pass


class ParallelJob(Logger):
    """
    Manages event chunk partitioning, subprocess dispatching, and output merging.

    Attributes:
        output_file: Final merged output ROOT file path.
        seed: Base random seed used to deterministically generate chunk seeds.
        number_of_threads: Number of concurrent worker processes to launch.
        number_of_events: Total number of events requested.
        events_per_job: Number of events per chunk (-1 calculates automatically).
        event_numbers: Optional explicit list or comma-separated string of event IDs.
        merge: If True, merges chunk files with `hadd -f` after completion.
        ntuple_name: Name of TTree checked for file existence / validation.
        overwrite: If True, re-executes and overwrites already existing chunk files.
        dry_run: If True, plans execution and displays commands without running them.
        show_output: If True, streams worker stdout/stderr in real time.
    """

    def __init__(
        self,
        output_file: Union[str, Path],
        seed: int = 512,
        number_of_threads: int = 1,
        number_of_events: int = -1,
        events_per_job: int = -1,
        event_numbers: Optional[Union[str, List[int]]] = None,
        merge: bool = True,
        ntuple_name: str = "particles",
        overwrite: bool = True,
        dry_run: bool = False,
        show_output: bool = False,
    ):
        super().__init__()
        self.output_file = str(output_file)
        self.seed = seed
        self.number_of_threads = number_of_threads
        self.number_of_events = number_of_events
        self.events_per_job = events_per_job
        self.event_numbers = event_numbers
        self.merge = merge
        self.ntuple_name = ntuple_name
        self.overwrite = overwrite
        self.dry_run = dry_run
        self.show_output = show_output

    def get_events_per_job(self) -> int:
        """
        Calculates the number of events allocated to each job partition.

        Returns:
            Events count per job.
        """
        if self.events_per_job > 0:
            return self.events_per_job
        if self.number_of_threads > 0 and self.number_of_events > 0:
            return ceil(self.number_of_events / self.number_of_threads)
        return max(1, self.number_of_events)

    def build_plan(self) -> Dict[str, Dict[str, Any]]:
        """
        Partitions the event domain into chunks and assigns unique random seeds.

        Returns:
            Dictionary mapping intermediate chunk output filenames to their configuration:
            {
                "output.0.root": {"events": [0, 1, ...], "seed": 1234567, "event_start": 0},
                ...
            }
        """
        def get_random_seed() -> int:
            return random.randint(1, 900_000_000)

        # Parse event list: explicit event numbers vs range(total)
        if self.event_numbers:
            if isinstance(self.event_numbers, str):
                events_list = [int(x.strip()) for x in self.event_numbers.split(",") if x.strip()]
            else:
                events_list = list(self.event_numbers)
            self.number_of_events = len(events_list)
        else:
            total = max(0, self.number_of_events)
            events_list = list(range(total))

        step = self.get_events_per_job()
        chunks = [events_list[i : i + step] for i in range(0, len(events_list), step)]

        plan: Dict[str, Dict[str, Any]] = {}
        random.seed(self.seed)

        for idx, chunk_events in enumerate(chunks):
            chunk_file = append_index_to_file(self.output_file, idx)
            cfg: Dict[str, Any] = {
                "events": chunk_events,
                "seed": get_random_seed(),
            }
            # Optimize continuous ranges by passing event_start offset
            if not self.event_numbers and chunk_events:
                cfg["event_start"] = chunk_events[0]
            plan[chunk_file] = cfg
        return plan

    def print_plan(self, plan: Dict[str, Dict[str, Any]]) -> None:
        """
        Displays a structured, elegant terminal table showing the execution plan.

        Follows a strict color palette: blue, green, and dark gray.

        Args:
            plan: The partitioned execution plan generated by `build_plan()`.
        """
        try:
            from rich.console import Console
            from rich.table import Table
            from rich import box

            console = Console()
            table = Table(
                title=(
                    f"\n[bold blue]Lorenzetti Parallel Execution Plan[/bold blue]\n"
                    f"[grey50]Output: {self.output_file}  │  Workers: {self.number_of_threads}  │  "
                    f"Total Events: {self.number_of_events}  │  Merge: {self.merge}[/grey50]\n"
                ),
                box=box.ROUNDED,
                border_style="grey50",
                header_style="bold blue",
                show_footer=True,
                footer_style="grey50",
            )

            table.add_column("Job", justify="center", style="bold blue", footer="Total", footer_style="bold blue")
            table.add_column("Output Chunk", style="green", footer=f"{len(plan)} job(s)", footer_style="green")
            table.add_column("Events", justify="right", style="bold green", footer=str(self.number_of_events), footer_style="bold green")
            table.add_column("Event Range", justify="center", style="grey50", footer="-")
            table.add_column("Seed", justify="right", style="blue", footer=f"base={self.seed}", footer_style="blue")
            table.add_column("Status", justify="center", footer="-")

            for idx, (chunk_file, cfg) in enumerate(plan.items()):
                events = cfg.get("events", [])
                n_evts = len(events)
                if "event_start" in cfg:
                    start = cfg["event_start"]
                    end = start + n_evts - 1 if n_evts > 0 else start
                    range_str = f"[{start} → {end}]"
                elif events:
                    if len(events) <= 4:
                        range_str = str(events)
                    else:
                        range_str = f"[{events[0]}, {events[1]}, ... {events[-1]}]"
                else:
                    range_str = "[]"

                exists = check_file_exists(chunk_file, self.ntuple_name)
                if exists and not self.overwrite:
                    status_str = "[grey50]Skip (exists)[/grey50]"
                else:
                    status_str = "[bold green]Ready[/bold green]"

                table.add_row(
                    str(idx),
                    Path(chunk_file).name,
                    str(n_evts),
                    range_str,
                    str(cfg["seed"]),
                    status_str,
                )

            console.print(table)
            print()
        except Exception:
            self._logger.info(f"Execution plan: {len(plan)} chunk(s) to process.")

    def run_commands(self, commands: List[Tuple[str, List[str]]]) -> None:
        """
        Executes a list of worker commands concurrently via isolated subprocesses.

        Args:
            commands: List of tuples where each element contains `(chunk_file, command_arguments)`.

        Raises:
            RuntimeError: If any subprocess fails with a non-zero exit code.
        """
        def _exec_cmd(item: Tuple[str, List[str]]) -> str:
            chunk_file, cmd = item
            cmd_str = " ".join(cmd)
            self._logger.debug(f"Starting chunk process: {cmd_str}")

            if self.show_output:
                chunk_name = Path(chunk_file).name
                proc = subprocess.Popen(
                    cmd,
                    env=os.environ,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                if proc.stdout:
                    for line in iter(proc.stdout.readline, ""):
                        print(f"[{chunk_name}] {line}", end="", flush=True)
                proc.wait()
                if proc.returncode != 0:
                    self._logger.error(
                        f"Job failed for chunk: {chunk_file}\n"
                        f"Command: {cmd_str}\n"
                        f"Exit code: {proc.returncode}"
                    )
                    raise RuntimeError(f"Subprocess failed for {chunk_file} (exit code {proc.returncode})")
                return chunk_file

            res = subprocess.run(cmd, env=os.environ, capture_output=True, text=True)
            if res.returncode != 0:
                self._logger.error(
                    f"Job failed for chunk: {chunk_file}\n"
                    f"Command: {cmd_str}\n"
                    f"Exit code: {res.returncode}\n"
                    f"--- STDERR ---\n{res.stderr}\n"
                    f"--- STDOUT ---\n{res.stdout}"
                )
                raise RuntimeError(f"Subprocess failed for {chunk_file} (exit code {res.returncode})")
            if res.stdout:
                self._logger.debug(f"[{chunk_file} stdout]: {res.stdout.strip()}")
            return chunk_file

        with ThreadPoolExecutor(max_workers=max(1, self.number_of_threads)) as executor:
            list(executor.map(_exec_cmd, commands))


def parallel_job(_func: Optional[Callable] = None, *, ntuple_name: str = "particles"):
    """
    Decorator that transforms a worker function into a production Typer CLI application
    with subprocess-based parallel processing.

    The decorated function should accept the following standard framework parameters:
    - `events: List[int]`: The list of event indices allocated to this execution chunk.
    - `output_file: str`: The destination output ROOT file path for this chunk.
    - `seed: int`: The pseudo-random seed assigned for this chunk.

    Any additional parameters with `Annotated[..., typer.Option(...)]` will automatically
    be exposed as CLI arguments and passed to child workers.

    Args:
        _func: The worker function to decorate (when used without parentheses).
        ntuple_name: The name of the primary TTree or object in the ROOT file
                     used to check for existing entries and validate outputs.

    Returns:
        A callable Typer application launcher.
    """
    def decorator(fn: Callable):
        sig = inspect.signature(fn)
        injected = {"events", "output_file", "seed"}

        worker_params = []
        for name, p in sig.parameters.items():
            if name not in injected:
                worker_params.append(p.replace(kind=inspect.Parameter.KEYWORD_ONLY))

        def job_file_callback(ctx: typer.Context, value: Optional[Path]):
            """Loads overrides from a JSON configuration file if provided."""
            if value and value.exists():
                with open(value, "r") as f:
                    data = json.load(f)
                    ctx.default_map = ctx.default_map or {}
                    ctx.default_map.update(data)
            return value

        # Standard options injected by the ParallelJob framework into the CLI
        framework_params = [
            inspect.Parameter(
                "is_worker",
                inspect.Parameter.KEYWORD_ONLY,
                default=False,
                annotation=Annotated[bool, typer.Option("--is-worker", hidden=True, help="Internal worker flag")],
            ),
            inspect.Parameter(
                "event_start",
                inspect.Parameter.KEYWORD_ONLY,
                default=0,
                annotation=Annotated[int, typer.Option("--event-start", hidden=True, help="Internal event start offset")],
            ),
            inspect.Parameter(
                "output_file",
                inspect.Parameter.KEYWORD_ONLY,
                annotation=Annotated[Path, typer.Option("-o", "--output-file", help="Destination ROOT output file")],
            ),
            inspect.Parameter(
                "nov",
                inspect.Parameter.KEYWORD_ONLY,
                default=-1,
                annotation=Annotated[int, typer.Option("--nov", "--number-of-events", help="Total number of events to run")],
            ),
            inspect.Parameter(
                "number_of_threads",
                inspect.Parameter.KEYWORD_ONLY,
                default=1,
                annotation=Annotated[int, typer.Option("-nt", "--number-of-threads", help="Number of parallel worker processes")],
            ),
            inspect.Parameter(
                "events_per_job",
                inspect.Parameter.KEYWORD_ONLY,
                default=-1,
                annotation=Annotated[int, typer.Option("--events-per-job", help="Number of events per chunk/job")],
            ),
            inspect.Parameter(
                "seed",
                inspect.Parameter.KEYWORD_ONLY,
                default=512,
                annotation=Annotated[int, typer.Option("-s", "--seed", help="Base random seed")],
            ),
            inspect.Parameter(
                "event_numbers",
                inspect.Parameter.KEYWORD_ONLY,
                default=None,
                annotation=Annotated[Optional[str], typer.Option("-e", "--event-numbers", help="Comma-separated event numbers")],
            ),
            inspect.Parameter(
                "merge",
                inspect.Parameter.KEYWORD_ONLY,
                default=True,
                annotation=Annotated[bool, typer.Option("-m", "--merge/--no-merge", help="Merge chunk files with hadd")],
            ),
            inspect.Parameter(
                "overwrite",
                inspect.Parameter.KEYWORD_ONLY,
                default=True,
                annotation=Annotated[bool, typer.Option("--overwrite/--no-overwrite", help="Overwrite existing output files")],
            ),
            inspect.Parameter(
                "dry_run",
                inspect.Parameter.KEYWORD_ONLY,
                default=False,
                annotation=Annotated[bool, typer.Option("--dry-run", help="Dry run without executing jobs")],
            ),
            inspect.Parameter(
                "show_output",
                inspect.Parameter.KEYWORD_ONLY,
                default=False,
                annotation=Annotated[bool, typer.Option("--show-output/--no-show-output", "-v", help="Display stdout/stderr from worker processes in real time")],
            ),
            inspect.Parameter(
                "job_file",
                inspect.Parameter.KEYWORD_ONLY,
                default=None,
                annotation=Annotated[Optional[Path], typer.Option("--job-file", callback=job_file_callback, is_eager=True, help="JSON configuration file to override options")],
            ),
        ]

        all_params = framework_params + worker_params
        new_sig = sig.replace(parameters=all_params)

        def cli_entry(**kwargs):
            is_worker = kwargs.pop("is_worker", False)
            event_start = kwargs.pop("event_start", 0)
            output_file = kwargs.pop("output_file")
            nov = kwargs.pop("nov")
            base_seed = kwargs.pop("seed")
            event_numbers_str = kwargs.pop("event_numbers", None)

            # Orchestrator-only options
            n_threads = kwargs.pop("number_of_threads", 1)
            events_per_job = kwargs.pop("events_per_job", -1)
            merge = kwargs.pop("merge", True)
            overwrite = kwargs.pop("overwrite", True)
            dry_run = kwargs.pop("dry_run", False)
            show_output = kwargs.pop("show_output", False)
            kwargs.pop("job_file", None)

            if is_worker:
                # =============================================================
                # WORKER MODE: Execute this single partition in clean process
                # =============================================================
                if event_numbers_str:
                    events = [int(x.strip()) for x in event_numbers_str.split(",") if x.strip()]
                else:
                    events = list(range(event_start, event_start + max(0, nov)))

                fn(events=events, output_file=str(output_file), seed=base_seed, **kwargs)
                return

            # =================================================================
            # ORCHESTRATOR MODE: Plan, dispatch subprocesses, and merge results
            # =================================================================
            if Path(output_file).is_dir():
                raise IsADirectoryError(f"Output file '{output_file}' was expected to be a file, but it is a directory.")

            job = ParallelJob(
                output_file=output_file,
                seed=base_seed,
                number_of_threads=n_threads,
                number_of_events=nov,
                events_per_job=events_per_job,
                event_numbers=event_numbers_str,
                merge=merge,
                ntuple_name=ntuple_name,
                overwrite=overwrite,
                dry_run=dry_run,
                show_output=show_output,
            )

            plan = job.build_plan()
            job.print_plan(plan)

            script_path = shutil.which(sys.argv[0]) or os.path.abspath(sys.argv[0])

            commands_to_run: List[Tuple[str, List[str]]] = []
            for chunk_file, config in plan.items():
                if not check_file_exists(chunk_file, ntuple_name) or overwrite:
                    cmd = [
                        sys.executable,
                        script_path,
                        "--is-worker",
                        "-o", str(chunk_file),
                        "-s", str(config["seed"]),
                    ]
                    if "event_start" in config:
                        cmd.extend([
                            "--nov", str(len(config["events"])),
                            "--event-start", str(config["event_start"]),
                        ])
                    else:
                        cmd.extend([
                            "--nov", str(len(config["events"])),
                            "--event-numbers", ",".join(str(x) for x in config["events"]),
                        ])

                    for k, v in kwargs.items():
                        cli_flag = f"--{k.replace('_', '-')}"
                        if isinstance(v, bool):
                            if v:
                                cmd.append(cli_flag)
                        elif v is not None:
                            cmd.extend([cli_flag, str(v)])

                    commands_to_run.append((chunk_file, cmd))
                else:
                    job._logger.info(f"Skipping existing output: {chunk_file}")

            if dry_run:
                job._logger.info(f"[Dry Run] {len(commands_to_run)} jobs planned:")
                for chunk_file, cmd in commands_to_run:
                    job._logger.info(f"  Command: {' '.join(cmd)}")
                return

            if not commands_to_run:
                job._logger.info("No jobs to run (all outputs already exist).")
                return

            job._logger.info(f"Executing {len(commands_to_run)} jobs across {n_threads} processes...")
            job.run_commands(commands_to_run)

            all_chunk_files = list(plan.keys())
            if merge or len(all_chunk_files) == 1:
                job._logger.info(f"Merging {len(all_chunk_files)} chunk(s) into {output_file}...")
                merge_root_files(output_file, all_chunk_files)

        cli_entry.__signature__ = new_sig
        cli_entry.__annotations__ = {p.name: p.annotation for p in all_params}
        cli_entry.__doc__ = fn.__doc__

        app = typer.Typer(
            pretty_exceptions_enable=False,
            context_settings={"help_option_names": ["-h", "--help"]},
        )
        app.command()(cli_entry)

        def launcher(*args, **kw):
            if args or kw:
                return fn(*args, **kw)
            return app()

        launcher.app = app
        launcher.fn = fn
        return launcher

    if _func is None:
        return decorator
    return decorator(_func)
