UPDATE appointments 
SET 
    patient_name = ?,
    age = ?,
    sex = ?,
    purpose = ?,
    doctor_type = ?,
    time_slot = ?,
    temperature = ?,
    medicines = ?,
    description = ?
WHERE 
    appointment_id = ?;