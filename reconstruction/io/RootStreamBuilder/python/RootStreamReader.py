__all__ = [
    "RootStreamReader",
    "RootStreamReaderCfg",
    "RootStreamAODReader",
    "RootStreamAODReaderCfg",
    "RootStreamESDReader",
    "RootStreamESDReaderCfg",
    "RootStreamHITReader",
    "RootStreamHITReaderCfg",
]

import ROOT
from typing import Optional
from GaugiKernel import Configurable


def RootStreamReaderCfg(
    name: str = "RootStreamReader",
    InputFile: str = "",
    TreeName: str = "CollectionTree",
    FilterBySigma: bool = False,
    SigmaThreshold: float = 2.0,
    DescriptorsKey: str = "CaloDetDescriptors",
    OutputLevel: int = 0,
) -> Configurable:
    """
    Creates an auto-discovery RootStreamReader algorithm.
    It inspects all <TypeName>_<Key> branches from the input ROOT TTree,
    instantiates the matching converters, and reconstructs the xAOD containers
    directly into the EventContext with their respective keys.

    :param name: Algorithm name.
    :param InputFile: Path to input ROOT file (optional if managed by EventLoop).
    :param TreeName: Name of the TTree inside the ROOT file.
    :param FilterBySigma: Enable online 2-sigma noise cell filtering (ATLAS Run 4).
    :param SigmaThreshold: Threshold multiplier for noise cut (default: 2.0).
    :param DescriptorsKey: StoreGate key for master CaloDetDescriptorContainer.
    :param OutputLevel: Verbosity level (0=INFO, 1=DEBUG, etc.).
    """
    return Configurable(
        ROOT.RootStreamReader,
        name=name,
        InputFile=InputFile,
        TreeName=TreeName,
        FilterBySigma=FilterBySigma,
        SigmaThreshold=SigmaThreshold,
        DescriptorsKey=DescriptorsKey,
        OutputLevel=OutputLevel,
    )


RootStreamReader = RootStreamReaderCfg


def RootStreamAODReaderCfg(
    name: str = "RootStreamAODReader",
    InputFile: str = "",
    TreeName: str = "CollectionTree",
    OutputLevel: int = 0,
    **_kwargs,
) -> Configurable:
    """
    Auto-discovery reader preset for AOD files (compatible with legacy scripts).
    """
    return RootStreamReaderCfg(
        name=name,
        InputFile=InputFile,
        TreeName=TreeName,
        OutputLevel=OutputLevel,
    )


RootStreamAODReader = RootStreamAODReaderCfg


def RootStreamESDReaderCfg(
    name: str = "RootStreamESDReader",
    InputFile: str = "",
    TreeName: str = "CollectionTree",
    FilterBySigma: bool = False,
    SigmaThreshold: float = 2.0,
    DescriptorsKey: str = "CaloDetDescriptors",
    OutputLevel: int = 0,
    **_kwargs,
) -> Configurable:
    """
    Auto-discovery reader preset for ESD files (compatible with legacy scripts).
    Supports optional online noise sigma cell filtering (ATLAS Run 4).
    """
    return RootStreamReaderCfg(
        name=name,
        InputFile=InputFile,
        TreeName=TreeName,
        FilterBySigma=FilterBySigma,
        SigmaThreshold=SigmaThreshold,
        DescriptorsKey=DescriptorsKey,
        OutputLevel=OutputLevel,
    )


RootStreamESDReader = RootStreamESDReaderCfg


def RootStreamHITReaderCfg(
    name: str = "RootStreamHITReader",
    InputFile: str = "",
    TreeName: str = "CollectionTree",
    OutputLevel: int = 0,
    **_kwargs,
) -> Configurable:
    """
    Auto-discovery reader preset for HIT files (compatible with legacy scripts).
    """
    return RootStreamReaderCfg(
        name=name,
        InputFile=InputFile,
        TreeName=TreeName,
        OutputLevel=OutputLevel,
    )


RootStreamHITReader = RootStreamHITReaderCfg
