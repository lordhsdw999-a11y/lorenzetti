__all__ = [
    "RootStreamMaker",
    "RootStreamMakerCfg",
    "RootStreamAODMaker",
    "RootStreamAODMakerCfg",
    "RootStreamESDMaker",
    "RootStreamESDMakerCfg",
    "RootStreamHITMaker",
    "RootStreamHITMakerCfg",
]

import ROOT
from typing import List, Optional
from GaugiKernel import Configurable
from RootStreamBuilder import RootStreamAODFlags


def RootStreamMakerCfg(
    name: str = "RootStreamMaker",
    ItemList: Optional[List[str]] = None,
    TreeName: str = "CollectionTree",
    OutputLevel: int = 0,
) -> Configurable:
    """
    Creates a generic RootStreamMaker algorithm that serializes any requested
    xAOD containers into branches of format <TypeName>_<Key> inside a TTree.

    :param name: Algorithm name.
    :param ItemList: List of items to record, formatted as 'TypeName#Key' (e.g. 'CaloClusterContainer#CaloClusters').
    :param TreeName: Name of the output TTree.
    :param OutputLevel: Verbosity level (0=INFO, 1=DEBUG, etc.).
    """
    if ItemList is None:
        ItemList = []

    return Configurable(
        ROOT.RootStreamMaker,
        name=name,
        ItemList=ItemList,
        TreeName=TreeName,
        OutputLevel=OutputLevel,
    )


RootStreamMaker = RootStreamMakerCfg


def RootStreamAODMakerCfg(
    name: str = "RootStreamAODMaker",
    InputEventKey: str = "EventInfo",
    InputTruthKey: str = "Particles",
    InputCellsKey: str = "Cells",
    InputClusterKey: str = "CaloClusters",
    InputRingerKeys: Optional[List[str]] = None,
    InputElectronKey: str = "Electrons",
    InputTruthCellsKey: str = "TruthCells",
    InputTruthClusterKey: str = "TruthClusters",
    InputTruthRingerKeys: Optional[List[str]] = None,
    InputTruthElectronKey: str = "TruthElectrons",
    TreeName: str = "CollectionTree",
    OutputLevel: int = 0,
    DumpCells: bool = RootStreamAODFlags.DumpCells,
) -> Configurable:
    """
    Convenience preset configuring a RootStreamMaker for AOD tier output.
    """
    if InputRingerKeys is None:
        InputRingerKeys = ["Rings"]
    if InputTruthRingerKeys is None:
        InputTruthRingerKeys = ["TruthRings"]

    item_list: List[str] = [
        f"EventInfoContainer#{InputEventKey}",
        f"TruthParticleContainer#{InputTruthKey}",
        f"CaloClusterContainer#{InputClusterKey}",
        f"ElectronContainer#{InputElectronKey}",
        f"CaloClusterContainer#{InputTruthClusterKey}",
        f"ElectronContainer#{InputTruthElectronKey}",
    ]

    for key in InputRingerKeys:
        item_list.append(f"CaloRingsContainer#{key}")

    for key in InputTruthRingerKeys:
        item_list.append(f"CaloRingsContainer#{key}")

    if DumpCells:
        item_list.append(f"CaloCellContainer#{InputCellsKey}")
        item_list.append(f"CaloCellContainer#{InputTruthCellsKey}")

    return RootStreamMakerCfg(
        name=name,
        ItemList=item_list,
        TreeName=TreeName,
        OutputLevel=OutputLevel,
    )


RootStreamAODMaker = RootStreamAODMakerCfg


def RootStreamESDMakerCfg(
    name: str = "RootStreamESDMaker",
    InputEventKey: str = "EventInfo",
    InputTruthKey: str = "Particles",
    InputSeedsKey: str = "Seeds",
    InputCellsKey: str = "Cells",
    InputTruthCellsKey: str = "TruthCells",
    InputClusterKey: str = "CaloClusters",
    InputTruthClusterKey: str = "TruthClusters",
    TreeName: str = "CollectionTree",
    OutputLevel: int = 0,
) -> Configurable:
    """
    Convenience preset configuring a RootStreamMaker for ESD tier output.
    """
    item_list: List[str] = [
        f"EventInfoContainer#{InputEventKey}",
        f"TruthParticleContainer#{InputTruthKey}",
        f"SeedContainer#{InputSeedsKey}",
        f"CaloCellContainer#{InputCellsKey}",
        f"CaloCellContainer#{InputTruthCellsKey}",
        f"CaloClusterContainer#{InputClusterKey}",
        f"CaloClusterContainer#{InputTruthClusterKey}",
    ]

    return RootStreamMakerCfg(
        name=name,
        ItemList=item_list,
        TreeName=TreeName,
        OutputLevel=OutputLevel,
    )


RootStreamESDMaker = RootStreamESDMakerCfg


def RootStreamHITMakerCfg(
    name: str = "RootStreamHITMaker",
    InputEventKey: str = "EventInfo",
    InputTruthKey: str = "Particles",
    InputHitsKey: str = "Hits",
    InputSeedsKey: str = "Seeds",
    TreeName: str = "CollectionTree",
    OutputLevel: int = 0,
) -> Configurable:
    """
    Convenience preset configuring a RootStreamMaker for HIT tier output.
    """
    item_list: List[str] = [
        f"EventInfoContainer#{InputEventKey}",
        f"TruthParticleContainer#{InputTruthKey}",
        f"CaloHitContainer#{InputHitsKey}",
        f"SeedContainer#{InputSeedsKey}",
    ]

    return RootStreamMakerCfg(
        name=name,
        ItemList=item_list,
        TreeName=TreeName,
        OutputLevel=OutputLevel,
    )


RootStreamHITMaker = RootStreamHITMakerCfg
