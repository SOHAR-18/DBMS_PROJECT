-- Insert new doctor record
INSERT INTO doctors (
    name, 
    specialization, 
    available_slots
) VALUES (
    ?,  -- Doctor name
    ?,  -- Specialization
    ?   -- Comma-separated available time slots
);