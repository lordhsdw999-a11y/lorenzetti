"""
Configuration flags for calorimeter cluster reconstruction.
"""

from GaugiKernel import EnumStringification
from GaugiKernel.constants import GeV

__all__ = ["CaloClusterFlags"]


class CaloClusterFlags(EnumStringification):
    """
    Steering flags for seeded calorimeter cluster reconstruction and moments computation.
    """
    MinCenterEnergy: float = 1.0 * GeV
    EtaWindow: float = 0.4
    PhiWindow: float = 0.4
    DoForwardMoments: bool = False