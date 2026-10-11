#!/usr/bin/env python3

from pathlib import Path
from typing_extensions import Annotated
import typer

from GaugiKernel import file_parallel_job, ComponentAccumulator, LoggingLevel
from GaugiKernel.constants import MINUTES
from G4Kernel import EventReader
from RootStreamBuilder import recordable, RootStreamHITMaker
from CaloHitBuilder import CaloHitBuilder
from geometry import DetectorConstruction_v1


@file_parallel_job(ntuple_name="CollectionTree", output_replace=(".EVT.", ".HIT."))
def main(
    input_file: Annotated[str | Path, typer.Option("-i", "--input-file", help="Input EVT file or directory")],
    output_file: Annotated[str | Path, typer.Option("-o", "--output-file", help="Destination HIT file or directory")],
    number_of_threads: Annotated[int, typer.Option("-nt", "--number-of-threads", help="Threads allocated per worker")] = 1,
    logging_level: Annotated[str, typer.Option("-l", "--output-level", help="The output level messenger.")] = "INFO",
    pre_init: Annotated[str, typer.Option("--pre-init", help="The preinit command")] = "''",
    pre_exec: Annotated[str, typer.Option("--pre-exec", help="The preexec command")] = "''",
    post_exec: Annotated[str, typer.Option("--post-exec", help="The postexec command")] = "''",
    enable_magnetic_field: Annotated[bool, typer.Option("--enable-magnetic-field", help="Enable the magnetic field.")] = False,
    save_all_hits: Annotated[bool, typer.Option("--save-all-hits", help="Save all hits into the output file.")] = False,
    timeout: Annotated[int, typer.Option("--timeout", help="Timeout in minutes.")] = 10,
    number_of_events: Annotated[int, typer.Option("--nov", "--number-of-events", help="The total number of events to run.")] = -1,
):
    """
    Simulates detector showers from generated events using Geant4.
    """
    input_file = str(input_file)
    output_file = str(output_file)
    outputLevel = LoggingLevel.toC(logging_level)

    exec(pre_init)

    acc = ComponentAccumulator(
        "ComponentAccumulator",
        DetectorConstruction_v1("ATLAS", UseMagneticField=enable_magnetic_field),
        NumberOfThreads=number_of_threads,
        OutputFile=output_file,
        Timeout=timeout * MINUTES,
    )

    gun = EventReader(
        "EventReader",
        input_file,
        OutputEventKey=recordable("Events"),
        OutputTruthKey=recordable("Particles"),
        OutputSeedKey=recordable("Seeds"),
    )
    calorimeter = CaloHitBuilder(
        "CaloHitBuilder",
        HistogramPath="Expert/Hits",
        OutputLevel=outputLevel,
        OutputHitsKey=recordable("Hits"),
    )

    gun.merge(acc)
    calorimeter.merge(acc)
    HIT = RootStreamHITMaker(
        "RootStreamHITMaker",
        OutputLevel=outputLevel,
        OnlyRoI=not save_all_hits,
        InputHitsKey=recordable("Hits"),
        InputEventKey=recordable("Events"),
        InputTruthKey=recordable("Particles"),
        InputSeedsKey=recordable("Seeds"),
    )
    acc += HIT

    exec(pre_exec)
    acc.run(number_of_events)
    exec(post_exec)


if __name__ == "__main__":
    main()
