import re
from datetime import datetime, date

VALID_BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
VALID_GENDERS = ['Male', 'Female', 'Other']
VALID_URGENCIES = ['Critical', 'Urgent', 'Normal']

def validate_phone(phone):
    """Validate that phone number is exactly 10 digits."""
    if not phone:
        return False, "Phone number is required."
    clean_phone = phone.strip()
    if not re.match(r'^\d{10}$', clean_phone):
        return False, "Phone number must be exactly 10 digits."
    return True, clean_phone

def validate_age(age):
    """Validate age between 18 and 65."""
    try:
        age_int = int(age)
        if age_int < 18 or age_int > 65:
            return False, "Donor age must be between 18 and 65 years."
        return True, age_int
    except (ValueError, TypeError):
        return False, "Age must be a valid number."

def validate_email(email):
    """Validate email format."""
    if not email:
        return False, "Email address is required."
    email_clean = email.strip().lower()
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(regex, email_clean):
        return False, "Please enter a valid email address."
    return True, email_clean

def validate_blood_group(bg):
    """Validate blood group against standard options."""
    if not bg or bg.upper() not in VALID_BLOOD_GROUPS:
        return False, f"Invalid blood group. Must be one of: {', '.join(VALID_BLOOD_GROUPS)}"
    return True, bg.upper()

def validate_donor_form(data):
    """Comprehensive validation for Donor Registration form."""
    errors = []

    # Name
    name = data.get('full_name', '').strip()
    if not name or len(name) < 2:
        errors.append("Full name must be at least 2 characters long.")

    # Age
    is_valid_age, age_res = validate_age(data.get('age'))
    if not is_valid_age:
        errors.append(age_res)

    # Gender
    gender = data.get('gender', '')
    if gender not in VALID_GENDERS:
        errors.append("Please select a valid gender option.")

    # Phone
    is_valid_phone, phone_res = validate_phone(data.get('phone_number'))
    if not is_valid_phone:
        errors.append(phone_res)

    # Email
    is_valid_email, email_res = validate_email(data.get('email'))
    if not is_valid_email:
        errors.append(email_res)

    # Blood Group
    is_valid_bg, bg_res = validate_blood_group(data.get('blood_group'))
    if not is_valid_bg:
        errors.append(bg_res)

    # City & Area
    city = data.get('city', '').strip()
    area = data.get('area', '').strip()
    if not city:
        errors.append("City is required.")
    if not area:
        errors.append("Area / Locality is required.")

    # Last Donation Date
    last_date = None
    last_date_str = data.get('last_donation_date', '').strip()
    if last_date_str:
        try:
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d').date()
            if last_date > date.today():
                errors.append("Last donation date cannot be in the future.")
        except ValueError:
            errors.append("Invalid last donation date format. Use YYYY-MM-DD.")

    # Consent
    consent = data.get('consent_given')
    if not consent or consent in ['false', '0', False]:
        errors.append("You must agree to the privacy consent to register as a donor.")

    return len(errors) == 0, errors, {
        'full_name': name,
        'age': age_res if is_valid_age else None,
        'gender': gender,
        'phone_number': phone_res if is_valid_phone else None,
        'email': email_res if is_valid_email else None,
        'blood_group': bg_res if is_valid_bg else None,
        'city': city,
        'area': area,
        'last_donation_date': last_date,
        'is_available': data.get('is_available') in ['true', 'True', True, 'on', 'yes', '1'],
        'consent_given': True
    }


def validate_request_form(data):
    """Comprehensive validation for Emergency Request form."""
    errors = []

    patient_name = data.get('patient_name', '').strip()
    if not patient_name or len(patient_name) < 2:
        errors.append("Patient name must be at least 2 characters.")

    is_valid_bg, bg_res = validate_blood_group(data.get('blood_group'))
    if not is_valid_bg:
        errors.append(bg_res)

    try:
        units = int(data.get('units_required', 1))
        if units < 1 or units > 20:
            errors.append("Units required must be between 1 and 20.")
    except (ValueError, TypeError):
        errors.append("Units required must be a valid number.")
        units = 1

    hospital_name = data.get('hospital_name', '').strip()
    if not hospital_name:
        errors.append("Hospital name and address are required.")

    city = data.get('city', '').strip()
    if not city:
        errors.append("City is required.")

    contact_person = data.get('contact_person', '').strip()
    if not contact_person:
        errors.append("Contact person name is required.")

    is_valid_phone, phone_res = validate_phone(data.get('contact_phone'))
    if not is_valid_phone:
        errors.append(phone_res)

    urgency = data.get('urgency', 'Normal')
    if urgency not in VALID_URGENCIES:
        urgency = 'Normal'

    req_date = None
    req_date_str = data.get('required_by_date', '').strip()
    if not req_date_str:
        errors.append("Required-by date is required.")
    else:
        try:
            req_date = datetime.strptime(req_date_str, '%Y-%m-%d').date()
            if req_date < date.today():
                errors.append("Required-by date cannot be in the past.")
        except ValueError:
            errors.append("Invalid required-by date format.")

    notes = data.get('notes', '').strip()

    return len(errors) == 0, errors, {
        'patient_name': patient_name,
        'blood_group': bg_res if is_valid_bg else None,
        'units_required': units,
        'hospital_name': hospital_name,
        'city': city,
        'contact_person': contact_person,
        'contact_phone': phone_res if is_valid_phone else None,
        'urgency': urgency,
        'required_by_date': req_date,
        'notes': notes
    }
