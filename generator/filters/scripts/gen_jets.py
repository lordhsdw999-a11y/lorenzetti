#!/usr/bin/env python3
"""
Script: gen_jets.py
Purpose: Generates Jet simulation events using Pythia8 and the JF17 filter.
Usage:
    gen_jets.py -o output.root --nov 100 [options]
"""

import os
from pathlib import Path
from typing import List
from typing_extensions import Annotated
import typer

from GaugiKernel import parallel_job, LoggingLevel, GeV
from GenKernel import Pythia8Cfg as Pythia8, EventTapeCfg as EventTape
from filters import JF17Cfg as JF17


datapath = os.environ.get("LORENZETTI_EVTGEN_DATA_DIR", "")
JF17_FILE = f"{datapath}/jet_config.cmnd"


@parallel_job
def main(
    events: List[int],
    output_file: str,
    seed: int,
    run_number: Annotated[int, typer.Option("--run-number", help="The run number.")] = 0,
    output_level: Annotated[str, typer.Option("--output-level", help="The output level messenger.")] = "INFO",
    eta_min: Annotated[float, typer.Option("--eta-min", help="The eta min used in generator.")] = 0.0,
    eta_max: Annotated[float, typer.Option("--eta-max", help="The eta max used in generator.")] = 3.2,
    energy_min: Annotated[float, typer.Option("--energy-min", help="Minimum energy in GeV.")] = 17.0,
    energy_max: Annotated[float, typer.Option("--energy-max", help="Maximum energy in GeV.")] = 6500.0,
    jf17_file: Annotated[str, typer.Option("--jf17-file", help="The pythia JF17 file configuration.")] = JF17_FILE,
):
    """
    Generates Jet simulation events using Pythia8 and the JF17 filter.
    """
    outputLevel = LoggingLevel.toC(output_level)

    tape = EventTape(
        "EventTape",
        OutputFile=output_file,
        RunNumber=run_number,
    )

    jets = JF17(
        "JF17",
        Pythia8(
            "Generator",
            File=jf17_file,
            Seed=seed,
        ),
        EtaMax=eta_max,
        EtaMin=eta_min,
        MinPt=energy_min * GeV,
        Select=2,
        EtaWindow=0.4,
        PhiWindow=0.4,
        OutputLevel=outputLevel,
    )

    tape += jets
    tape.run(events)


if __name__ == "__main__":
    main()