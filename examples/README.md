# Lorenzetti Examples & Execution Guide

This directory contains production job cards, transform templates, and examples demonstrating how to run the full simulation and reconstruction sequence.

---

## 1. End-to-End Simulation & Reconstruction Workflow

```mermaid
graph TD
    subgraph Stage1 ["1. Generation (Pythia8)"]
        Gen["gen_zee.py / gen_jets.py"] --> EvtFile["EVT.root (Truth &amp; Seeds)"]
    end

    subgraph Stage2 ["2. Simulation (Geant4)"]
        EvtFile --> Sim["simu_trf.py"]
        Sim --> HitFile["HIT.root (CaloHits)"]
    end

    subgraph Stage3 ["3. Digitization &amp; Reconstruction"]
        HitFile --> Reco["reco_trf.py (Cells &rarr; Clusters &rarr; Rings &rarr; Electrons)"]
        Reco --> AodFile["AOD.root (Reconstructed EDM)"]
    end

    subgraph Stage4 ["4. Analysis &amp; ML"]
        AodFile --> Ntuple["ntuple_trf.py"]
        Ntuple --> FlatNtuple["NTUPLE.root (Flattened Trees for Ringer)"]
    end
```

---

## 2. Running a Production Chain from Scratch

### 2.1. Create Jobs from a Production Card
```bash
run_job.py create --production-card zee.card -o zee_jobs
```

### 2.2. Run a Single Job
```bash
run_job.py run -j zee_jobs/job.0.json -o experiment
```

### 2.3. Run in Parallel with Multi-Threading (`prun_jobs`)
```bash
mkdir -p zee
prun_jobs.py -i zee_jobs -o zee/job --number-of-threads 10 -c "run_job.py run -j %IN -o %OUT"
```
