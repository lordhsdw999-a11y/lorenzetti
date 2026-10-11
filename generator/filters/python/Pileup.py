"""
Pileup filter configuration helper.

Provides PileupCfg helper to configure ROOT.generator.Pileup.
"""

from typing import Any
import ROOT

from GaugiKernel import Configurable, LoggingLevel

__all__ = ["PileupCfg"]


def PileupCfg(
    name: str = "Pileup",
    gen: Any = None,
    EtaMax: float = 1.4,
    PileupAvg: float = 0.0,
    PileupSigma: float = 0.0,
    PileupPerBunch: float = -1.0,
    BunchIdStart: int = -8,
    BunchIdEnd: int = 7,
    Select: int = 2,
    DeltaEta: float = 0.22,
    DeltaPhi: float = 0.22,
    OutputLevel: int = LoggingLevel.toC("INFO"),
    **kwargs
) -> Configurable:
    """
    Configures and returns a Pileup filter algorithm instance.
    """
    gen_ptr = gen.c_ptr() if hasattr(gen, "c_ptr") else gen
    return Configurable(
        lambda n: ROOT.generator.Pileup(n, gen_ptr),
        name,
        EtaMax=EtaMax,
        PileupAvg=PileupAvg,
        PileupSigma=PileupSigma,
        PileupPerBunch=PileupPerBunch,
        BunchIdStart=BunchIdStart,
        BunchIdEnd=BunchIdEnd,
        Select=Select,
        DeltaEta=DeltaEta,
        DeltaPhi=DeltaPhi,
        OutputLevel=OutputLevel,
        **kwargs
    )
