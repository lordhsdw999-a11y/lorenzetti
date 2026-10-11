"""
Pythia8 generator configuration helper.

Provides the Pythia8Cfg helper to configure ROOT.generator.Pythia8Gen.
"""

from typing import Optional
import ROOT

from GaugiKernel import Configurable, LoggingLevel

__all__ = ["Pythia8Cfg"]


def Pythia8Cfg(
    name: str = "Pythia8",
    File: str = "",
    Seed: int = 512,
    OutputLevel: int = LoggingLevel.toC("INFO"),
    **kwargs
) -> Configurable:
    """
    Configures and returns a Pythia8 generator instance.

    Args:
        name: Name of the generator instance.
        File: Path to external Pythia configuration/command file (e.g. .cmnd).
        Seed: Random seed for Pythia generation.
        OutputLevel: Logging verbosity level.

    Returns:
        Configurable: Configured ROOT.generator.Pythia8Gen instance.
    """
    return Configurable(
        ROOT.generator.Pythia8Gen,
        name,
        File=File,
        Seed=Seed,
        OutputLevel=OutputLevel,
        **kwargs
    )

