"""
Digitization configuration flags for calorimeter cell reconstruction.
"""

from GaugiKernel import EnumStringification
from GaugiKernel.constants import GeV

__all__ = ["CaloFlags", "CrossTalkFlags", "AnomalyFlags"]


class CaloFlags(EnumStringification):
    """
    Global steering flags for calorimeter digitization.
    """
    SamplingnoiseStd: float = 0.0
    DoCrossTalk: bool = False
    DoCOF: bool = False
    DoDefects: bool = False


class CrossTalkFlags(EnumStringification):
    """
    Steering flags for cross-talk simulation between neighboring calorimeter cells.
    """
    MinEnergy: float = 1.0 * GeV
    AmpCapacitive: float = 4.2
    AmpInductive: float = 2.3
    AmpResistive: float = 1.0


class AnomalyFlags(EnumStringification):
    """
    Configuration flags for detector defects and anomalies.
    """
    BadRunListFile: str = ""