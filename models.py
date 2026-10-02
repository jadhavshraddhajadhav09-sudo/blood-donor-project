from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Blood Compatibility Rules Matrix (Recipient -> Compatible Donor Groups)
BLOOD_COMPATIBILITY = {
    'A+': ['A+', 'A-', 'O+', 'O-'],
    'A-': ['A-', 'O-'],
    'B+': ['B+', 'B-', 'O+', 'O-'],
    'B-': ['B-', 'O-'],
    'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
    'AB-': ['AB-', 'A-', 'B-', 'O-'],
    'O+': ['O+', 'O-'],
    'O-': ['O-']
}

class Donor(db.Model):
    __tablename__ = 'donors'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False, index=True)
    city = db.Column(db.String(100), nullable=False, index=True)
    area = db.Column(db.String(100), nullable=False)
    last_donation_date = db.Column(db.Date, nullable=True)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    consent_given = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def days_since_last_donation(self):
        if not self.last_donation_date:
            return None
        return (date.today() - self.last_donation_date).days

    @property
    def is_eligible(self):
        """Donor is eligible if 90 days have passed since last donation or no donation history recorded."""
        if not self.last_donation_date:
            return True
        return self.days_since_last_donation >= 90

    @property
    def days_until_eligible(self):
        if self.is_eligible or not self.last_donation_date:
            return 0
        return max(0, 90 - self.days_since_last_donation)

    @property
    def masked_phone(self):
        if len(self.phone_number) == 10:
            return f"{self.phone_number[:5]}*****"
        elif len(self.phone_number) > 5:
            return f"{self.phone_number[:3]}******{self.phone_number[-2:]}"
        return "**********"

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'age': self.age,
            'gender': self.gender,
            'masked_phone': self.masked_phone,
            'phone_number': self.phone_number,
            'email': self.email,
            'blood_group': self.blood_group,
            'city': self.city,
            'area': self.area,
            'last_donation_date': self.last_donation_date.strftime('%Y-%m-%d') if self.last_donation_date else 'Never',
            'is_available': self.is_available,
            'is_eligible': self.is_eligible,
            'days_until_eligible': self.days_until_eligible,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }


class EmergencyRequest(db.Model):
    __tablename__ = 'emergency_requests'

    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False, index=True)
    units_required = db.Column(db.Integer, nullable=False, default=1)
    hospital_name = db.Column(db.String(150), nullable=False)
    city = db.Column(db.String(100), nullable=False, index=True)
    contact_person = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(15), nullable=False)
    urgency = db.Column(db.String(20), nullable=False, default='Normal') # Critical, Urgent, Normal
    required_by_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Active') # Active, Fulfilled, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def compatible_donor_groups(self):
        return BLOOD_COMPATIBILITY.get(self.blood_group, [self.blood_group])

    def to_dict(self):
        return {
            'id': self.id,
            'patient_name': self.patient_name,
            'blood_group': self.blood_group,
            'units_required': self.units_required,
            'hospital_name': self.hospital_name,
            'city': self.city,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'urgency': self.urgency,
            'required_by_date': self.required_by_date.strftime('%Y-%m-%d'),
            'notes': self.notes or '',
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }


class AdminUser(db.Model):
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
