### Generating synthetic data for patients and appointments

from pathlib import Path
import random
import pandas as pd

project = Path(__file__).resolve().parent.parent
output_folder = project / "data" / "synthetic"
output_folder.mkdir(parents=True, exist_ok=True)

rng = random.Random(42)

patient_count = 5_000
age_groups = ["18-34", "35-49", "50-64", "65+"]

patients = pd.DataFrame({
    "patient_id": [
        f"SYN{i:05d}"
        for i in range(1, patient_count + 1)
    ],
    "age_group": [
        rng.choice(age_groups)
        for _ in range(patient_count)
    ]
})

patients.to_csv(output_folder / "patients.csv", index=False)

print(patients.head())
print("Patients generated:", len(patients))
print("Unique IDs:", patients["patient_id"].nunique())

### Generating 50,000 appointments across 8 clinics and the complete year 2025

from datetime import date, timedelta

appointment_count = 50_000
patient_ids = patients["patient_id"].tolist()
clinic_ids = [f"C{i:02d}" for i in range(1, 9)]

start_date = date(2025, 1, 1)

appointments = pd.DataFrame({
    "appointment_id": [
        f"APT{i:06d}"
        for i in range(1, appointment_count + 1)
    ],
    "patient_id": rng.choices(patient_ids, k=appointment_count),
    "clinic_id": rng.choices(clinic_ids, k=appointment_count),
    "appointment_date": [
        (start_date + timedelta(days=rng.randrange(365))).isoformat()
        for _ in range(appointment_count)
    ],
    "status": rng.choices(
        ["Attended", "Did Not Attend", "Unknown", "Cancelled"],
        weights=[70, 18, 7, 5],
        k=appointment_count
    )
})

appointments.to_csv(
    output_folder / "appointments_clean.csv",
    index=False
)

print("Appointments generated:", len(appointments))
print(appointments["status"].value_counts())

### Verifying the generated data for consistency and integrity

clinics = pd.DataFrame({"clinic_id": clinic_ids})
clinics.to_csv(output_folder / "clinics.csv", index=False)

assert patients["patient_id"].is_unique
assert appointments["appointment_id"].is_unique
assert not patients.isna().any().any()
assert not appointments.isna().any().any()

assert appointments["patient_id"].isin(patients["patient_id"]).all()
assert appointments["clinic_id"].isin(clinics["clinic_id"]).all()

assert appointments["status"].isin([
    "Attended", "Did Not Attend", "Unknown", "Cancelled"
]).all()

dates = pd.to_datetime(
    appointments["appointment_date"],
    format="%Y-%m-%d",
    errors="raise"
)
assert dates.between("2025-01-01", "2025-12-31").all()

reference_counts = (
    appointments.groupby(["clinic_id", "status"])
    .size()
    .rename("appointment_count")
    .reset_index()
)

reference_counts.to_csv(
    output_folder / "reference_clinic_status_counts.csv",
    index=False
)

print("PASS: clean reference data validated.")