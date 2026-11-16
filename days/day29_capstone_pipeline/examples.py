"""Day 29 - Reference run of the finished pipeline (read it AFTER trying practice.py).

It imports the model solution so you can see the end result:
    python examples.py
"""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOLUTION = ROOT / "solutions" / "day29_solution.py"
OUT = HERE / "output"

# Load the solution module's functions without running its self-checks twice.
sys.argv = ["day29_solution.py"]
namespace = runpy.run_path(str(SOLUTION), run_name="day29_reference")

print("\n=== Running the pipeline ===")
kpis = namespace["run_pipeline"](ROOT / "datasets" / "sales_messy.csv", OUT)
print("\nKPIs:", kpis)
print("\n=== report.md ===")
print((OUT / "report.md").read_text(encoding="utf-8"))
print("Files created:", sorted(p.name for p in OUT.iterdir()))
