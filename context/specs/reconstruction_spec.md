# 🔬 Reconstruction & Signal Processing Specification (`reconstruction/`)

> **Status:** Active Specification  
> **Location:** [reconstruction/](file:///home/joao.pinto/git_repos/lorenzetti/reconstruction)  
> **Subpackages:** `calorimeter`, `physics`, `io`, `reco`, `tracking`

---

## 1. Package Overview

The `reconstruction/` package houses the algorithmic core of Lorenzetti: transforming raw Geant4 energy hits into electronic pulse shapes, reconstructing digitized cell energies via Optimal Filtering, clustering cells, computing Ringer rings, identifying physics objects, and reading/writing ROOT streams.

```
reconstruction/
├── calorimeter/
│   ├── CaloHitBuilder/       # Geant4 hit aggregation into sampling containers
│   ├── CaloCellBuilder/      # Pulse shaping, electronic noise, cross-talk, defects, OF/COF reconstruction
│   ├── CaloClusterBuilder/   # Sliding window & topological clustering
│   └── CaloRingsBuilder/     # Concentric ring energy extraction per layer
├── physics/
│   └── EgammaBuilder/        # Electron / photon candidate reconstruction & PID
├── tracking/                 # SpacePoint reconstruction
└── reco/
    ├── python/               # Job configuration (gen_job.py, reco_job.py)
    └── scripts/              # Transform scripts (simu_trf, digit_trf, merge_trf, reco_trf, ntuple_trf, prun)
```

---

## 2. Calorimeter Digitization Chain (`CaloCellBuilder`)

The digitization pipeline converts simulated step energy deposits into reconstructed cell four-momenta:

```
[Geant4 Hits]
     │
     ▼
[1. Pulse Generator] ─── Convolve hits with shaper response g(t) across bunch crossings
     │
     ▼
[2. Noise Injector] ──── Add Gaussian electronic noise ~ N(0, σ_noise)
     │
     ▼
[3. Cross-Talk] ──────── Capacitive, inductive, and resistive leakage to neighbors
     │
     ▼
[4. Pulse Perturber] ─── Inject hardware defects (dead cells, noisy channels, hot towers)
     │
     ▼
[5. Optimal Filtering] ── Apply OF/COF weights: E = Σ a_i S_i,  t = (1/E) Σ b_i S_i
     │
     ▼
[6. Cell Merging] ────── Combine all samplings into master CaloCellContainer
```

### 2.1. Mathematical Foundations
- **Pulse Shape**: $S(t) = \sum_k E_k \cdot g(t - t_k) + n(t)$
- **Optimal Filtering (OF)**:
  $$E = \sum_{i=1}^N a_i S_i, \quad E \tau = \sum_{i=1}^N b_i S_i$$
  where weights $a_i$ and $b_i$ minimize variance $\text{Var}(E)$ subject to $\sum a_i g_i = 1$ and $\sum a_i g'_i = 0$.

### 2.2. Configuration Flags
- **`CaloFlags`**: `SamplingnoiseStd`, `DoCrossTalk`, `DoCOF`, `DoDefects`.
- **`CrossTalkFlags`**: `AmpCapacitive`, `AmpInductive`, `AmpResistive`, `MinEnergy`.
- **`AnomalyFlags`**: `BadRunListFile` (specifying cell hashes, run numbers, and defect types).

---

## 3. Clustering & Ringer Rings

### 3.1. `CaloClusterBuilder`
- **Sliding Window**: Searches for seed towers exceeding a threshold $E_T$, building clusters of size $\Delta\eta \times \Delta\phi$ (e.g., $3 \times 7$ in barrel, $5 \times 5$ in endcap).
- Computes barycenter coordinates $(\eta_{\text{cluster}}, \phi_{\text{cluster}})$ and total cluster energy.

### 3.2. `CaloRingsBuilder`
- Constructs concentric rings around the cluster centroid for each calorimeter layer.
- Ring width $\Delta R = 0.025$ in middle/back layers, fine sub-strip rings in EM1.
- Generates standard 100-dimensional feature vectors used for Fast Triggering and Offline Machine Learning classifiers.

---

## 4. Transform Scripts & Execution Sequence (`*_trf.py`)

All transforms must follow strict CLI signatures:

| Transform | Input File | Output File | Description |
| :--- | :--- | :--- | :--- |
| **`simu_trf.py`** | `EVT.root` | `HIT.root` | Geant4 detector shower simulation |
| **`merge_trf.py`** | Signal `HIT.root` + Minbias `HIT.root` | `merged.HIT.root` | In-time and out-of-time pileup overlay |
| **`digit_trf.py`** | `HIT.root` | `ESD.root` | Electronic pulse shaping, noise, defects, and OF cell reconstruction |
| **`reco_trf.py`** | `ESD.root` | `AOD.root` | Cluster reconstruction, ring construction, e/gamma building |
| **`ntuple_trf.py`**| `AOD.root` | `NTUPLE.root` | Export flat ROOT TTree for ML / Python analysis |

---

## 5. Python Transform Interface Specification

```python
import typer
from typing import Optional

app = typer.Typer(
    name="digit_trf",
    help="**Digitization Transform: Converts HIT.root to ESD.root**",
    add_completion=False
)

@app.command()
def digitize(
    input_file: str = typer.Option(..., "-i", "--input-file", help="Path to input `HIT.root` file."),
    output_file: str = typer.Option(..., "-o", "--output-file", help="Path to output `ESD.root` file."),
    num_events: int = typer.Option(-1, "-nt", "--num-events", help="Number of events to digitize."),
    noise_sigma: float = typer.Option(0.0, "--noise-sigma", help="Electronic noise standard deviation."),
    enable_crosstalk: bool = typer.Option(False, "--enable-crosstalk", help="Enable cross-talk modeling."),
    enable_defects: bool = typer.Option(False, "--enable-defects", help="Enable defect injection."),
    bad_run_list: Optional[str] = typer.Option(None, "--bad-run-list", help="Path to Bad Run List JSON."),
    output_level: str = typer.Option("INFO", "--output-level", help="Logging verbosity.")
) -> None:
    ...

if __name__ == "__main__":
    app()
```
