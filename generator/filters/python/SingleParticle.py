"""
SingleParticle filter configuration helper.

Provides SingleParticleCfg helper to configure ROOT.generator.SingleParticle.
"""

from typing import Any
import ROOT

from GaugiKernel import Configurable, LoggingLevel, EnumStringification
from GaugiKernel.constants import GeV

__all__ = ["SingleParticleCfg", "Particle"]


class Particle(EnumStringification):
    Electron = 11
    Photon = 22
    PiPlus = 211
    PiZero = 111
    Neutrino = 12


def SingleParticleCfg(
    name: str = "SingleParticle",
    gen: Any = None,
    Eta: float = 0.0,
    Phi: float = 0.0,
    Particle: int = Particle.Electron,
    Energy: float = -1.0,
    EnergyMin: float = 0.0 * GeV,
    EnergyMax: float = 100.0 * GeV,
    HasLifetime: bool = False,
    AtRest: bool = False,
    DoRangedEta: bool = False,
    EtaMin: float = -2.5,
    EtaMax: float = 2.5,
    DoRangedPhi: bool = False,
    PhiMin: float = -3.14,
    PhiMax: float = 3.14,
    OutputLevel: int = LoggingLevel.toC("INFO"),
    **kwargs
) -> Configurable:
    """
    Configures and returns a SingleParticle generator filter instance.
    """
    gen_ptr = gen.c_ptr() if hasattr(gen, "c_ptr") else gen
    return Configurable(
        lambda n: ROOT.generator.SingleParticle(n, gen_ptr),
        name,
        Eta=Eta,
        Phi=Phi,
        Particle=Particle,
        Energy=Energy,
        EnergyMin=EnergyMin,
        EnergyMax=EnergyMax,
        HasLifetime=HasLifetime,
        AtRest=AtRest,
        DoRangedEta=DoRangedEta,
        EtaMin=EtaMin,
        EtaMax=EtaMax,
        DoRangedPhi=DoRangedPhi,
        PhiMin=PhiMin,
        PhiMax=PhiMax,
        OutputLevel=OutputLevel,
        **kwargs
    )
