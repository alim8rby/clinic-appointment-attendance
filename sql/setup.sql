BEGIN TRANSACTION;
CREATE TABLE appointments (
    appointment_id TEXT PRIMARY KEY NOT NULL,
    patient_id TEXT NOT NULL,
    clinic_id TEXT NOT NULL,
    appointment_date TEXT NOT NULL,
    status TEXT NOT NULL
        CHECK (
            status IN (
                'Attended',
                'Did Not Attend',
                'Unknown',
                'Cancelled'
            )
        ),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id)
);
INSERT INTO "appointments" VALUES('A101','P01','A','2026-09-01','Attended');
INSERT INTO "appointments" VALUES('A102','P02','A','2026-09-05','Unknown');
INSERT INTO "appointments" VALUES('A103','P01','A','2026-09-10','Did Not Attend');
INSERT INTO "appointments" VALUES('A104','P03','B','2026-10-01','Unknown');
INSERT INTO "appointments" VALUES('A105','P04','B','2026-10-05','Attended');
INSERT INTO "appointments" VALUES('A106','P05','B','2026-10-10','Attended');
INSERT INTO "appointments" VALUES('A107','P06','B','2026-10-15','Attended');
INSERT INTO "appointments" VALUES('A108','P01','A','2026-10-18','Attended');
INSERT INTO "appointments" VALUES('A109','P02','A','2026-10-19','Attended');
INSERT INTO "appointments" VALUES('A110','P99','A','2026-10-19','Attended');
INSERT INTO "appointments" VALUES('A111','P02','A','2026-10-20','Attended');
INSERT INTO "appointments" VALUES('A112','P03','B','2026-10-20','Did Not Attend');
INSERT INTO "appointments" VALUES('A113','P04','B','2026-10-21','Did Not Attend');
INSERT INTO "appointments" VALUES('A114','P02','A','2026-10-21','Attended');
INSERT INTO "appointments" VALUES('A115','P03','B','2026-10-21','Attended');
CREATE TABLE clinics (
    clinic_id TEXT PRIMARY KEY NOT NULL
);
INSERT INTO "clinics" VALUES('A');
INSERT INTO "clinics" VALUES('B');
CREATE TABLE patients (    patient_id TEXT PRIMARY KEY NOT NULL,    age_group TEXT NOT NULL);
INSERT INTO "patients" VALUES('P01','18-34');
INSERT INTO "patients" VALUES('P02','35-49');
INSERT INTO "patients" VALUES('P03','50-64');
INSERT INTO "patients" VALUES('P04','65+');
INSERT INTO "patients" VALUES('P05','35-49');
INSERT INTO "patients" VALUES('P06','50-64');
INSERT INTO "patients" VALUES('P99','35-49');
CREATE VIEW clinic_attendance_summary AS
WITH counts AS (
    SELECT
        c.clinic_id,
        COUNT(a.appointment_id) AS total_appointments,
        SUM(CASE WHEN a.status = 'Attended'
            THEN 1 ELSE 0 END) AS attended,
        SUM(CASE WHEN a.status = 'Did Not Attend'
            THEN 1 ELSE 0 END) AS missed,
        SUM(CASE WHEN a.status = 'Unknown'
            THEN 1 ELSE 0 END) AS unknown
    FROM clinics AS c
    LEFT JOIN appointments AS a
        ON c.clinic_id = a.clinic_id
    GROUP BY c.clinic_id
)
SELECT
    *,
    attended + missed AS known_appointments,
    ROUND(
        100.0 * attended / NULLIF(attended + missed, 0), 1
    ) AS attendance_pct,
    ROUND(
        100.0 * unknown / NULLIF(total_appointments, 0), 1
    ) AS unknown_pct
FROM counts;
COMMIT;