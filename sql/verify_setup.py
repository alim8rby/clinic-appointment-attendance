from pathlib import Path
import sqlite3

project = Path(__file__).resolve().parent.parent
setup_sql = (project / "sql" / "setup.sql").read_text(encoding="utf-8")

with sqlite3.connect(":memory:") as connection:
    connection.executescript(setup_sql)
    connection.execute("PRAGMA foreign_keys = ON;")

    count = connection.execute(
        "SELECT COUNT(*) FROM appointments"
    ).fetchone()[0]

    issues = connection.execute(
        "PRAGMA foreign_key_check;"
    ).fetchall()

    assert count == 15, f"Expected 15 appointments, found {count}"
    assert not issues, f"Broken references: {issues}"

    for row in connection.execute(
        "SELECT clinic_id, total_appointments, attendance_pct "
        "FROM clinic_attendance_summary ORDER BY clinic_id"
    ):
        print(row)

    print("PASS: database rebuilt with 15 appointments and valid references.")