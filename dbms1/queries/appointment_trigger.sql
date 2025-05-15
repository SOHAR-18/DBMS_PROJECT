CREATE TRIGGER IF NOT EXISTS new_appointment_trigger
AFTER INSERT ON appointments
FOR EACH ROW
BEGIN
    UPDATE doctors 
    SET available_slots = REPLACE(available_slots, NEW.time_slot, '')
    WHERE specialization = NEW.doctor_type 
    AND available_slots LIKE '%' || NEW.time_slot || '%';
END;