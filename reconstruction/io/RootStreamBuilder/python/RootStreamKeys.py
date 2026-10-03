__all__ = ["recordable", "valid_keys"]

valid_keys = [
    "EventInfo",
    "Hits",
    # CaloCellMerge
    "Cells",
    "TruthCells",
    # CaloClusterMaker
    "Events",
    "Seeds",
    "Clusters",
    "TruthClusters",
    "Particles",
    "TruthParticles",
    # CaloRingsBuilder
    "Rings",
    "RingsSigmaNoise",
    "TruthRings",
    "AsymRings",
    "TruthAsymRings",
    "CornerRings",
    "TruthCornerRings",
    "StripsRings",
    "TruthStripsRings",
    "CrossRings",
    "TruthCrossRings",
    "CustomRings",
    "TruthCustomRings",
    "Electrons",
    "TruthElectrons",
    "RingsL0",
    "TruthRingsL0",
]


def recordable(key: str) -> str:
    if key not in valid_keys:
        raise RuntimeError(f"Key {key} is not allowed to be recorded.")
    return key
