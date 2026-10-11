#!/usr/bin/env python3
"""
Script: gen_single.py
Purpose: Generates single particle events using Pythia8 and the SingleParticle filter.
Usage:
    gen_single.py -o output.root --nov 100 -p Electron [options]
"""

import os
from typing import List
from typing_extensions import Annotated
import typer

from GaugiKernel import parallel_job, LoggingLevel, GeV
from GenKernel import Pythia8Cfg as Pythia8, EventTapeCfg as EventTape
from filters import SingleParticleCfg as SingleParticle, Particle


@parallel_job
def main(
    events: List[int],
    output_file: str,
    seed: int,
    particle: Annotated[str, typer.Option("-p", "--particle", help="The single particle type: Electron, Photon, PiPlus, PiZero, Neutrino.")],
    run_number: Annotated[int, typer.Option("--run-number", help="The run number.")] = 0,
    output_level: Annotated[str, typer.Option("--output-level", help="The output level messenger.")] = "INFO",
    energy_min: Annotated[float, typer.Option("--energy-min", help="Energy min in GeV.")] = -1.0,
    energy_max: Annotated[float, typer.Option("--energy-max", help="Energy max in GeV.")] = -1.0,
    energy: Annotated[float, typer.Option("--energy", help="Energy in GeV.")] = -1.0,
    eta: Annotated[float, typer.Option("--eta", help="Eta position.")] = 0.0,
    phi: Annotated[float, typer.Option("--phi", help="Phi position.")] = 1.52,
    do_eta_ranged: Annotated[bool, typer.Option("--do-eta-ranged", help="Enable eta range.")] = False,
    eta_min: Annotated[float, typer.Option("--eta-min", help="Minimum Eta.")] = -2.5,
    eta_max: Annotated[float, typer.Option("--eta-max", help="Maximum Eta.")] = 2.5,
    do_phi_ranged: Annotated[bool, typer.Option("--do-phi-ranged", help="Enable phi range.")] = False,
    phi_min: Annotated[float, typer.Option("--phi-min", help="Minimum Phi.")] = -3.14,
    phi_max: Annotated[float, typer.Option("--phi-max", help="Maximum Phi.")] = 3.14,
):
    """
    Generates single particle events using Pythia8 and the SingleParticle filter.
    """
    outputLevel = LoggingLevel.toC(output_level)

    tape = EventTape("EventTape", OutputFile=output_file, RunNumber=run_number)

    part = SingleParticle(
        particle,
        Pythia8("Generator", Seed=seed),
        Eta=eta,
        Phi=phi,
        EnergyMin=energy_min * GeV,
        EnergyMax=energy_max * GeV,
        Energy=energy * GeV,
        Particle=Particle.fromstring(particle),
        DoRangedEta=do_eta_ranged,
        EtaMin=eta_min,
        EtaMax=eta_max,
        DoRangedPhi=do_phi_ranged,
        PhiMin=phi_min,
        PhiMax=phi_max,
        OutputLevel=outputLevel,
    )
    tape += part
    tape.run(events)


if __name__ == "__main__":
    main()