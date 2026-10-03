# 🛡️ Quality Gates & Development Standards

> **Status:** Active Reference  
> **Scope:** Code health, static analysis, type checking, formatting, test suites, and CI/CD validation.

---

## 1. Overview of Quality Gates

To preserve stability, maintainability, and reproducibility in particle physics analyses, every change in Lorenzetti must pass through four quality layers:

```
[1. Local Formatting & Linting] ──▶ [2. Strict Type Checking] ──▶ [3. CLI & Unit Testing] ──▶ [4. Physics Simulation CI Pipeline]
```

---

## 2. Quality Gate Definitions

### Gate 1: Python Strict Typing Gate
- **Requirement**: 100% of all Python modules, functions, classes, and scripts must have complete type hints using the `typing` library.
- **Checker**: `mypy --ignore-missing-imports` / `pyright`.
- **Criteria**:
  - Zero untyped function definitions (`def func(x): ...` $\to$ prohibited).
  - Explicit `Optional[...]` when values can be `None`.
  - Concrete collection parameters (e.g. `List[str]`, `Dict[str, float]`).
  - Strict return types declared on all callable objects.

### Gate 2: Code Formatting & Linting
- **Python**:
  - `black` / `ruff format` configured to standard 100-character line width.
  - `ruff check` / `flake8` for unused imports, undefined variables, and cyclomatic complexity.
- **C++**:
  - `clang-format` (Google/LLVM style with 2 or 4 spaces indentation, no tabs).
  - No raw pointers for object ownership; use `std::unique_ptr` / `std::shared_ptr`.
  - Memory leak prevention: All ROOT `TObject` allocations in event loops must be appropriately managed or collected.

### Gate 3: CLI Standards with Typer
- **Requirement**: All scripts under `scripts/` or `*/scripts/` must be implemented using `typer`.
- **Validation**:
  - `--help` flag produces rich markdown-compatible descriptions.
  - Required parameters marked with `...` (or `typer.Option(..., ...)`).
  - Argument types correctly mapped (`int`, `float`, `str`, `bool`, `Path`, `List[str]`).
  - Short flags (e.g. `-i`, `-o`, `-nt`, `-g`) provided for common options.

### Gate 4: Physics & Simulation Validation Chain
- **Requirement**: Full end-to-end event generation and reconstruction sequence must run without segfaults, memory leaks, or NaN energy outputs.
- **Automated Validation Sequence**:
  1. `gen_zee.py` / `gen_jets.py` / `gen_minbias.py` $\to$ Valid `EVT.root`
  2. `simu_trf.py` $\to$ Valid `HIT.root` with non-zero deposited energy
  3. `merge_trf.py` $\to$ Valid pileup overlay into `HIT.root`
  4. `digit_trf.py` $\to$ Valid `ESD.root` with reconstructed cell pulses
  5. `reco_trf.py` $\to$ Valid `AOD.root` with reconstructed clusters and rings
  6. `ntuple_trf.py` $\to$ Valid `NTUPLE.root` with non-empty TTree branches

---

## 3. Pre-Commit Checklist for Developers

Before submitting a Pull Request:

```bash
# 1. Format Python code
ruff format .
ruff check --fix .

# 2. Check Python typing
mypy core events generator geometry reconstruction

# 3. Format C++ code
find core events generator geometry reconstruction -name "*.cxx" -o -name "*.h" | xargs clang-format -i

# 4. Build and run validation pipeline inside Singularity
singularity exec docker/lorenzetti_latest.sif bash -c "
  make clean && make
  source build/lzt_setup.sh
  gen_zee.py --nov 5 -o test.EVT.root
  simu_trf.py -i test.EVT.root -o test.HIT.root -nt 5
  digit_trf.py -i test.HIT.root -o test.ESD.root
  reco_trf.py -i test.ESD.root -o test.AOD.root
  ntuple_trf.py -i test.AOD.root -o test.NTUPLE.root
"
```

---

## 4. Documentation & Docstring Quality Gate

- Every public class and function must include Google/Sphinx Markdown docstrings:
  ```python
  def convolve_samples(
      hit_energies: List[float],
      hit_times: List[float],
      shaper_weights: List[float],
      sampling_rate: float = 25.0
  ) -> List[float]:
      """
      Convolves simulated hit energy deposits with electronic pulse shaper.

      Args:
          hit_energies (List[float]): Deposited energy per Geant4 hit in MeV.
          hit_times (List[float]): Arrival time per Geant4 hit in nanoseconds.
          shaper_weights (List[float]): Discrete response coefficients of the shaper.
          sampling_rate (float): Digitizer sampling clock interval in ns (default: 25.0 ns for LHC).

      Returns:
          List[float]: Vector of digitized ADC sample voltages.
      """
      ...
  ```
- Package-level `README.md` must be updated if parameters, flags, or class signatures are modified.
