# 🔄 CI/CD & Automated Testing Specification (`ci_cd_spec.md`)

> **Status:** Active Specification  
> **Scope:** GitHub Actions workflows (`.github/workflows/`), automated tests, container validation, and documentation deployment.

---

## 1. CI/CD Architecture Overview

Lorenzetti uses GitHub Actions running on self-hosted or container-capable runners. All compilation, generation, simulation, digitization, reconstruction, and documentation tasks execute strictly inside the official container image `docker://lorenzetti/lorenzetti:latest`.

```
[Git Push / PR]
       │
       ├──▶ [Workflow 1: reco_sequence.yml] ─── Full Event Reconstruction Chain
       │       ├── Build & Compile
       │       ├── Event Generation (Zee, Jets, MinBias, Single Particle)
       │       ├── Geant4 Simulation (simu_trf)
       │       ├── Pileup Merging (merge_trf)
       │       ├── Digitization (digit_trf)
       │       ├── Reconstruction (reco_trf)
       │       └── Flat Ntuple Production (ntuple_trf)
       │
       ├──▶ [Workflow 2: anomaly_sequence.yml] ── Hardware Defect & Anomaly Validation
       │       ├── Bad Run List Injection
       │       ├── Noise Perturbation
       │       └── Reconstruction with Defects
       │
       └──▶ [Workflow 3: pages.yml] ─────────── Documentation Generation
               ├── Doxygen C++ API Extraction
               ├── Sphinx Documentation Build (RST + Notebooks)
               └── GitHub Pages Deployment
```

---

## 2. GitHub Actions Workflow Definitions

### 2.1. `reco_sequence.yml` (Core Simulation & Reconstruction Pipeline)
- **Trigger**: `push` to any branch, `pull_request` to `master`/`main`.
- **Environment**: `container: image: docker://lorenzetti/lorenzetti:latest`.
- **Jobs**:
  1. `build`: Compiles C++ libraries (`make`) and verifies `build/lzt_setup.sh`.
  2. `generation`: Runs `gen_zee.py --nov 5 -o Zee.EVT.root`.
  3. `simulation`: Runs `simu_trf.py -i Zee.EVT.root -o Zee.HIT.root -nt 5`.
  4. `merge`: Simulates minbias `mb.HIT.root` and runs `merge_trf.py`.
  5. `digitalization`: Runs `digit_trf.py -i Zee.HIT.root -o Zee.ESD.root`.
  6. `reconstruction`: Runs `reco_trf.py -i Zee.ESD.root -o Zee.AOD.root`.
  7. `ntuple`: Runs `ntuple_trf.py -i Zee.AOD.root -o Zee.NTUPLE.root`.
  8. Generator test matrix: `gen_jets`, `gen_minbias`, `gen_single_particle`, `gen_overlapped_zee`.

### 2.2. `anomaly_sequence.yml` (Defect & Perturbation Validation)
- Validates the injection of hardware defects (dead cells, noisy channels, hot spots) using JSON bad run lists.
- Ensures the `PulsePerturber` and `CrossTalkMaker` modules operate correctly without unhandled exceptions.

### 2.3. `pages.yml` (Documentation Pipeline)
- Generates C++ Doxygen XML.
- Executes `setup_doc_env.py` and `generate_cxx_rst.py`.
- Compiles Sphinx HTML with Jupyter notebook tutorials (`doc/source/tutorials/`).
- Deploys static pages to GitHub Pages.

---

## 3. CI Quality Assurance Rules

1. **Deterministic Exit Codes**: Every step must exit with `0`. Any non-zero exit immediately fails the pipeline.
2. **Artifact Verification**: Downstream jobs must verify that generated ROOT files contain valid, non-corrupted TTrees with non-zero entries.
3. **No Unmanaged Temp Files**: Pipelines run in isolated container workspaces; cache and intermediate ROOT files are cleaned up or stored as job artifacts.
