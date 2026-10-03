__all__ = ["ElectronBuilder", "ElectronBuilderCfg", "ElectronWorkingPoint"]

from typing import List
import ROOT
from GaugiKernel import Configurable, EnumStringification


class ElectronWorkingPoint(EnumStringification):
    """
    Standard operating points for electron identification.
    """
    VeryLoose = "vloose"
    Loose     = "loose"
    Medium    = "medium"
    Tight     = "tight"


def getIsEMCuts(wpname: str) -> List[float]:
    """
    Returns rectangular cut thresholds for central electron identification.

    :param wpname: Working point ('loose', 'medium', 'tight', 'vloose').
    :return: List of [etHadCut, rEtaCut, eRatioCut].
    """
    etHadCut = {
        "loose": [0.1218],
        "medium": [0.0270375],
        "tight": [0.0270375],
        "vloose": [0.157],
    }

    rEtaCut = {
        "loose": [0.57],
        "medium": [0.814625],
        "tight": [0.83125],
        "vloose": [0.752],
    }

    eRatioCut = {
        "loose": [0.47],
        "medium": [0.57],
        "tight": [0.65],
        "vloose": [0.52],
    }

    return [etHadCut[wpname][0], rEtaCut[wpname][0], eRatioCut[wpname][0]]


def ElectronBuilderCfg(
    name: str,
    InputClusterKey: str,
    OutputElectronKey: str,
    OutputLevel: int = 0,
    HistogramPath: str = "Expert/Electrons",
) -> Configurable:
    """
    Configures the ElectronMaker algorithm for electron candidate reconstruction and PID.

    :param name: Name of the ElectronMaker algorithm instance.
    :param InputClusterKey: StoreGate key of the input xAOD::CaloClusterContainer.
    :param OutputElectronKey: StoreGate key for the output xAOD::ElectronContainer.
    :param OutputLevel: Verbosity logging level.
    :param HistogramPath: Path in StoreGate for histogram booking.
    :return: Configurable algorithm instance.
    """
    return Configurable(
        ROOT.ElectronMaker,
        name,
        InputClusterKey=InputClusterKey,
        OutputElectronKey=OutputElectronKey,
        OutputLevel=OutputLevel,
        HistogramPath=HistogramPath,
        # Central cuts
        TightCuts=getIsEMCuts("tight"),
        MediumCuts=getIsEMCuts("medium"),
        LooseCuts=getIsEMCuts("loose"),
        VLooseCuts=getIsEMCuts("vloose"),
        # Forward cuts
        SecondLambdaCuts=[4500.0, 4500.0, 2800.0],
        LateralMomCuts=[0.69, 0.64, 0.64],
        LongMomCuts=[0.55, 0.29, 0.24],
        FracMaxCuts=[0.22, 0.23, 0.39],
        SecondRCuts=[3900.0, 3300.0, 3000.0],
        LambdaCenterCuts=[255.0, 255.0, 250.0],
    )


ElectronBuilder = ElectronBuilderCfg
