from pathlib import Path
import sqlite3
import pandas as pd

project = Path(__file__).resolve().parent.parent
database = project / "data" / "synthetic" / "appointments.db"
view_file = project / "sql" / "clinic_attendance_summary.sql"

output_folder = project / "outputs" / "synthetic"
output_folder.mkdir(parents=True, exist_ok=True)

with sqlite3.connect(
    f"{database.as_uri()}?mode=rw", uri=True
) as connection:
    view_exists = connection.execute(
        "SELECT 1 FROM sqlite_master "
        "WHERE type = 'view' "
        "AND name = 'clinic_attendance_summary'"
    ).fetchone()

    if view_exists is None:
        connection.executescript(
            view_file.read_text(encoding="utf-8")
        )

    summary = pd.read_sql_query(
        "SELECT * FROM clinic_attendance_summary "
        "ORDER BY clinic_id",
        connection
    )

assert len(summary) == 8
assert summary["total_appointments"].sum() == 50_000

summary.to_csv(
    output_folder / "clinic_summary.csv",
    index=False
)

print(summary.to_string(index=False))
print("\nPASS: 8 clinics reconcile to 50,000 appointments.")
print("Saved outputs/synthetic/clinic_summary.csv")