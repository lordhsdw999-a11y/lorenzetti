# 📦 Events & Event Data Model (EDM) Specification (`events/`)

> **Status:** Active Specification  
> **Location:** [events/](file:///home/joao.pinto/git_repos/lorenzetti/events)  
> **Subpackages:** `EventInfo`, `TruthParticle`, `CaloHit`, `CaloCell`, `SpacePoint`, `CaloCluster`, `CaloRings`, `Egamma`

---

## 1. Package Overview

The `events/` package defines the core **Event Data Model (EDM)** for Lorenzetti. Every class represents a physical or reconstructed entity across the simulation and reconstruction chain, with native ROOT dictionary generation (`LinkDef.h`) for serialization.

```
events/
├── EventInfo/       # Run number, event number, luminosity block, bunch crossing ID
├── TruthParticle/   # MC truth particle kinematics (px, py, pz, E, pdgId, status, vertex)
├── CaloHit/         # Step-level energy deposits from Geant4 sensitive detectors
├── CaloCell/        # Calorimeter readout cells (reconstructed energy, time, sampling, descriptor)
├── SpacePoint/      # Tracking 3D spacepoints (r, phi, z, cov matrix)
├── CaloCluster/     # Reconstructed energy clusters in Δη × Δφ window
├── CaloRings/       # Concentric energy rings extracted per calorimeter layer
└── Egamma/          # Electron and photon composite candidates (Cluster + Track + Rings)
```

---

## 2. Detailed EDM Class Specifications

### 2.1. `EventInfo`
Represents global event metadata.
- **Attributes**:
  - `runNumber()`: `uint32_t` / `int`
  - `eventNumber()`: `uint64_t` / `int`
  - `lumiBlock()`: `uint32_t` / `int`
  - `bunchCrossingId()`: `uint32_t` / `int`
  - `avgInteractionsPerCrossing()` ($\mu$): `float`

### 2.2. `TruthParticle` & `TruthParticleContainer`
Represents generated Monte Carlo truth particles from Pythia8 / HepMC3.
- **Attributes**:
  - `pdgId()`: `int` (PDG ID, e.g. 11 for $e^-$, 22 for $\gamma$, 23 for $Z$)
  - `status()`: `int` (Pythia generator status code)
  - `p4()`: `TLorentzVector` / `(px, py, pz, e)`
  - `pt()`, `eta()`, `phi()`, `m()`: Kinematic accessors
  - `vertex()`: `TVector3` / `(vx, vy, vz)` production vertex

### 2.3. `CaloHit` & `CaloHitContainer`
Raw energy deposition recorded by Geant4 Sensitive Detectors.
- **Attributes**:
  - `energy()`: `float` (deposited energy in MeV)
  - `time()`: `float` (deposition time in ns)
  - `position()`: `TVector3` (global spatial coordinate $x, y, z$)
  - `sampling()`: `int` / `CaloSampling` enum
  - `cellId()`: `uint64_t` / hash ID of the containing calorimeter cell

### 2.4. `CaloCell` & `CaloCellContainer`
Readout cell after electronic pulse simulation, noise injection, and Optimal Filtering.
- **Attributes**:
  - `energy()`: `float` (reconstructed cell energy in MeV)
  - `time()`: `float` (reconstructed pulse time in ns)
  - `sampling()`: `CaloSampling` enum (e.g. `EMB1`, `EMB2`, `EMB3`, `TileBar0`)
  - `eta()`, `phi()`, `r()`, `z()`: Geometric centroid coordinates
  - `descriptor()`: Pointer / reference to `CaloDetDescriptor`
  - `samples()`: `std::vector<float>` digitized ADC samples
  - `gain()`: `CaloGain` enum (`HIGH`, `MEDIUM`, `LOW`)
  - `provenance()`: Bitmask indicating defect, noise, or cross-talk injection

### 2.5. `CaloCluster` & `CaloClusterContainer`
Spatial cluster reconstructed by grouping adjacent `CaloCell` objects.
- **Attributes**:
  - `energy()`, `et()`, `eta()`, `phi()`: Cluster 4-momentum
  - `cells()`: `std::vector<const CaloCell*>` constituents
  - `nCells()`: `size_t`
  - `sizeEta()`, `sizePhi()`: Angular window size (e.g., $3 \times 7$, $7 \times 11$)
  - `samplingEnergy(CaloSampling)`: Longitudinal energy fraction per layer

### 2.6. `CaloRings` & `CaloRingsContainer`
Concentric energy rings constructed around the cluster seed for pattern recognition and neural networks.
- **Attributes**:
  - `rings()`: `std::vector<float>` vector of ring energies normalized or absolute
  - `nRings()`: Number of concentric rings (e.g., 8 in PS, 64 in EM1, 8 in EM2, 8 in EM3, 4 in HCAL)
  - `cluster()`: Reference to parent `CaloCluster`

### 2.7. `Egamma` & `EgammaContainer`
Composite object representing an electron or photon candidate.
- **Attributes**:
  - `cluster()`: Associated `CaloCluster`
  - `rings()`: Associated `CaloRings`
  - `truthParticle()`: Associated `TruthParticle` (for MC matching)
  - `author()`: Algorithm author tag
  - `pid()`: Identification flags (e.g., Loose, Medium, Tight neural network triggers)

---

## 3. Python Type Hints for EDM Manipulation

```python
from typing import List, Optional, Dict, Any

class CaloCell:
    def energy(self) -> float: ...
    def time(self) -> float: ...
    def sampling(self) -> int: ...
    def eta(self) -> float: ...
    def phi(self) -> float: ...
    def samples(self) -> List[float]: ...

class CaloCluster:
    def energy(self) -> float: ...
    def et(self) -> float: ...
    def eta(self) -> float: ...
    def phi(self) -> float: ...
    def cells(self) -> List[CaloCell]: ...
    def n_cells(self) -> int: ...

class CaloRings:
    def rings(self) -> List[float]: ...
    def n_rings(self) -> int: ...
```
