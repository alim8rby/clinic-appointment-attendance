from pathlib import Path
import pandas as pd

project = Path(__file__).resolve().parent.parent
folder = project / "data" / "synthetic"

appointments = pd.read_csv(folder / "appointments_cleaned.csv")
patients = pd.read_csv(folder / "patients.csv")

# Many appointments may belong to one patient.
enriched = appointments.merge(
    patients,
    on="patient_id",
    how="left",
    validate="many_to_one",
    indicator=True
)

# Stop if any appointment has no matching patient.
unmatched = enriched["_merge"].ne("both")

if unmatched.any():
    raise ValueError(
        f"{unmatched.sum()} appointments have no matching patient."
    )

assert len(enriched) == len(appointments), (
    "The merge changed the appointment count."
)

enriched = enriched.drop(columns="_merge")

enriched.to_csv(
    folder / "appointments_enriched.csv",
    index=False
)

print("Appointments enriched:", len(enriched))
print("Missing age groups:", enriched["age_group"].isna().sum())
print("Saved appointments_enriched.csv")