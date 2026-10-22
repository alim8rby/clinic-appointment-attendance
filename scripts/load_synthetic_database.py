"""Build validated SQLite data; optionally replace the prior synthetic database."""
import argparse
import os
from pathlib import Path
import sqlite3
import tempfile

import pandas as pd


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--replace", action="store_true",
        help="Replace only the synthetic database after a successful staged build.",
    )
    arguments = parser.parse_args()
    project = Path(__file__).resolve().parent.parent
    folder = project / "data" / "synthetic"
    baseline = project / "data" / "appointments.db"
    target = folder / "appointments.db"

    if target.exists() and not arguments.replace:
        raise FileExistsError(
            f"Database already exists: {target}. Use --replace to rebuild it safely."
        )

    with sqlite3.connect(f"{baseline.as_uri()}?mode=ro", uri=True) as source:
        schemas = {}
        for table in ["patients", "clinics", "appointments"]:
            row = source.execute(
                "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
                (table,),
            ).fetchone()
            if row is None:
                raise ValueError(f"Baseline schema is missing table: {table}")
            schemas[table] = row[0]

    folder.mkdir(parents=True, exist_ok=True)
    # Build beside the destination so publication is a same-filesystem replacement.
    with tempfile.TemporaryDirectory(prefix=".sqlite-build-", dir=folder) as temporary:
        staged = Path(temporary) / "appointments.db"
        connection = sqlite3.connect(staged)
        try:
            connection.execute("PRAGMA foreign_keys = ON")
            with connection:
                for table, schema in schemas.items():
                    connection.execute(schema)
                    filename = (
                        "appointments_cleaned.csv"
                        if table == "appointments" else f"{table}.csv"
                    )
                    frame = pd.read_csv(folder / filename)
                    columns = ", ".join(f'"{column}"' for column in frame.columns)
                    placeholders = ", ".join(["?"] * len(frame.columns))
                    connection.executemany(
                        f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
                        frame.itertuples(index=False, name=None),
                    )

                count = connection.execute(
                    "SELECT COUNT(*) FROM appointments"
                ).fetchone()[0]
                if count != 50_000:
                    raise ValueError(f"Expected 50,000 appointments, found {count}")
                issues = connection.execute("PRAGMA foreign_key_check").fetchall()
                if issues:
                    raise ValueError(f"Broken foreign-key references: {issues}")
                integrity = connection.execute("PRAGMA integrity_check").fetchall()
                if integrity != [("ok",)]:
                    raise ValueError(f"SQLite integrity check failed: {integrity}")
        finally:
            connection.close()

        # The existing database survives any build or validation failure above.
        os.replace(staged, target)

    print(f"PASS: loaded {count:,} appointments.")
    print("Saved:", target)


if __name__ == "__main__":
    main()
