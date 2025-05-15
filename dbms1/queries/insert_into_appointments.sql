INSERT INTO appointments 
(patient_id, doctor_type, time_slot, temperature, medicines, description, created_at)
VALUES 
(%s, %s, %s, %s, %s, %s, NOW());