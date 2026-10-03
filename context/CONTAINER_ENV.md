# 🐳 Singularity & Container Execution Environment

> **Status:** Active Reference  
> **Scope:** Container ecosystem, Singularity SIF build/runtime, standard environment variables, and execution rules.

---

## 1. Container Strategy Overview

Lorenzetti builds on top of complex HEP C++ libraries (**ROOT 6**, **Geant4 11**, **Pythia 8.3**, **FastJet 3.4**, **HepMC3 3.3**, **DD4hep**, **LCIO**). To guarantee bitwise reproducibility across local development machines, GitHub Actions CI runners, and HPC clusters (e.g. SLURM), the framework is fully containerized.

- **Docker Image**: `docker://lorenzetti/lorenzetti:latest` (built via [docker/Dockerfile](file:///home/joao.pinto/git_repos/lorenzetti/docker/Dockerfile)).
- **Singularity Image (SIF)**: `lorenzetti_latest.sif` or sandbox directory `lorenzetti_latest/`.

---

## 2. Standard Project Environment Variables

The project mandates the following environment variables. They are initialized automatically by container entrypoints or by sourcing `build/lzt_setup.sh`:

### 2.1. Framework Paths
| Variable | Description | Default / In-Container Path |
| :--- | :--- | :--- |
| `LORENZETTI_BUILD_DIR` | Directory containing compiled libraries and binaries | `$PWD/build` |
| `LORENZETTI_SCRIPTS_DIR` | Path to execution transform scripts | `$PWD/scripts` |
| `LORENZETTI_EVTGEN_DATA_DIR` | Path to Pythia8 configuration files (`.cmnd`) | `$PWD/data/evtgen` |
| `LORENZETTI_GEOMETRY_DATA_DIR`| Path to calorimeter GDML / geometry definitions | `$PWD/data/geometry` |
| `PYTHONPATH` | Python import search path | `$PWD/python:$PYTHONPATH:/opt/root/build/lib:/opt/pythia/lib` |
| `LD_LIBRARY_PATH` | Shared library load path | `$PWD/lib:$ROOTSYS/lib:$LD_LIBRARY_PATH` |

### 2.2. Underlying HEP Toolkit Paths
| Variable | Value in Base Container | Purpose |
| :--- | :--- | :--- |
| `ROOTSYS` | `/opt/root/build/` | ROOT installation root |
| `PYTHIA8_INCLUDE` | `/opt/pythia/include` | Pythia8 C++ headers |
| `PYTHIA8_LIBRARIES` | `/opt/pythia/lib` | Pythia8 shared libraries |
| `FASTJET_INCLUDE` | `/opt/fastjet/include` | FastJet C++ headers |
| `FASTJET_LIBRARIES` | `/usr/local/lib` | FastJet shared libraries |
| `HEPMC_INCLUDE` | `/opt/optmc/include/` | HepMC3 C++ headers |
| `HEPMC_LIBRARIES` | `/usr/local/lib` | HepMC3 shared libraries |
| `G4*DATA` | `/opt/geant4/build/data/*` | Geant4 nuclear & electromagnetic cross-section datasets |

### 2.3. Singularity Cache & Temp Directories
When building or pulling Singularity images, always configure dedicated cache and temporary paths:
```bash
export SINGULARITY_CACHEDIR=$PWD/docker/cache
export SINGULARITY_TMPDIR=$PWD/docker/cache
```

---

## 3. Singularity Build & Execution Workflows

### 3.1. Pulling / Building SIF
To pull the official image or compile a Singularity sandbox:

```bash
# Pull SIF image
make -C docker pull

# Build Singularity sandbox locally from Docker image
make -C docker build_singularity
```

### 3.2. Running Interactive Shell inside Singularity
Mount current repository into Singularity:

```bash
singularity shell --bind $(pwd):/workspace docker/lorenzetti_latest.sif
# Inside container:
cd /workspace
make
source build/lzt_setup.sh
```

### 3.3. One-Liner Execution via Singularity Exec
Execute a transform script directly using the Singularity container:

```bash
singularity exec \
  --bind $(pwd):/workspace \
  --pwd /workspace \
  docker/lorenzetti_latest.sif \
  bash -c "source build/lzt_setup.sh && gen_zee.py --nov 50 -o Zee.EVT.root"
```

---

## 4. Setup Script Lifecycle (`lzt_setup.sh`)

When `source build/lzt_setup.sh` runs:
1. Symlinks all `.pcm` ROOT dictionary payload files to `build/`.
2. Symlinks shared objects (`.so` / `.dylib`) into `build/lib/`.
3. Symlinks compiled executables into `build/executables/`.
4. Exports `PATH`, `PYTHONPATH`, `LD_LIBRARY_PATH`, and `LORENZETTI_*` environment variables.
5. Emits confirmation: `Lorenzetti framework set.`
