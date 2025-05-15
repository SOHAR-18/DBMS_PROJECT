// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
}

function validatePassword(password) {
    return password.length >= 6;
}

// Login form validation
document.querySelector('#loginPage form')?.addEventListener('submit', function(e) {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    if (!validateEmail(email)) {
        alert('Please enter a valid email address.');
        e.preventDefault();
        return;
    }
    
    if (!validatePassword(password)) {
        alert('Password must be at least 6 characters long.');
        e.preventDefault();
        return;
    }
});

// Registration form validation
document.querySelector('#registerPage form')?.addEventListener('submit', function(e) {
    const name = document.getElementById('reg_name').value;
    const email = document.getElementById('reg_email').value;
    const password = document.getElementById('reg_password').value;
    
    if (name.trim() === '') {
        alert('Please enter your name.');
        e.preventDefault();
        return;
    }
    
    if (!validateEmail(email)) {
        alert('Please enter a valid email address.');
        e.preventDefault();
        return;
    }
    
    if (!validatePassword(password)) {
        alert('Password must be at least 6 characters long.');
        e.preventDefault();
        return;
    }
});

// Patient form validation
document.querySelector('#patientPage form')?.addEventListener('submit', function(e) {
    const name = document.querySelector('#patientPage input[name="name"]').value;
    const age = document.querySelector('#patientPage input[name="age"]').value;
    const sex = document.querySelector('#patientPage select[name="sex"]').value;
    const purpose = document.querySelector('#patientPage input[name="purpose"]').value;
    
    if (name.trim() === '') {
        alert('Please enter patient name.');
        e.preventDefault();
        return;
    }
    
    if (age === '' || isNaN(age) || age <= 0 || age > 120) {
        alert('Please enter a valid age between 1 and 120.');
        e.preventDefault();
        return;
    }
    
    if (sex === '') {
        alert('Please select patient sex.');
        e.preventDefault();
        return;
    }
    
    if (purpose.trim() === '') {
        alert('Please enter purpose of visit.');
        e.preventDefault();
        return;
    }
});

// Time slot form validation
document.querySelector('#timeSlotPage form')?.addEventListener('submit', function(e) {
    const timeSlot = document.querySelector('#timeSlotPage select[name="time_slot"]').value;
    const temperature = document.querySelector('#timeSlotPage input[name="temperature"]').value;
    const description = document.querySelector('#timeSlotPage textarea[name="description"]').value;
    
    if (timeSlot === '') {
        alert('Please select a time slot.');
        e.preventDefault();
        return;
    }
    
    if (temperature === '' || isNaN(temperature)) {
        alert('Please enter a valid temperature.');
        e.preventDefault();
        return;
    }
    
    if (description.trim() === '') {
        alert('Please describe your issue.');
        e.preventDefault();
        return;
    }
});

// Toggle password visibility
document.addEventListener('DOMContentLoaded', function() {
    const passwordToggles = document.querySelectorAll('.password-toggle');
    
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    });
});