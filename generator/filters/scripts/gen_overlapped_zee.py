#!/usr/bin/env python3
"""
Script: gen_overlapped_zee.py
Purpose: Generates overlapped Zee events with boosted electrons using Pythia8.
Usage:
    gen_overlapped_zee.py -o output.root --nov 100 [options]
"""

import os
from typing import List
from typing_extensions import Annotated
import typer

from GaugiKernel import parallel_job, LoggingLevel, GeV
from GenKernel import Pythia8Cfg as Pythia8, EventTapeCfg as EventTape
from filters import ZeeCfg as Zee, OverlappedEventsCfg as OverlappedEvents, Particle


datapath = os.environ.get("LORENZETTI_EVTGEN_DATA_DIR", "")
ZEE_FILE = f"{datapath}/zee_config.cmnd"


@parallel_job
def main(
    events: List[int],
    output_file: str,
    seed: int,
    run_number: Annotated[int, typer.Option("--run-number", help="The run number.")] = 0,
    output_level: Annotated[str, typer.Option("--output-level", help="The output level messenger.")] = "INFO",
    eta_max: Annotated[float, typer.Option("--eta-max", help="The eta max used in generator.")] = 3.2,
    force_forward_electron: Annotated[bool, typer.Option("--force-forward-electron", help="Force at least one electron into forward region.")] = False,
    zero_vertex_particles: Annotated[bool, typer.Option("--zero-vertex-particles", help="Fix the z vertex position in simulation to zero.")] = False,
    zee_file: Annotated[str, typer.Option("--zee-file", help="The pythia zee file configuration.")] = ZEE_FILE,
):
    """
    Generates overlapped Zee events with boosted electrons using Pythia8.
    """
    outputLevel = LoggingLevel.toC(output_level)

    tape = EventTape("EventTape", OutputFile=output_file, RunNumber=run_number)

    zee = Zee(
        "Zee",
        Pythia8("Generator", File=zee_file, Seed=seed),
        EtaMax=eta_max,
        MinPt=15 * GeV,
        ZeroVertexParticles=zero_vertex_particles,
        ForceForwardElectron=force_forward_electron,
        OutputLevel=outputLevel,
    )
    tape += zee

    boostedElectron = OverlappedEvents(
        "BoostedElectron",
        Pythia8("BoostedGenerator", Seed=seed),
        Particle=Particle.Electron,
        DeltaR=0.5,
        OutputLevel=outputLevel,
    )
    tape += boostedElectron

    tape.run(events)


if __name__ == "__main__":
    main()
