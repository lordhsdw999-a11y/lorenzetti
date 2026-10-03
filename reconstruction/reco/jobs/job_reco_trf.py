#!/usr/bin/env python3
import argparse
import sys
import typer
import os

from pathlib import Path
from typing import List, Annotated
from expand_folders import expand_folders
from GaugiKernel import LoggingLevel, get_argparser_formatter
from GaugiKernel import ComponentAccumulator
from RootStreamBuilder import RootStreamESDReader, recordable
from CaloClusterBuilder import CaloClusterMaker
from CaloRingsBuilder import CaloRingsBuilderCfg
from EgammaBuilder import ElectronBuilderCfg
from RootStreamBuilder import RootStreamAODMaker
from RootStreamBuilder.RootStreamFlags import RootStreamAODFlags as flags

from reco.reco_job import merge_args, update_args, create_parallel_job

"""
Script: reco_trf.py
Purpose: Executes the offline reconstruction chain.
         Reads digitized cells (ESD), builds calorimeter clusters, computes
         ring variables (Rings), and reconstructs electron candidates.
Usage:
    reco_trf.py -i input.ESD.root -o output.AOD.root
"""

app = typer.Typer()

@app.command()
def main(
    nov             : Annotated[List[int]   , 
                                typer.Option("--nov", "--number-of-events", 
                                help="The total number of events to run.")] = -1,
    logging_level   : Annotated[str         , 
                                typer.Option("-l", "--log-level", 
                                help="Logging verbosity.")] = "INFO",
    input_file      : Annotated[str | Path  , 
                                typer.Option("-i", "--input-file", 
                                help="The input file or folder to run the job.")],
    output_file     : Annotated[str | Path  , 
                                typer.Option("-o", "--output-file", 
                                help="The output file.")],
    preexec         : Annotated[str         , 
                                typer.Option("-p", "--preexec", 
                                help="The preexec command to run before the reconstruction.")] = "''",
):

    if isinstance(input_file, Path):
        input_file = str(input_file)
    if isinstance(output_file, Path):
        output_file = str(object=output_file)

    outputLevel = LoggingLevel.toC(logging_level)

    exec(preexec)

    acc = ComponentAccumulator("ComponentAccumulator", output_file)

    ESD = RootStreamESDReader(
        "ESDReader",
        InputFile=input_file,
        OutputCellsKey=recordable("Cells"),
        OutputCellsTruthKey=recordable("TruthCells"),
        OutputEventKey=recordable("Events"),
        OutputTruthKey=recordable("Particles"),
        OutputSeedsKey=recordable("Seeds"),
        OutputLevel=outputLevel,
    )
    ESD.merge(acc)

    cluster = CaloClusterMaker(
        "CaloClusterMaker",
        InputCellsKey=recordable("Cells"),
        InputSeedsKey=recordable("Seeds"),
        # output as
        OutputClusterKey=recordable("Clusters"),
        # other configs
        HistogramPath="Expert/Clusters",
        OutputLevel=outputLevel,
    )

    cluster_truth = CaloClusterMaker(
        "CaloClusterMaker_Truth",
        InputCellsKey=recordable("TruthCells"),
        InputSeedsKey=recordable("Seeds"),
        # output as
        OutputClusterKey=recordable("TruthClusters"),
        # other configs
        HistogramPath="Expert/TruthClusters",
        OutputLevel=outputLevel,
    )

    hypo = ElectronBuilderCfg(
        "ElectronBuilder",
        InputClusterKey=recordable("Clusters"),
        OutputElectronKey=recordable("Electrons"),
        OutputLevel=outputLevel,
    )

    hypo_truth = ElectronBuilderCfg(
        "ElectronBuilder_Truth",
        InputClusterKey=recordable("TruthClusters"),
        OutputElectronKey=recordable("TruthElectrons"),
        OutputLevel=outputLevel,
    )

    acc_rings = CaloRingsBuilderCfg(
            f"CaloRingsBuilder",
            InputClusterKey=recordable("Clusters"),
            OutputRingerKey=recordable("Rings"),
            HistogramPath=f"Expert/Rings",
            OutputLevel=outputLevel,
        )

    acc_rings_truth = CaloRingsBuilderCfg(
                f"CaloRingsBuilder_Truth",
                InputClusterKey=recordable("TruthClusters"),
                OutputRingerKey=recordable("TruthRings"),
                HistogramPath=f"Expert/TruthRings",
                OutputLevel=outputLevel,
        )

    AOD = RootStreamAODMaker(
        "RootStreamAODMaker",
        InputEventKey=recordable("Events"),
        InputSeedsKey=recordable("Seeds"),
        InputTruthKey=recordable("Particles"),
        InputCellsKey=recordable("Cells"),
        InputTruthCellsKey=recordable("TruthCells"),
        InputClusterKey=recordable("Clusters"),
        InputTruthClusterKey=recordable("TruthClusters"),
        InputRingerKeys=recordable("Rings"),
        InputTruthRingerKeys=recordable("TruthRings"),
        InputElectronKey=recordable("Electrons"),
        InputTruthElectronKey=recordable("TruthElectrons"),
        OutputLevel=outputLevel,
    )

    # sequence
    acc += cluster
    acc += acc_rings
    acc += acc_rings_truth
    acc += hypo
    acc += cluster_truth
    acc += hypo_truth
    acc += AOD
    acc.run(nov)


if __name__ == "__main__":
    app()