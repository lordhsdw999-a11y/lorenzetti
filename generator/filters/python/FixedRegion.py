"""
FixedRegion filter configuration helper.

Provides FixedRegionCfg helper to configure ROOT.generator.FixedRegion.
"""

import ROOT

from GaugiKernel import Configurable, LoggingLevel

__all__ = ["FixedRegionCfg"]


def FixedRegionCfg(
    name: str = "FixedRegion",
    Eta: float = 0.0,
    Phi: float = 0.0,
    OutputLevel: int = LoggingLevel.toC("INFO"),
    **kwargs
) -> Configurable:
    """
    Configures and returns a FixedRegion algorithm instance.
    """
    return Configurable(
        lambda n: ROOT.generator.FixedRegion(n),
        name,
        Eta=Eta,
        Phi=Phi,
        OutputLevel=OutputLevel,
        **kwargs
    )
