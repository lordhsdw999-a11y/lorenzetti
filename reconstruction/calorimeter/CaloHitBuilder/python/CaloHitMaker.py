"""
CaloHitMaker configuration helper.

Creates a Configurable instance for ROOT.CaloHitMaker bound to a specific detector sampling.
"""

from typing import Any, Optional
import ROOT

from GaugiKernel import LoggingLevel, Configurable
from GaugiKernel.macros import *

__all__ = ["CaloHitMakerCfg"]


def CaloHitMakerCfg(
    name: str,
    sampling: Any,
    OutputCollectionKey: str = "Hits",
    HistogramPath: str = "Expert",
    OutputLevel: int = LoggingLevel.toC("INFO"),
    DetailedHistograms: bool = False,
    SamplingNoiseStd: float = 0.0,
) -> Configurable:
    """
    Configures and returns a CaloHitMaker algorithm instance for a given calorimeter sampling.

    Args:
        name: Name of the algorithm instance.
        sampling: Calorimeter sampling descriptor object (from geometry configuration).
        OutputCollectionKey: SG key for the output hit collection.
        HistogramPath: Base path in histogram service.
        OutputLevel: Logging verbosity level.
        DetailedHistograms: If True, book and fill fine-grained diagnostic histograms.
        SamplingNoiseStd: Noise standard deviation (MeV) for time-of-flight thresholding.

    Returns:
        Configurable: Configured ROOT.CaloHitMaker algorithm wrapper.
    """
    return Configurable(
        ROOT.CaloHitMaker,
        name,
        OutputCollectionKey=OutputCollectionKey,
        HistogramPath=HistogramPath,
        OutputLevel=OutputLevel,
        DetailedHistograms=DetailedHistograms,
        SamplingNoiseStd=SamplingNoiseStd,
        EtaBins=sampling.sensitive().EtaBins,
        PhiBins=sampling.sensitive().PhiBins,
        RMin=sampling.volume().RMin,
        RMax=sampling.volume().RMax,
        ZMin=sampling.volume().ZMin,
        ZMax=sampling.volume().ZMax,
        Sampling=sampling.Sampling,
        Segment=sampling.sensitive().Segment,
        Detector=sampling.Detector,
        BunchIdStart=sampling.BunchIdStart,
        BunchIdEnd=sampling.BunchIdEnd,
        BunchDuration=25,
    )
