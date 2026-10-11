"""
Zee filter configuration helper.

Provides ZeeCfg helper to configure ROOT.generator.Zee.
"""

from typing import Any
import ROOT

from GaugiKernel import Configurable, LoggingLevel

__all__ = ["ZeeCfg"]


def ZeeCfg(
    name: str = "Zee",
    gen: Any = None,
    EtaMax: float = 1.4,
    MinPt: float = 0.0,
    ZeroVertexParticles: bool = False,
    ForceForwardElectron: bool = False,
    OutputLevel: int = LoggingLevel.toC("INFO"),
    **kwargs
) -> Configurable:
    """
    Configures and returns a Zee filter algorithm instance.
    """
    gen_ptr = gen.c_ptr() if hasattr(gen, "c_ptr") else gen
    return Configurable(
        lambda n: ROOT.generator.Zee(n, gen_ptr),
        name,
        EtaMax=EtaMax,
        MinPt=MinPt,
        ZeroVertexParticles=ZeroVertexParticles,
        ForceForwardElectron=ForceForwardElectron,
        OutputLevel=OutputLevel,
        **kwargs
    )
