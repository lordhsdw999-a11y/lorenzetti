#!/usr/bin/env python3

from pathlib import Path
from typing_extensions import Annotated
import typer

from GaugiKernel import file_parallel_job, ComponentAccumulator, LoggingLevel
from RootStreamBuilder import RootStreamAODReader, recordable, RootStreamNtupleMaker


@file_parallel_job(ntuple_name="physics", output_replace=(".AOD.", ".NTUPLE."))
def main(
    input_file: Annotated[str | Path, typer.Option("-i", "--input-file", help="The input file or folder to run the job.")],
    output_file: Annotated[str | Path, typer.Option("-o", "--output-file", help="The output file or folder.")],
    number_of_threads: Annotated[int, typer.Option("-nt", "--number-of-threads", help="Threads allocated per worker")] = 1,
    nov: Annotated[int, typer.Option("--nov", "--number-of-events", help="The total number of events to run.")] = -1,
    logging_level: Annotated[str, typer.Option("-l", "--log-level", help="Logging verbosity.")] = "INFO",
):
    """
    Creates an analysis flat ntuple (TTree 'physics') from AOD input files.
    """
    input_file = str(input_file)
    output_file = str(output_file)
    outputLevel = LoggingLevel.toC(logging_level)

    acc = ComponentAccumulator("ComponentAccumulator", output_file)

    aod = RootStreamAODReader(
        "AODReader",
        InputFile=input_file,
        OutputLevel=outputLevel,
        OutputEventKey=recordable("Events"),
        OutputTruthKey=recordable("Particles"),
        OutputClusterKey=recordable("Clusters"),
        OutputElectronKey=recordable("Electrons"),
        OutputSeedsKey=recordable("Seeds"),
        OutputTruthClusterKey=recordable("TruthClusters"),
        OutputRingerL0Key=recordable("RingsL0"),
        OutputTruthElectronKey=recordable("TruthElectrons"),
        NtupleName="CollectionTree",
    )
    aod.merge(acc)

    ntuple = RootStreamNtupleMaker(
        "NtupleMaker",
        OutputLevel=outputLevel,
        InputEventKey=recordable("Events"),
        InputTruthKey=recordable("Particles"),
        InputClusterKey=recordable("Clusters"),
        InputRingerL0Key=recordable("RingsL0"),
        InputElectronKey=recordable("Electrons"),
        InputSeedsKey=recordable("Seeds"),
        InputTruthClusterKey=recordable("TruthClusters"),
        InputTruthElectronKey=recordable("TruthElectrons"),
        OutputNtupleName="physics",
    )
    acc += ntuple
    acc.run(nov)


if __name__ == "__main__":
    main()
