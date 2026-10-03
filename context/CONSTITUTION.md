# 📜 Lorenzetti Framework Constitution

> **Status:** Active & Mandatory  
> **Version:** 1.0.0  
> **Scope:** Entire Lorenzetti C++ and Python codebase, simulation pipeline, reconstruction tools, CI/CD, and execution environments.

---

## 1. Mission & Domain Charter

Lorenzetti is a high-precision, modular High Energy Physics (HEP) simulation and reconstruction framework dedicated to:
1. **High-Granularity Calorimetry Simulation**: Simulating electromagnetic (ECAL) and hadronic (HCAL) showers using **Geant4**.
2. **Realistic Readout & Digitization**: Convolving energy depositions with electronic pulse shapers, injecting electronic noise, modelling cross-talk, simulating hardware defects, and performing Optimal Filtering (OF / COF).
3. **Advanced Pileup & High-Luminosity Environments**: Simulating in-time and out-of-time pileup via overlay techniques.
4. **Fast Prototyping & Machine Learning**: Producing structured, transparent datasets for ML models (e.g., Ringer algorithms for electron/photon identification, anomaly detection, super-resolution, fast triggering).

All contributions, refactorings, and module additions must adhere to the principles in this Constitution.

---

## 2. Core Non-Negotiable Technical Directives

### 2.1. Python Type Hinting Directive
- **Strict Typing Mandatory**: Every Python function, method, constructor, and class attribute MUST declare explicit type hints.
- **Typing Library Standard**: Import standard type constructs from `typing` (e.g., `Dict`, `List`, `Optional`, `Union`, `Tuple`, `Any`, `Callable`, `TypeVar`, `Set`, `Sequence`, `Literal`).
- **Return Types**: All callable routines must declare return types (`-> None`, `-> Dict[str, Any]`, `-> bool`, etc.).
- **Container Specialization**: Generic types without parameters (e.g. bare `list` or `dict`) are prohibited. Use `List[str]`, `Dict[str, float]`, `Optional[CaloCell]`.

```python
# ✅ REQUIRED CONVENTION
from typing import Dict, List, Optional, Union

def configure_sampling(
    sampling_name: str,
    gain_weights: List[float],
    noise_sigma: float = 0.0,
    dead_channels: Optional[List[int]] = None
) -> Dict[str, Union[str, float, List[float]]]:
    """Configures calorimeter sampling parameters with full type safety."""
    ...
```

### 2.2. Command Line Interface (CLI) Directive with Typer
- **Mandatory Typer Framework**: All user-facing CLI entry points and transform scripts (`*_trf.py`, `gen_*.py`, `prun.py`, etc.) MUST use **`typer`** (with `rich` formatting support).
- **No `argparse` in New/Refactored Code**: Legacy `argparse` scripts must be refactored to declarative `typer.Typer()` applications.
- **Self-Documenting Options**: Every CLI argument and option must use `typer.Option(...)` or `typer.Argument(...)` with explicit types, defaults, help strings formatted in Markdown, and short/long flags.
- **Structured Exit Codes**: Scripts must return standard POSIX exit codes (0 for success, non-zero for failures) and provide clear visual diagnostics.

```python
# ✅ REQUIRED CONVENTION
import typer
from typing import Optional

app = typer.Typer(
    name="simu_trf",
    help="**Lorenzetti Calorimeter Geant4 Simulation Transform**",
    add_completion=False,
)

@app.command()
def main(
    input_file: str = typer.Option(..., "-i", "--input-file", help="Path to input `EVT.root` file."),
    output_file: str = typer.Option(..., "-o", "--output-file", help="Path to output `HIT.root` file."),
    num_events: int = typer.Option(-1, "-nt", "--num-events", help="Number of events to simulate (-1 for all)."),
    geometry_version: str = typer.Option("v1", "-g", "--geometry", help="Detector geometry version tag."),
    seed: Optional[int] = typer.Option(None, "--seed", help="Random engine seed (defaults to entropy)."),
    output_level: str = typer.Option("INFO", "--output-level", help="Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)."),
) -> None:
    ...
```

### 2.3. Documentation & Markdown Comments Directive
- **English Language Mandatory**: All repository documentation, package `README.md` files, architecture notes, code comments, docstrings, and CLI help texts MUST be written in **English**.
- **Mermaid Diagram Standard**: All module and architecture `README.md` files must include structured, clean Mermaid diagrams illustrating data flow and component interactions. Follow the **RootStreamBuilder architectural style**:
  - Use `graph TD` or `graph LR` with logical `subgraph` sections grouping stages (e.g. `Storage`, `Reading`, `Reconstruction / Memory`, `Writing`).
  - Use explicit, descriptive labels for nodes with clean bracket notation (`subgraph Name ["Display Title"]`, `NodeID["Description ('Key')"]`).
  - Illustrate clear end-to-end data progression, showing inputs, in-memory representations (`StoreGate / EventContext`), and outputs.
- **Markdown Comments & Docstrings**: Code comments, docstrings, and help texts must follow Markdown formatting (including code blocks, tables, bold text, and math notation where appropriate).
- **Docstring Standard**: Use Google/Sphinx style docstrings detailing:
  - `Args:` / `Parameters:` with descriptions.
  - `Returns:` with return value semantics.
  - `Raises:` for explicit exception propagation.
- **Module-Level Documentation**: Every package must have a descriptive `README.md` in English containing purpose, architecture diagram (Mermaid), configuration flags, class signatures, and execution examples.

### 2.4. C++ Architecture & Integration Standards
- **Standard C++17/20**: Modern C++ best practices, emphasizing RAII, `std::unique_ptr` / `std::shared_ptr`, `const` correctness, and `noexcept` specifications.
- **ROOT / Geant4 Integration**:
  - Event Data Model (EDM) classes must inherit from `TObject` (or be ROOT-streamable) and generate dictionary bindings (`LinkDef.h`).
  - Thread safety: Geant4 multithreaded simulation (`G4MTRunManager`) actions and Sensitive Detectors must isolate thread-local state.
- **GaugiKernel Ecosystem**: C++ algorithms and tools inherit from `Gaugi::Algorithm`, `Gaugi::Tool`, or `Gaugi::Service`, maintaining lifecycle stages (`initialize()`, `execute()`, `finalize()`).

---

## 3. Singularity & Container Runtime Environment

Lorenzetti relies on a standardized Singularity/Docker base image providing ROOT, Geant4, Pythia8, FastJet, and HepMC3.

1. **Environment Variables**: The framework relies on standard environment variables declared in container recipes and setup scripts:
   - `LORENZETTI_BUILD_DIR`: Root build artifact directory.
   - `LORENZETTI_SCRIPTS_DIR`: Path to execution scripts.
   - `LORENZETTI_EVTGEN_DATA_DIR`: Path to Pythia8 configuration data (`.cmnd`).
   - `LORENZETTI_GEOMETRY_DATA_DIR`: Path to GDML/XML geometry data.
   - `SINGULARITY_CACHEDIR`: Local directory for caching image builds.
2. **Setup Script**: Every interactive and batch session must source `build/lzt_setup.sh` to populate `PYTHONPATH`, `LD_LIBRARY_PATH`, and `PATH`.
3. **No External Dependencies Outside Container**: Local development and CI runners must execute inside the designated container image (`docker://lorenzetti/lorenzetti:latest`).

---

## 4. Quality Gates & Enforcement

Every pull request and merge to `master` / `main` must satisfy all quality gates:

| Gate | Tool / Check | Threshold |
| :--- | :--- | :--- |
| **Type Safety** | `mypy` / `pyright` | Zero type errors (`--strict` mode encouraged) |
| **Code Formatting** | `black` / `ruff format` | 100% compliant with PEP 8 |
| **Linting & Complexity** | `ruff check` / `flake8` | Zero unresolved warnings |
| **CLI Compliance** | Automated CLI test suite | All CLIs use `typer` and pass parameter validation |
| **C++ Standards** | `clang-format` (Google/LLVM style) | Clean formatting |
| **Simulation Chain Validation** | GitHub Actions (`reco_sequence.yml`) | Successful execution from `EVT` to `NTUPLE` |
| **Documentation** | Sphinx + Doxygen (`pages.yml`) | Clean build without broken references |

---

## 5. Architectural Invariants

1. **Strict EDM Layering**: An event must pass through well-defined stages: `EVT` (Generator) $\to$ `HIT` (Simulation) $\to$ `ESD` (Digitization) $\to$ `AOD` (Reconstruction) $\to$ `NTUPLE` (Analysis/ML). No backward dependencies between layers are allowed.
2. **Determinism & Reproducibility**: Given the same random seed and configuration file, event generation and detector response must yield bit-identical outputs.
3. **Decoupled Physics & Instrumentation**: Detector geometry and pulse shapes are configured via metadata (JSON/Python), allowing detector variations without modifying C++ kernels.
