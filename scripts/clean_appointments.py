from pathlib import Path
import pandas as pd

project = Path(__file__).resolve().parent.parent
folder = project / "data" / "synthetic"

# Read the dirty input.
appointments = pd.read_csv(folder / "appointments_dirty.csv")
input_count = len(appointments)

# Remove exact duplicate rows.
appointments = appointments.drop_duplicates().copy()
duplicates_removed = input_count - len(appointments)

# Standardize status formatting.
original_status = appointments["status"].copy()

appointments["status"] = (
    appointments["status"]
    .str.strip()
    .str.title()
)

statuses_changed = original_status.ne(appointments["status"]).sum()

# Check that no conflicting appointment IDs remain.
assert appointments["appointment_id"].is_unique, (
    "Repeated appointment IDs remain after exact duplicate removal. "
    "Investigate conflicting records."
)

# Verify every cleaned record against the original reference.
reference = pd.read_csv(folder / "appointments_clean.csv")

expected = (
    reference.sort_values("appointment_id")
    .reset_index(drop=True)
)

actual = (
    appointments.sort_values("appointment_id")
    .reset_index(drop=True)
)

pd.testing.assert_frame_equal(actual, expected)

# Save only after verification passes.
appointments.to_csv(
    folder / "appointments_cleaned.csv",
    index=False
)

print("Input rows:", input_count)
print("Exact duplicates removed:", duplicates_removed)
print("Statuses standardized:", statuses_changed)
print("Cleaned rows:", len(appointments))
print("PASS: cleaned data exactly matches the clean reference.")