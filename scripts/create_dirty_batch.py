from pathlib import Path
import random
import pandas as pd

# Locate the synthetic data folder.
project = Path(__file__).resolve().parent.parent
folder = project / "data" / "synthetic"

# Read the clean reference without changing it.
clean = pd.read_csv(folder / "appointments_clean.csv")
dirty = clean.copy()

# Make the injected issues reproducible.
rng = random.Random(43)
issue_log = []

# Introduce 200 status-formatting issues.
selected_rows = rng.sample(range(len(dirty)), 200)

for row in selected_rows:
    original = dirty.at[row, "status"]
    modified = f"  {original.upper()}  "

    dirty.at[row, "status"] = modified

    issue_log.append({
        "appointment_id": dirty.at[row, "appointment_id"],
        "issue_type": "status_formatting",
        "original_value": original,
        "modified_value": modified
    })

# Append 100 exact copies of existing rows.
duplicate_rows = rng.sample(range(len(dirty)), 100)
duplicates = dirty.iloc[duplicate_rows].copy()

dirty = pd.concat([dirty, duplicates], ignore_index=True)

for appointment_id in duplicates["appointment_id"]:
    issue_log.append({
        "appointment_id": appointment_id,
        "issue_type": "exact_duplicate",
        "original_value": "One appointment row",
        "modified_value": "Extra identical copy"
    })

# Save the dirty batch and its issue log.
dirty.to_csv(
    folder / "appointments_dirty.csv",
    index=False
)

pd.DataFrame(issue_log).to_csv(
    folder / "injected_issues.csv",
    index=False
)

print("Dirty appointment rows:", len(dirty))
print("Formatting issues introduced:", len(selected_rows))
print("Duplicate rows added:", len(duplicates))
print("Injected issues logged:", len(issue_log))