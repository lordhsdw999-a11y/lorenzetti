"""
PulsePerturber module for defect and anomaly injection into simulated calorimeter pulses.
"""

from typing import Any, Dict, List, Set
import json
import ROOT

from GaugiKernel import Configurable, LoggingLevel

__all__ = ["PulsePerturberCfg", "get_cells_from_brl"]


def get_cells_from_brl(path: str) -> Set[int]:
    """
    Parses a Bad Run List (BRL) JSON file and extracts unique cell IDs.

    Args:
        path: Path to the Bad Run List JSON file.

    Returns:
        Set of cell hash identifiers.
    """
    with open(path, "r", encoding="utf-8") as f:
        d: Dict[str, Any] = json.load(f)
        cells: List[int] = []
        for run in d.get("runs", []):
            if not run.get("DeadModules", False):
                cells.extend(run.get("Cells", []))
        return set(cells)


def PulsePerturberCfg(
    name: str,
    BadRunListFile: str,
    OutputLevel: int = LoggingLevel.toC("INFO"),
    NoiseMean: float = 0.0,
    NoiseStd: float = 0.0,
    InputEventKey: str = "Events",
) -> Configurable:
    """
    Creates and configures a PulsePerturber tool instance from a Bad Run List file.

    Args:
        name: Name of the tool instance.
        BadRunListFile: Path to the Bad Run List JSON configuration.
        OutputLevel: Logging verbosity level.
        NoiseMean: Mean noise to inject.
        NoiseStd: Standard deviation of injected noise.
        InputEventKey: StoreGate key for event information.

    Returns:
        Configurable instance of ROOT.PulsePerturber.
    """
    with open(BadRunListFile, "r", encoding="utf-8") as f:
        d: Dict[str, Any] = json.load(f)
        events: List[List[int]] = []
        dead_modules: List[bool] = []
        noise_factor: List[float] = []
        cells: List[List[int]] = []
        for run in d.get("runs", []):
            events.append([run["StartEventNumber"], run["EndEventNumber"]])
            dead_modules.append(run["DeadModules"])
            noise_factor.append(run["NoiseStdFactor"])
            cells.append(run["Cells"])

        return Configurable(
            ROOT.PulsePerturber,
            name,
            OutputLevel=OutputLevel,
            NoiseMean=NoiseMean,
            NoiseStd=NoiseStd,
            InputEventKey=InputEventKey,
            DeadModules=dead_modules,
            Cells=cells,
            NoiseStdFactor=noise_factor,
            EventNumberRange=events,
        )
