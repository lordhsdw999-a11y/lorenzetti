# 🖥️ CLI Standards & Typer Architecture (`cli_standards.md`)

> **Status:** Active Specification  
> **Scope:** All executable Python scripts in `generator/filters/scripts/`, `reconstruction/reco/scripts/`, `geometry/scripts/`, and root tools.

---

## 1. Principles of Lorenzetti CLI Design

1. **Declarative & Type-Safe**: All CLI scripts must use **`typer`** with type annotations.
2. **Positional vs Options**:
   - Primary inputs and outputs are explicit named options with short flags (e.g. `-i / --input-file`, `-o / --output-file`).
   - Counts and parameters have standardized flags (`-n / --nov / -nt / --num-events`).
3. **Help & Documentation**:
   - `typer.Option(..., help="...")` must contain clear, markdown-compatible descriptions.
   - Default values and units (e.g., `MeV`, `GeV`, `mm`, `ns`) must be clearly stated.
4. **Consistent Exit Codes & Errors**:
   - `0` on successful completion.
   - `1` for invalid arguments or missing input files.
   - `2` for simulation/runtime errors.

---

## 2. Standard CLI Flag Conventions

| Concept | Preferred Long Option | Preferred Short Flag | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Input File** | `--input-file` / `--input-files` | `-i` | `str` / `List[str]` | Input ROOT file path(s) |
| **Output File** | `--output-file` | `-o` | `str` | Output ROOT destination path |
| **Number of Events** | `--num-events` / `--nov` | `-n` / `-nt` | `int` | Number of events to process (-1 for all) |
| **Random Seed** | `--seed` | `-s` | `Optional[int]` | Random engine seed |
| **Run Number** | `--run-number` | `-r` | `int` | Event run identifier |
| **Verbosity** | `--output-level` | `-v` | `str` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| **Multiprocessing** | `--n-jobs` / `--threads` | `-j` | `int` | Parallel worker processes |
| **Geometry Tag** | `--geometry` | `-g` | `str` | Geometry version (`v1`, `v2`, etc.) |

---

## 3. Migration Pattern: `argparse` to `typer`

When refactoring legacy scripts:

### Legacy `argparse` Pattern (Deprecated)
```python
# ❌ DEPRECATED
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input-file', required=True, type=str)
parser.add_argument('-o', '--output-file', required=True, type=str)
args = parser.parse_args()
```

### Modern `typer` Pattern (Mandatory)
```python
# ✅ MANDATORY PATTERN
import typer
from typing import Optional

app = typer.Typer(
    help="**Description of script purpose in Markdown**",
    add_completion=False
)

@app.command()
def main(
    input_file: str = typer.Option(..., "-i", "--input-file", help="Input file path."),
    output_file: str = typer.Option(..., "-o", "--output-file", help="Output file destination."),
    num_events: int = typer.Option(10, "-n", "--nov", help="Total events to process."),
    seed: Optional[int] = typer.Option(None, "--seed", help="Random seed.")
) -> None:
    ...

if __name__ == "__main__":
    app()
```
