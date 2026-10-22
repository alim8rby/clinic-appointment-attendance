### Reading and exploring the appointments database

from pathlib import Path
import sqlite3
import pandas as pd

project = Path(__file__).resolve().parent.parent
database = project / "data" / "appointments.db"

with sqlite3.connect(f"{database.as_uri()}?mode=ro", uri=True) as connection:
    appointments = pd.read_sql_query(
        "SELECT * FROM appointments",
        connection
    )

print(appointments.head())
print("Appointment count:", len(appointments))
print(appointments["status"].value_counts())

### Calculating attendance rate

attended = (appointments["status"] == "Attended").sum()
missed = (appointments["status"] == "Did Not Attend").sum()
known = attended + missed

attendance_rate = attended / known if known > 0 else None

print("Attended:", attended)
print("Did Not Attend:", missed)

if attendance_rate is None:
    print("Attendance rate: No known statuses")
else:
    print(f"Attendance rate: {attendance_rate:.1%}")

clinic_summary = pd.crosstab(
    appointments["clinic_id"],
    appointments["status"]
).reindex(
    columns=["Attended", "Did Not Attend", "Unknown", "Cancelled"],
    fill_value=0
)

### Creating a summary table with totals and attendance percentage

clinic_summary["Total"] = clinic_summary.sum(axis=1)

known = (
    clinic_summary["Attended"]
    + clinic_summary["Did Not Attend"]
)

clinic_summary["Attendance %"] = (
    clinic_summary["Attended"]
    .div(known.where(known > 0))
    .mul(100)
    .round(1)
)

output_folder = project / "outputs"
output_folder.mkdir(exist_ok=True)

clinic_summary.to_csv(output_folder / "clinic_summary.csv")

print(clinic_summary)
print("Saved outputs/clinic_summary.csv")