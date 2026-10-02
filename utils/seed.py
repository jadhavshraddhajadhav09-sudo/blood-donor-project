from datetime import date, timedelta
from models import db, Donor, EmergencyRequest, AdminUser
from config import Config

def seed_database():
    """Seed sample data if tables are empty."""
    # Seed or sync Admin User from environment variables
    if Config.ADMIN_USERNAME and Config.ADMIN_PASSWORD:
        admin = AdminUser.query.filter_by(username=Config.ADMIN_USERNAME).first()
        if not admin:
            admin = AdminUser(username=Config.ADMIN_USERNAME)
            admin.set_password(Config.ADMIN_PASSWORD)
            db.session.add(admin)
            print(f"Created admin user '{Config.ADMIN_USERNAME}' from environment settings.")
        else:
            admin.set_password(Config.ADMIN_PASSWORD)
            print(f"Updated password for admin user '{Config.ADMIN_USERNAME}' from environment settings.")


    # Seed Donors if empty
    if Donor.query.count() == 0:
        sample_donors = [
            # Eligible donors (> 90 days or no previous donation)
            {
                'full_name': 'Rahul Sharma', 'age': 28, 'gender': 'Male',
                'phone_number': '9876543210', 'email': 'rahul.s@example.com',
                'blood_group': 'O+', 'city': 'Mumbai', 'area': 'Andheri West',
                'last_donation_date': date.today() - timedelta(days=120),
                'is_available': True, 'consent_given': True
            },
            {
                'full_name': 'Priya Patel', 'age': 24, 'gender': 'Female',
                'phone_number': '9876543211', 'email': 'priya.p@example.com',
                'blood_group': 'A+', 'city': 'Mumbai', 'area': 'Bandra East',
                'last_donation_date': None, # First time donor
                'is_available': True, 'consent_given': True
            },
            {
                'full_name': 'Amit Kumar', 'age': 35, 'gender': 'Male',
                'phone_number': '9876543212', 'email': 'amit.k@example.com',
                'blood_group': 'O-', 'city': 'Delhi', 'area': 'Connaught Place',
                'last_donation_date': date.today() - timedelta(days=105),
                'is_available': True, 'consent_given': True
            },
            {
                'full_name': 'Sneha Reddy', 'age': 30, 'gender': 'Female',
                'phone_number': '9876543213', 'email': 'sneha.r@example.com',
                'blood_group': 'B+', 'city': 'Bangalore', 'area': 'Koramangala',
                'last_donation_date': date.today() - timedelta(days=95),
                'is_available': True, 'consent_given': True
            },
            {
                'full_name': 'Vikram Singh', 'age': 42, 'gender': 'Male',
                'phone_number': '9876543214', 'email': 'vikram.s@example.com',
                'blood_group': 'AB+', 'city': 'Delhi', 'area': 'Saket',
                'last_donation_date': date.today() - timedelta(days=150),
                'is_available': True, 'consent_given': True
            },
            {
                'full_name': 'Ananya Roy', 'age': 26, 'gender': 'Female',
                'phone_number': '9876543215', 'email': 'ananya.r@example.com',
                'blood_group': 'AB-', 'city': 'Kolkata', 'area': 'Salt Lake',
                'last_donation_date': date.today() - timedelta(days=180),
                'is_available': True, 'consent_given': True
            },
            {
                'full_name': 'David Miller', 'age': 33, 'gender': 'Male',
                'phone_number': '9876543216', 'email': 'david.m@example.com',
                'blood_group': 'B-', 'city': 'Pune', 'area': 'Viman Nagar',
                'last_donation_date': date.today() - timedelta(days=200),
                'is_available': True, 'consent_given': True
            },
            {
                'full_name': 'Kavita Joshi', 'age': 29, 'gender': 'Female',
                'phone_number': '9876543217', 'email': 'kavita.j@example.com',
                'blood_group': 'A-', 'city': 'Mumbai', 'area': 'Dadars',
                'last_donation_date': date.today() - timedelta(days=110),
                'is_available': True, 'consent_given': True
            },
            # Non-eligible donors (donated within last 90 days - cooling period)
            {
                'full_name': 'Rohan Mehta', 'age': 31, 'gender': 'Male',
                'phone_number': '9876543218', 'email': 'rohan.m@example.com',
                'blood_group': 'O+', 'city': 'Mumbai', 'area': 'Powai',
                'last_donation_date': date.today() - timedelta(days=35), # In cooling period!
                'is_available': True, 'consent_given': True
            },
            {
                'full_name': 'Deepika Verma', 'age': 27, 'gender': 'Female',
                'phone_number': '9876543219', 'email': 'deepika.v@example.com',
                'blood_group': 'B+', 'city': 'Bangalore', 'area': 'Indiranagar',
                'last_donation_date': date.today() - timedelta(days=50), # In cooling period!
                'is_available': True, 'consent_given': True
            }
        ]

        for d_data in sample_donors:
            donor = Donor(**d_data)
            db.session.add(donor)
        print("Seeded sample donors!")

    # Seed Emergency Requests if empty
    if EmergencyRequest.query.count() == 0:
        sample_requests = [
            {
                'patient_name': 'Suresh Chandra',
                'blood_group': 'O+',
                'units_required': 3,
                'hospital_name': 'Lilavati Hospital & Research Centre',
                'city': 'Mumbai',
                'contact_person': 'Mahesh Chandra',
                'contact_phone': '9812345670',
                'urgency': 'Critical',
                'required_by_date': date.today() + timedelta(days=1),
                'notes': 'Urgent requirement for cardiac surgery. Any O+ or O- blood donor please reach immediately.',
                'status': 'Active'
            },
            {
                'patient_name': 'Meera Sen',
                'blood_group': 'A+',
                'units_required': 2,
                'hospital_name': 'AIIMS Trauma Center',
                'city': 'Delhi',
                'contact_person': 'Sunil Sen',
                'contact_phone': '9812345671',
                'urgency': 'Urgent',
                'required_by_date': date.today() + timedelta(days=2),
                'notes': 'Platelet transfusion needed. Please contact patient attendant.',
                'status': 'Active'
            },
            {
                'patient_name': 'Arjun Nair',
                'blood_group': 'B+',
                'units_required': 1,
                'hospital_name': 'Manipal Hospital',
                'city': 'Bangalore',
                'contact_person': 'Sita Nair',
                'contact_phone': '9812345672',
                'urgency': 'Normal',
                'required_by_date': date.today() + timedelta(days=3),
                'notes': 'Routine replacement for scheduled orthopaedic procedure.',
                'status': 'Active'
            },
            {
                'patient_name': 'Sunita Rao',
                'blood_group': 'AB+',
                'units_required': 2,
                'hospital_name': 'Ruby Hall Clinic',
                'city': 'Pune',
                'contact_person': 'Rajesh Rao',
                'contact_phone': '9812345673',
                'urgency': 'Critical',
                'required_by_date': date.today(),
                'notes': 'Emergency ICU admission. All universal donors welcome.',
                'status': 'Fulfilled'
            }
        ]

        for req_data in sample_requests:
            req = EmergencyRequest(**req_data)
            db.session.add(req)
        print("Seeded sample emergency requests!")

    db.session.commit()
