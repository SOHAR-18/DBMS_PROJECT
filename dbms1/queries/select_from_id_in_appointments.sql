-- Get appointment details by appointment ID
SELECT 
    a.appointment_id,
    a.patient_name,
    a.age,
    a.sex,
    a.purpose,
    a.doctor_type,
    a.time_slot,
    a.temperature,
    a.medicines,
    a.description,
    a.token,
    a.created_at,
    u.email AS patient_email
FROM 
    appointments a
JOIN 
    users u ON a.user_id = u.user_id
WHERE 
    a.appointment_id = ?;