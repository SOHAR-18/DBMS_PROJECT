from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL # type: ignore
import random
from datetime import datetime
import MySQLdb.cursors # type: ignore

app = Flask(__name__)
app.secret_key = 'healthcare_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''  # Enter your MySQL password here
app.config['MYSQL_DB'] = 'healthcare2_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Helper Functions
def get_appointment(appointment_id):
    """Get single appointment by ID"""
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT * FROM appointments 
        WHERE appointment_id = %s
    """, (appointment_id,))
    appointment = cursor.fetchone()
    cursor.close()
    return appointment

def add_doctor(name, specialization, available_slots):
    """Add new doctor"""
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO doctors (name, specialization, available_slots)
        VALUES (%s, %s, %s)
    """, (name, specialization, available_slots))
    mysql.connection.commit()
    cursor.close()

def init_db():
    with app.app_context():
        cursor = mysql.connection.cursor()
        
        # Create tables
        cursor.execute("DROP TABLE IF EXISTS appointments")
        cursor.execute("DROP TABLE IF EXISTS doctors")
        cursor.execute("DROP TABLE IF EXISTS users")
        
        cursor.execute("""
            CREATE TABLE users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE doctors (
                doctor_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                specialization VARCHAR(100) NOT NULL,
                available_slots TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE appointments (
                appointment_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                patient_name VARCHAR(100) NOT NULL,
                patient_age INT NOT NULL,
                patient_sex VARCHAR(10) NOT NULL,
                purpose VARCHAR(100) NOT NULL,
                doctor_type VARCHAR(100) NOT NULL,
                time_slot VARCHAR(50) NOT NULL,
                temperature FLOAT,
                medicines TEXT,
                description TEXT NOT NULL,
                token INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Create trigger (MySQL syntax differs from SQLite)
        cursor.execute("""
            CREATE TRIGGER update_doctor_slots
            AFTER INSERT ON appointments
            FOR EACH ROW
            BEGIN
                UPDATE doctors 
                SET available_slots = REPLACE(available_slots, NEW.time_slot, '')
                WHERE specialization = NEW.doctor_type;
            END
        """)
        
        # Insert initial doctor data
        doctors = [
            ('Dr. Smith', 'Gynecologist', '10:00 AM - 10:30 AM,11:00 AM - 11:30 AM,2:00 PM - 2:30 PM,4:00 PM - 4:30 PM,5:00 PM - 5:30 PM'),
            ('Dr. Johnson', 'Orthopaedist', '10:00 AM - 10:30 AM,11:00 AM - 11:30 AM,2:00 PM - 2:30 PM,4:00 PM - 4:30 PM,5:00 PM - 5:30 PM'),
            ('Dr. Williams', 'Cardiologist', '10:00 AM - 10:30 AM,11:00 AM - 11:30 AM,2:00 PM - 2:30 PM,4:00 PM - 4:30 PM,5:00 PM - 5:30 PM,5:00 PM - 5:30 PM'),
            ('Dr. Brown', 'Neurologist', '10:00 AM - 10:30 AM,11:00 AM - 11:30 AM,2:00 PM - 2:30 PM,4:00 PM - 4:30 PM,5:00 PM - 5:30 PM')
        ]
        
        cursor.executemany(
            "INSERT IGNORE INTO doctors (name, specialization, available_slots) VALUES (%s, %s, %s)",
            doctors
        )
        
        print("Generating test data...")
        cursor = mysql.connection.cursor()
        
        # 1. Generate 21 random users
        for i in range(1, 21):
            name = f"User{i}"
            email = f"user{i}@example.com"
            password = "password123"  # Same password for all test users
            try:
                cursor.execute(
                    "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                    (name, email, password)
                )
            except MySQLdb.IntegrityError:
                pass  # Skip if user already exists
        
        mysql.connection.commit()
        
        # 2. Generate random appointments for these users
        doctor_types = ['Gynecologist', 'Orthopaedist', 'Cardiologist', 'Neurologist']
        purposes = ['Regular Checkup', 'Fever', 'Headache', 'Back Pain', 'Heart Issues', 'Pregnancy']
        
        for user_id in range(1, 101):
            # Each user gets 1-3 random appointments
            for _ in range(random.randint(1, 3)):
                patient_name = f"Patient{random.randint(1, 1000)}"
                patient_age = random.randint(1, 80)
                patient_sex = random.choice(['Male', 'Female'])
                purpose = random.choice(purposes)
                doctor_type = random.choice(doctor_types)
                
                # Get available slots for this doctor type
                cursor.execute(
                    "SELECT available_slots FROM doctors WHERE specialization = %s",
                    (doctor_type,)
                )
                doctor = cursor.fetchone()
                
                if doctor and doctor['available_slots']:
                    available_slots = [slot.strip() for slot in doctor['available_slots'].split(',') if slot.strip()]
                    if available_slots:
                        time_slot = random.choice(available_slots)
                        temperature = round(random.uniform(96.0, 104.0), 1)
                        medicines = random.choice(['Paracetamol', 'Ibuprofen', 'Aspirin', 'None'])
                        description = f"Patient complains of {purpose.lower()}"
                        token = random.randint(1000, 9999)
                        
                        cursor.execute("""
                            INSERT INTO appointments (
                                user_id, patient_name, patient_age, patient_sex, purpose,
                                doctor_type, time_slot, temperature, medicines, description, token
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            user_id, patient_name, patient_age, patient_sex, purpose,
                            doctor_type, time_slot, temperature, medicines, description, token
                        ))
        
        mysql.connection.commit()
        cursor.close()
        print("Finished generating test data")        
        
        mysql.connection.commit()
        cursor.close()

# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        
        if user and user['password'] == password:
            session['user_id'] = user['user_id']
            session['user_email'] = user['email']
            return redirect(url_for('patient_details'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, password)
            )
            mysql.connection.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except MySQLdb.IntegrityError:
            flash('Email already exists', 'error')
        finally:
            cursor.close()
    
    return render_template('registration.html')

@app.route('/patient_details', methods=['GET', 'POST'])
def patient_details():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        session['patient_name'] = request.form['name']
        session['patient_age'] = request.form['age']
        session['patient_sex'] = request.form['sex']
        session['patient_purpose'] = request.form['purpose']
        return redirect(url_for('select_doctor'))
    
    return render_template('patient.html')

@app.route('/select_doctor', methods=['GET', 'POST'])
def select_doctor():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT DISTINCT specialization FROM doctors")
    specializations = [row['specialization'] for row in cursor.fetchall()]
    cursor.close()
    
    if request.method == 'POST':
        session['doctor_type'] = request.form['doctor']
        return redirect(url_for('select_time_slot'))
    
    return render_template('doctor.html', specializations=specializations)

@app.route('/select_time_slot', methods=['GET', 'POST'])
def select_time_slot():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT available_slots FROM doctors WHERE specialization = %s",
        (session['doctor_type'],)
    )
    doctor = cursor.fetchone()
    cursor.close()
    
    if not doctor:
        flash('No available doctors for this specialization', 'error')
        return redirect(url_for('select_doctor'))
    
    time_slots = [slot.strip() for slot in doctor['available_slots'].split(',') if slot.strip()]
    
    if request.method == 'POST':
        try:
            session['time_slot'] = request.form['time_slot']
            session['temperature'] = request.form['temperature']
            session['medicines'] = request.form['medicines']
            session['description'] = request.form['description']
            
            # Generate token and save appointment
            token = random.randint(1000, 9999)
            cursor = mysql.connection.cursor()
            
            cursor.execute("""
                INSERT INTO appointments (
                    user_id, patient_name, patient_age, patient_sex, purpose,
                    doctor_type, time_slot, temperature, medicines, description, token
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                session['user_id'], session['patient_name'], session['patient_age'],
                session['patient_sex'], session['patient_purpose'], session['doctor_type'],
                session['time_slot'], session['temperature'], session['medicines'],
                session['description'], token
            ))
            
            mysql.connection.commit()
            cursor.close()
            
            # Clear session data
            for key in ['patient_name', 'patient_age', 'patient_sex', 'patient_purpose',
                       'doctor_type', 'time_slot', 'temperature', 'medicines', 'description']:
                session.pop(key, None)
            
            return render_template('token.html', token=token)
        
        except Exception as e:
            flash(f'Error creating appointment: {str(e)}', 'error')
            return redirect(url_for('select_time_slot'))
    
    return render_template('timings.html', time_slots=time_slots)

@app.route('/appointment/<int:appointment_id>')
def view_appointment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    appointment = get_appointment(appointment_id)
    if not appointment:
        flash('Appointment not found', 'error')
        return redirect(url_for('appointment_history'))
    
    return render_template('view_appointment.html', appointment=appointment)

@app.route('/appointment_history')
def appointment_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT 
            appointment_id,
            patient_name,
            doctor_type,
            time_slot,
            purpose,
            DATE_FORMAT(created_at, '%%Y-%%m-%%d %%H:%%i') as formatted_date,
            token
        FROM appointments 
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (session['user_id'],))
    appointments = cursor.fetchall()
    cursor.close()
    
    return render_template('history.html', appointments=appointments)

@app.route('/admin/add_doctor', methods=['GET', 'POST'])
def admin_add_doctor():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        add_doctor(
            request.form['name'],
            request.form['specialization'],
            request.form['slots']
        )
        flash('Doctor added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_doctor.html')

@app.route('/forgot_password')
def forgot_password():
    return render_template('forgotpassword.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Create database and tables if they don't exist
    try:
        init_db()
    except Exception as e:
        print(f"Database initialization error: {e}")
    
    app.run(debug=True)