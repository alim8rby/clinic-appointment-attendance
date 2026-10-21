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