"""
Parallel execution engine and CLI generator using Typer.

Provides:
- ParallelJob: Core class for chunking events, dispatching workers, and merging results.
- @parallel_job: Decorator that turns a worker function into a complete Typer CLI command.
"""

from __future__ import annotations

import inspect
import json
import os
import random
import shutil
from math import ceil
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from typing_extensions import Annotated

import joblib
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
    """Inserts a chunk index before the file extension."""
    p = Path(output_file)
    suffix = p.suffix
    if suffix:
        return str(p.parent / f"{p.stem}.{index}{suffix}")
    return f"{str(p)}.{index}"


def check_file_exists(path: Union[str, Path], ntuple_name: str = "") -> bool:
    """Checks if a ROOT file exists and contains valid entries."""
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
    """Merges chunk ROOT files into a single destination file via hadd."""
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
    Manages event chunking, process dispatching, and output merging.
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

    def get_events_per_job(self) -> int:
        if self.events_per_job > 0:
            return self.events_per_job
        if self.number_of_threads > 0 and self.number_of_events > 0:
            return ceil(self.number_of_events / self.number_of_threads)
        return max(1, self.number_of_events)

    def build_plan(self) -> Dict[str, Dict[str, Any]]:
        """Splits events into chunks and assigns unique random seeds."""
        def get_random_seed() -> int:
            return random.randint(1, 900_000_000)

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
            plan[chunk_file] = {
                "events": chunk_events,
                "seed": get_random_seed(),
            }
        return plan

    def run(self, function: Callable, **worker_kwargs) -> None:
        """Executes the function over the generated plan."""
        plan = self.build_plan()
        self._logger.info(f"ParallelJob plan built with {len(plan)} job(s).")

        jobs = []
        for chunk_file, config in plan.items():
            if not check_file_exists(chunk_file, self.ntuple_name) or self.overwrite:
                jobs.append((chunk_file, config["events"], config["seed"]))
            else:
                self._logger.info(f"Skipping existing output: {chunk_file}")

        if self.dry_run:
            self._logger.info(f"[Dry Run] {len(jobs)} jobs would be scheduled:")
            for chunk_file, evts, s in jobs:
                self._logger.info(f"  File: {chunk_file} | Events: {len(evts)} | Seed: {s}")
            return

        if not jobs:
            self._logger.info("No jobs to run (all outputs already exist).")
            return

        self._logger.info(f"Executing {len(jobs)} jobs across {self.number_of_threads} threads/processes...")

        pool = joblib.Parallel(n_jobs=self.number_of_threads, backend="multiprocessing")
        pool(
            joblib.delayed(function)(
                events=evts,
                output_file=chunk_file,
                seed=s,
                **worker_kwargs
            )
            for chunk_file, evts, s in jobs
        )

        all_chunk_files = list(plan.keys())
        if self.merge or len(all_chunk_files) == 1:
            self._logger.info(f"Merging {len(all_chunk_files)} chunk(s) into {self.output_file}...")
            merge_root_files(self.output_file, all_chunk_files)


def parallel_job(_func: Optional[Callable] = None, *, ntuple_name: str = "particles"):
    """
    Decorator that turns a worker function into a complete Typer CLI application
    with parallel execution support.

    The worker function should accept injected parameters `events`, `output_file`, `seed`,
    and any additional CLI options annotated with `Annotated[..., typer.Option(...)]`.
    """
    def decorator(fn: Callable):
        sig = inspect.signature(fn)
        injected = {"events", "output_file", "seed"}

        worker_params = []
        for name, p in sig.parameters.items():
            if name not in injected:
                worker_params.append(p.replace(kind=inspect.Parameter.KEYWORD_ONLY))

        def job_file_callback(ctx: typer.Context, value: Optional[Path]):
            if value and value.exists():
                with open(value, "r") as f:
                    data = json.load(f)
                    ctx.default_map = ctx.default_map or {}
                    ctx.default_map.update(data)
            return value

        framework_params = [
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
                "job_file",
                inspect.Parameter.KEYWORD_ONLY,
                default=None,
                annotation=Annotated[Optional[Path], typer.Option("--job-file", callback=job_file_callback, is_eager=True, help="JSON configuration file to override options")],
            ),
        ]

        all_params = framework_params + worker_params
        new_sig = sig.replace(parameters=all_params)

        def cli_entry(**kwargs):
            output_file = kwargs.pop("output_file")
            if Path(output_file).is_dir():
                raise IsADirectoryError(f"Output file '{output_file}' was expected to be a file, but it is a directory.")

            nov = kwargs.pop("nov")
            n_threads = kwargs.pop("number_of_threads")
            events_per_job = kwargs.pop("events_per_job")
            base_seed = kwargs.pop("seed")
            event_numbers = kwargs.pop("event_numbers")
            merge = kwargs.pop("merge")
            overwrite = kwargs.pop("overwrite")
            dry_run = kwargs.pop("dry_run")
            kwargs.pop("job_file", None)

            job = ParallelJob(
                output_file=output_file,
                seed=base_seed,
                number_of_threads=n_threads,
                number_of_events=nov,
                events_per_job=events_per_job,
                event_numbers=event_numbers,
                merge=merge,
                ntuple_name=ntuple_name,
                overwrite=overwrite,
                dry_run=dry_run,
            )

            job.run(fn, **kwargs)

        cli_entry.__signature__ = new_sig
        cli_entry.__annotations__ = {p.name: p.annotation for p in all_params}
        cli_entry.__doc__ = fn.__doc__

        app = typer.Typer(pretty_exceptions_enable=False)
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
