# ⚛️ Physics Event Generation Specification (`generator/`)

> **Status:** Active Specification  
> **Location:** [generator/](file:///home/joao.pinto/git_repos/lorenzetti/generator)  
> **Subpackages:** `genkernel`, `filters`, `evtgen`

---

## 1. Package Overview

The `generator/` package is responsible for primary physics event simulation, parton showering, hadronization, and acceptance filtering using **Pythia8** and **HepMC3**.

```
generator/
├── filters/
│   ├── python/          # Filter definitions: Zee, JF17 (Jets), SingleParticle, Pileup, OverlappedEvents
│   └── scripts/         # Generation scripts: gen_zee.py, gen_jets.py, gen_minbias.py, gen_single.py
├── genkernel/           # GenKernel C++ base
└── evtgen/              # Pythia8 configuration data and cmnd templates
```

---

## 2. Event Generation Types & Filter Pipelines

```
[Pythia8 Engine] ──▶ [Phase Space & Kinematic Cuts] ──▶ [Detector Acceptance Filter] ──▶ [EventTape (EVT.root)]
```

### 2.1. Generation Modes
1. **$Z \to e^+e^-$ (`Zee`)**:
   - Resonant $Z/\gamma^*$ production decaying to electron-positron pairs.
   - Kinematic cuts: $p_T > 15\text{ GeV}$, $|\eta| < 3.2$.
   - Options: `--force-forward-electron`, `--zero-vertex-particles`.
2. **QCD Dijets (`JF17` / `Jets`)**:
   - Multi-jet events filtered in transverse momentum bins (e.g. $17 < p_T < 35\text{ GeV}$).
3. **Minimum Bias (`Minbias` / `Pileup`)**:
   - Inelastic proton-proton non-diffractive interactions for in-time/out-of-time pileup overlay.
4. **Single Particle (`SingleParticle`)**:
   - Single electrons, photons, pions ($\pi^\pm, \pi^0$), muons, or kaons injected with flat/log energy distributions for calibration and response matrix derivation.
5. **Overlapped Events (`OverlappedEvents`)**:
   - Combined hard scatter + $N$ pileup collisions per bunch crossing ($\mu$).

---

## 3. Filter Class APIs

```python
from typing import Optional, List
from GaugiKernel import Logger, LoggingLevel
from GenKernel import Pythia8

class Zee(Logger):
    def __init__(
        self,
        name: str,
        generator: Pythia8,
        eta_max: float = 3.2,
        min_pt: float = 15000.0,  # MeV
        zero_vertex_particles: bool = False,
        force_forward_electron: bool = False,
        output_level: int = LoggingLevel.INFO
    ) -> None:
        """
        Z -> ee event filter.

        Args:
            name (str): Filter instance name.
            generator (Pythia8): Pythia8 generator engine instance.
            eta_max (float): Maximum pseudorapidity cut for electrons.
            min_pt (float): Minimum transverse momentum in MeV.
            zero_vertex_particles (bool): Fix production vertex to (0,0,0).
            force_forward_electron (bool): Require at least one forward electron.
            output_level (int): Messenger verbosity.
        """
        ...
```

---

## 4. Typer CLI CLI Standard for Generation

All generation scripts (`gen_zee.py`, `gen_jets.py`, `gen_minbias.py`, `gen_single.py`, `gen_overlapped_zee.py`) must conform to `typer`:

```python
import typer
from typing import Optional

app = typer.Typer(
    name="gen_zee",
    help="**Generates Z -> ee events using Pythia8 and streams to EVT.root.**",
    add_completion=False
)

@app.command()
def generate(
    output_file: str = typer.Option(..., "-o", "--output-file", help="Path to output `EVT.root` file."),
    num_events: int = typer.Option(10, "-n", "--nov", help="Number of events to generate."),
    run_number: int = typer.Option(0, "--run-number", help="Run number identifier."),
    eta_max: float = typer.Option(3.2, "--eta-max", help="Max |eta| acceptance."),
    seed: Optional[int] = typer.Option(None, "--seed", help="Pythia random seed."),
    zero_vertex: bool = typer.Option(False, "--zero-vertex-particles", help="Zero production vertex for G4."),
    force_forward: bool = typer.Option(False, "--force-forward-electron", help="Force forward electron acceptance."),
    output_level: str = typer.Option("INFO", "--output-level", help="Logging verbosity.")
) -> None:
    ...

if __name__ == "__main__":
    app()
```
