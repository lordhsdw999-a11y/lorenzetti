"""
CaloCellMaker configuration helper.

Creates a Configurable instance for ROOT.CaloCellMaker for a specific detector sampling.
"""

from typing import Any
import ROOT

from GaugiKernel import Configurable, LoggingLevel

__all__ = ["CaloCellMakerCfg"]


def CaloCellMakerCfg(
    name: str,
    sampling: Any,
    InputHitsKey: str = "Hits",
    OutputCollectionKey: str = "Collection",
    OutputLevel: int = LoggingLevel.toC("INFO"),
    DetailedHistograms: bool = False,
    HistogramPath: str = "/Hists/Cells",
) -> Configurable:
    """
    Configures and returns a CaloCellMaker algorithm instance for a given calorimeter sampling.

    Args:
        name: Name of the algorithm instance.
        sampling: Calorimeter sampling descriptor object (from geometry configuration).
        InputHitsKey: SG key for input hits container.
        OutputCollectionKey: SG key for output descriptor collection.
        OutputLevel: Logging verbosity level.
        DetailedHistograms: If True, book fine-grained diagnostic histograms.
        HistogramPath: Base path in histogram service.

    Returns:
        Configurable: Configured ROOT.CaloCellMaker algorithm wrapper.
    """
    return Configurable(
        ROOT.CaloCellMaker,
        name,
        InputHitsKey=InputHitsKey,
        OutputCollectionKey=OutputCollectionKey,
        OutputLevel=OutputLevel,
        DetailedHistograms=DetailedHistograms,
        HistogramPath=HistogramPath,
        EtaBins=sampling.sensitive().EtaBins,
        PhiBins=sampling.sensitive().PhiBins,
        ZMin=sampling.volume().ZMin,
        ZMax=sampling.volume().ZMax,
        Z=sampling.sv.pv.Z,
        Sampling=sampling.Sampling,
        Segment=sampling.sensitive().Segment,
        Detector=sampling.Detector,
        BunchIdStart=sampling.BunchIdStart,
        BunchIdEnd=sampling.BunchIdEnd,
        BunchDuration=25,
    )
