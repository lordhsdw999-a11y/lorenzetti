"""
OverlappedEvents filter configuration helper.

Provides OverlappedEventsCfg helper to configure ROOT.generator.OverlappedEvents.
"""

from typing import Any
import ROOT

from GaugiKernel import Configurable, LoggingLevel
from GaugiKernel.constants import GeV
from filters.SingleParticle import Particle

__all__ = ["OverlappedEventsCfg"]


def OverlappedEventsCfg(
    name: str = "OverlappedEvents",
    gen: Any = None,
    Particle: int = Particle.Electron,
    Energy: float = 1.0 * GeV,
    DeltaR: float = 0.2,
    HasLifetime: bool = False,
    AtRest: bool = False,
    OutputLevel: int = LoggingLevel.toC("INFO"),
    **kwargs
) -> Configurable:
    """
    Configures and returns an OverlappedEvents filter algorithm instance.
    """
    gen_ptr = gen.c_ptr() if hasattr(gen, "c_ptr") else gen
    return Configurable(
        lambda n: ROOT.generator.OverlappedEvents(n, gen_ptr),
        name,
        Particle=Particle,
        Energy=Energy,
        DeltaR=DeltaR,
        HasLifetime=HasLifetime,
        AtRest=AtRest,
        OutputLevel=OutputLevel,
        **kwargs
    )
