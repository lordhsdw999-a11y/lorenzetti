# ⚙️ Kernel Modules Specification (`kernel/`)

> **Status:** Active Specification  
> **Location:** [kernel/](file:///home/joao.pinto/git_repos/lorenzetti/kernel)  
> **Subpackages:** `GaugiKernel`, `G4Kernel`, `GenKernel`

---

## 1. Package Overview

The `kernel/` package provides the foundational architecture for execution management, configuration, logging, Geant4 runtime control, and event generator interfacing.

```
kernel/
├── GaugiKernel/      # Framework backbone: Configurable, Logger, EventTape, ComponentAccumulator
├── G4Kernel/         # Geant4 run manager, sensitive detector hooks, user actions
└── GenKernel/        # Generator event tape, HepMC3 bridge, Pythia8 interfaces
```

---

## 2. Submodule Specifications

### 2.1. `GaugiKernel`
**Purpose**: Central framework infrastructure, execution lifecycle, logging, and property management.

- **Key Classes & Python Bindings**:
  - `Configurable`: Base class for all algorithmic components. Enables dynamic property assignment and serialization.
  - `Logger` & `LoggingLevel`: Standardized logging hierarchy (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `FATAL`) with ANSI color support.
  - `ComponentAccumulator`: Accumulates algorithms and services into an executable execution graph.
  - `EventTape`: Controls event-by-event loop execution and algorithm chaining.
  - `constants`: Physical unit definitions (`GeV`, `MeV`, `keV`, `eV`, `mm`, `cm`, `m`, `ns`, `ps`).
  - `enumerators`: Standard framework enumerations (detector samplings, particle types, status codes).

- **Type Hinting Standard**:
  ```python
  from typing import Dict, List, Optional, Any, Union
  from GaugiKernel import Logger, LoggingLevel

  class Service(Logger):
      def __init__(self, name: str, output_level: int = LoggingLevel.INFO) -> None:
          super().__init__(name)
          self.set_level(output_level)

      def initialize(self) -> bool:
          ...

      def execute(self) -> bool:
          ...

      def finalize(self) -> bool:
          ...
  ```

---

### 2.2. `G4Kernel`
**Purpose**: Encapsulates Geant4 runtime initialization, user actions, and sensitive detector bridges.

- **Key C++ Classes**:
  - `G4Kernel::RunManager`: Manages multithreaded / single-threaded Geant4 initialization, geometry registration, and physics list attachment.
  - `G4Kernel::PrimaryGeneratorAction`: Translates generator truth particles (`TruthParticle`) into Geant4 `G4PrimaryVertex` and `G4PrimaryParticle`.
  - `G4Kernel::SteppingAction` & `G4Kernel::StackingAction`: Monitors particle tracks, energy deposition, and step coordinates.
  - `G4Kernel::CaloSensitiveDetector`: Sensitive detector implementation attached to active calorimeter logical volumes, accumulating `CaloHit` objects.

- **Configuration Properties**:
  - `PhysicsList`: Selected physics list (e.g. `FTFP_BERT`, `QGSP_BERT`).
  - `MagneticField`: Uniform or map-based magnetic field vector in Tesla.
  - `StepLimits`: Maximum step length in active calorimeter media.

---

### 2.3. `GenKernel`
**Purpose**: Standard interface for physics event generators (Pythia8, HepMC3).

- **Key Classes**:
  - `GenKernel::Pythia8`: Python/C++ wrapper configuring Pythia8 event generation cards, center-of-mass energy ($\sqrt{s}$), and random seeds.
  - `GenKernel::EventTape`: Streams generated `TruthParticle` and `EventInfo` into `EVT.root` files.

- **Python Specification**:
  ```python
  from typing import Optional, List
  from GaugiKernel import Logger

  class Pythia8(Logger):
      def __init__(
          self,
          name: str,
          file: str,
          seed: Optional[int] = None,
          output_level: int = 1
      ) -> None:
          ...
  ```
