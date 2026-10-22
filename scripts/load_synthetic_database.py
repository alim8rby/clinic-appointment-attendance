### Keep this script outside the pipeline because it deliberately refuses to overwrite an existing database.

from pathlib import Path
import sqlite3
import pandas as pd

project = Path(__file__).resolve().parent.parent
folder = project / "data" / "synthetic"

baseline = project / "data" / "appointments.db"
target = folder / "appointments.db"

# Read the original table definitions without changing the baseline.
with sqlite3.connect(
    f"{baseline.as_uri()}?mode=ro", uri=True
) as source:
    schemas = {
        table: source.execute(
            "SELECT sql FROM sqlite_master "
            "WHERE type = 'table' AND name = ?",
            (table,)
        ).fetchone()[0]
        for table in ["patients", "clinics", "appointments"]
    }

# Refuse to overwrite an existing database.
if target.exists():
    raise FileExistsError(f"Database already exists: {target}")

connection = sqlite3.connect(target)

try:
    connection.execute("PRAGMA foreign_keys = ON")

    with connection:
        for table, schema in schemas.items():
            connection.execute(schema)

            filename = (
                "appointments_cleaned.csv"
                if table == "appointments"
                else f"{table}.csv"
            )

            frame = pd.read_csv(folder / filename)
            columns = ", ".join(frame.columns)
            placeholders = ", ".join(["?"] * len(frame.columns))

            connection.executemany(
                f"INSERT INTO {table} ({columns}) "
                f"VALUES ({placeholders})",
                frame.itertuples(index=False, name=None)
            )

        count = connection.execute(
            "SELECT COUNT(*) FROM appointments"
        ).fetchone()[0]

        assert count == 50_000
        assert not connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

    print(f"PASS: loaded {count:,} appointments.")
    print("Saved:", target)

finally:
    connection.close()