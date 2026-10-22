from pathlib import Path
import subprocess
import sys

project = Path(__file__).resolve().parent

steps = [
    "generate_synthetic.py",
    "create_dirty_batch.py",
    "clean_appointments.py",
    "enrich_appointments.py",
]

for step in steps:
    print(f"\nRunning {step}", flush=True)

    subprocess.run(
        [sys.executable, str(project / "scripts" / step)],
        cwd=project,
        check=True
    )

print("\nPASS: synthetic data pipeline completed.")