"""Regenerate synthetic CSVs, rebuild SQLite, and export clinic summaries."""
from pathlib import Path
import subprocess
import sys


def main():
    project = Path(__file__).resolve().parent
    steps = [
        ("generate_synthetic.py", []),
        ("create_dirty_batch.py", []),
        ("clean_appointments.py", []),
        ("enrich_appointments.py", []),
        ("load_synthetic_database.py", ["--replace"]),
        ("export_sql_summary.py", []),
    ]

    for step, arguments in steps:
        print(f"\nRunning {step}", flush=True)
        try:
            subprocess.run(
                [sys.executable, str(project / "scripts" / step), *arguments],
                cwd=project,
                check=True,
            )
        except subprocess.CalledProcessError as error:
            print(f"\nFAILED: {step}. Later steps were not run.", file=sys.stderr)
            return error.returncode

    print("\nPASS: synthetic CSVs, SQLite database, and SQL summary rebuilt.")
    print("Next: refresh Clinic_Appointment_Attendance_V2.pbix in Power BI Desktop.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
