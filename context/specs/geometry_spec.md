# 📐 Geometry & Calorimeter Construction Specification (`geometry/`)

> **Status:** Active Specification  
> **Location:** [geometry/](file:///home/joao.pinto/git_repos/lorenzetti/geometry)  
> **Subpackages:** `src`, `python/v1`, `data`, `scripts`

---

## 1. Calorimeter Geometry Architecture

Lorenzetti models a high-granularity $4\pi$ cylindrical calorimeter detector inspired by modern LHC experiments (ATLAS-style).

```
geometry/
├── src/           # C++ Geant4 DetectorConstruction, SensitiveDetector attachments
├── python/v1/     # Python geometry builder (ECAL, HCAL, segmentation parameters)
├── data/          # GDML models and material property definitions
└── scripts/       # Visualization tools (run_vis.py)
```

---

## 2. Calorimeter Subsystems & Layer Layout

```
                                    BEAM PIPE (z-axis)
══════════════════════════════════════════════════════════════════════════
  Layer 0: Pre-Sampler (PS)       ── Thin active layer (upstream energy correction)
  Layer 1: Front / Strips (EM1)   ── Ultra-fine Δη segmentation (pi0 / gamma separation)
  Layer 2: Middle (EM2)           ── Deep sampling (main EM shower energy deposit)
  Layer 3: Back (EM3)             ── EM leakage & tail catcher
──────────────────────────────────────────────────────────────────────────
  Hadronic Calorimeter (TileCal / HEC) ── Scintillator/Fe or LAr/Cu (Jets & MET)
```

### 2.1. Granularity & Material Specifications

| Subsystem | Layer ID | Layer Name | Absorber / Active | $\Delta\eta \times \Delta\phi$ Granularity | $\eta$ Acceptance |
| :--- | :---: | :--- | :--- | :---: | :---: |
| **ECAL (Barrel)** | 0 | Pre-Sampler | LAr / Pb | $0.025 \times 0.100$ | $|\eta| < 1.52$ |
| | 1 | Front (Strips) | LAr / Pb | $0.003125 \times 0.100$ | $|\eta| < 1.40$ |
| | 2 | Middle | LAr / Pb | $0.025 \times 0.025$ | $|\eta| < 1.475$ |
| | 3 | Back | LAr / Pb | $0.050 \times 0.025$ | $|\eta| < 1.35$ |
| **TileCal (Barrel)** | 1 | Front | Fe / Scintillator | $0.100 \times 0.100$ | $|\eta| < 1.0$ |
| | 2 | Middle | Fe / Scintillator | $0.100 \times 0.100$ | $|\eta| < 1.0$ |
| | 3 | Back | Fe / Scintillator | $0.200 \times 0.100$ | $|\eta| < 1.0$ |
| **EMEC (Endcap)** | 0-3 | Endcap EM | LAr / Pb | Varies ($0.025 \to 0.100$) | $1.375 < |\eta| < 3.2$ |
| **HEC (Endcap)** | 1-3 | Endcap Hadronic | LAr / Cu | $0.100 \times 0.100 / 0.200 \times 0.200$ | $1.5 < |\eta| < 3.2$ |

---

## 3. `CaloDetDescriptor` Specification

Every readout cell is indexed by a `CaloDetDescriptor` defining its:
- `caloSampling()`: Layer ID enum (`EMB0`, `EMB1`, `EMB2`, `EMB3`, `EME1`, `TileBar0`, etc.)
- `etaMin()`, `etaMax()`, `dEta()`: Pseudorapidity bounds and granularity
- `phiMin()`, `phiMax()`, `dPhi()`: Azimuthal bounds and granularity
- `rMin()`, `rMax()`, `zMin()`, `zMax()`: Physical radial and longitudinal extents in mm
- `nEta()`, `nPhi()`: Cell grid matrix dimensions

---

## 4. Python Geometry Builder API

```python
from typing import Dict, List, Optional
from GaugiKernel import Logger

class ECAL(Logger):
    def __init__(
        self,
        name: str = "ECAL",
        eta_max: float = 2.5,
        phi_max: float = 3.14159,
        active_material: str = "G4_lAr",
        absorber_material: str = "G4_Pb"
    ) -> None:
        """
        Builds Electromagnetic Calorimeter barrel and endcap volumes.

        Args:
            name (str): Detector volume name.
            eta_max (float): Maximum absolute eta acceptance.
            phi_max (float): Maximum phi angle.
            active_material (str): Geant4 material name for active medium.
            absorber_material (str): Geant4 material name for absorber.
        """
        super().__init__(name)
        ...
```
