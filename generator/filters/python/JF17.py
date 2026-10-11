"""
JF17 jet filter configuration helper.

Provides JF17Cfg helper to configure ROOT.generator.JF17.
"""

from typing import Optional, Any
import ROOT

from GaugiKernel import Configurable, LoggingLevel

__all__ = ["JF17Cfg"]


def JF17Cfg(
    name: str = "JF17",
    gen: Any = None,
    EtaMax: float = 1.4,
    EtaMin: float = 0.0,
    MinPt: float = 0.0,
    Select: int = 2,
    OutputLevel: int = LoggingLevel.toC("INFO"),
    EtaWindow: float = 0.4,
    PhiWindow: float = 0.4,
    MaxEMFraction: float = 0.7,
    **kwargs
) -> Configurable:
    """
    Configures and returns a JF17 jet filter algorithm instance.

    Args:
        name: Name of the algorithm instance.
        gen: Primary event generator instance (e.g. Pythia8) providing .c_ptr().
        EtaMax: Maximum pseudorapidity for jet filtering.
        EtaMin: Minimum pseudorapidity for jet filtering.
        MinPt: Minimum transverse energy (Pt) for the filter.
        Select: Filter mode selection (default 2).
        OutputLevel: Logging verbosity level.
        EtaWindow: Jet cluster eta window.
        PhiWindow: Jet cluster phi window.
        MaxEMFraction: Maximum electromagnetic energy fraction.

    Returns:
        Configurable: Configured ROOT.generator.JF17 algorithm instance.
    """
    gen_ptr = gen.c_ptr() if hasattr(gen, "c_ptr") else gen
    cfg = Configurable(
        lambda n: ROOT.generator.JF17(n, gen_ptr),
        name,
        EtaMax=EtaMax,
        EtaMin=EtaMin,
        MinPt=MinPt,
        Select=Select,
        OutputLevel=OutputLevel,
        EtaWindow=EtaWindow,
        PhiWindow=PhiWindow,
        MaxEMFraction=MaxEMFraction,
        **kwargs
    )
    return cfg
