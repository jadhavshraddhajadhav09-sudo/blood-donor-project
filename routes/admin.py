from functools import wraps
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from models import db, AdminUser, Donor, EmergencyRequest
from utils.validators import validate_donor_form, validate_request_form, VALID_BLOOD_GROUPS, VALID_URGENCIES

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in to access the Admin Dashboard.', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin Login route."""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        admin = AdminUser.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['admin_logged_in'] = True
            session['admin_username'] = admin.username
            flash(f'Welcome back, {admin.username}!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('admin/login.html')


@admin_bp.route('/logout')
def logout():
    """Admin Logout route."""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('admin.login'))


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin Dashboard route."""
    donors = Donor.query.order_by(Donor.created_at.desc()).all()
    requests = EmergencyRequest.query.order_by(EmergencyRequest.created_at.desc()).all()

    total_donors = len(donors)
    eligible_donors_count = sum(1 for d in donors if d.is_eligible and d.is_available)
    active_requests_count = sum(1 for r in requests if r.status == 'Active')
    fulfilled_requests_count = sum(1 for r in requests if r.status == 'Fulfilled')

    # Calculate blood group distribution count
    bg_counts = {bg: 0 for bg in VALID_BLOOD_GROUPS}
    for d in donors:
        if d.blood_group in bg_counts:
            bg_counts[d.blood_group] += 1

    return render_template(
        'admin/dashboard.html',
        total_donors=total_donors,
        eligible_donors_count=eligible_donors_count,
        active_requests_count=active_requests_count,
        fulfilled_requests_count=fulfilled_requests_count,
        donors=donors,
        requests=requests,
        bg_counts=bg_counts,
        blood_groups=VALID_BLOOD_GROUPS,
        urgencies=VALID_URGENCIES
    )


@admin_bp.route('/api/stats')
@admin_required
def get_chart_stats():
    """API endpoint providing JSON data for Admin Chart.js charts."""
    donors = Donor.query.all()
    bg_counts = {bg: 0 for bg in VALID_BLOOD_GROUPS}
    for d in donors:
        if d.blood_group in bg_counts:
            bg_counts[d.blood_group] += 1

    req_counts = {
        'Active': EmergencyRequest.query.filter_by(status='Active').count(),
        'Fulfilled': EmergencyRequest.query.filter_by(status='Fulfilled').count(),
        'Cancelled': EmergencyRequest.query.filter_by(status='Cancelled').count()
    }

    return jsonify({
        'blood_groups': list(bg_counts.keys()),
        'donor_counts': list(bg_counts.values()),
        'request_status': list(req_counts.keys()),
        'request_counts': list(req_counts.values())
    })


@admin_bp.route('/donor/<int:donor_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_donor(donor_id):
    """Admin route to edit a donor's profile."""
    donor = Donor.query.get_or_404(donor_id)

    if request.method == 'POST':
        is_valid, errors, data = validate_donor_form(request.form)

        # Allow keeping current phone number if unchanged
        if data.get('phone_number') != donor.phone_number:
            existing = Donor.query.filter_by(phone_number=data.get('phone_number')).first()
            if existing:
                errors.append("Another donor is already registered with this phone number.")
                is_valid = False

        if not is_valid:
            for error in errors:
                flash(error, 'danger')
            return render_template('admin/edit_donor.html', donor=donor, blood_groups=VALID_BLOOD_GROUPS)

        donor.full_name = data['full_name']
        donor.age = data['age']
        donor.gender = data['gender']
        donor.phone_number = data['phone_number']
        donor.email = data['email']
        donor.blood_group = data['blood_group']
        donor.city = data['city']
        donor.area = data['area']
        donor.last_donation_date = data['last_donation_date']
        donor.is_available = data['is_available']

        db.session.commit()
        flash(f"Donor profile for '{donor.full_name}' updated successfully.", 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_donor.html', donor=donor, blood_groups=VALID_BLOOD_GROUPS)


@admin_bp.route('/donor/<int:donor_id>/delete', methods=['POST'])
@admin_required
def delete_donor(donor_id):
    """Admin route to delete a donor."""
    donor = Donor.query.get_or_404(donor_id)
    name = donor.full_name
    db.session.delete(donor)
    db.session.commit()
    flash(f"Donor '{name}' has been deleted.", 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/request/<int:request_id>/edit', methods=['POST'])
@admin_required
def edit_request(request_id):
    """Admin route to edit emergency request details."""
    req = EmergencyRequest.query.get_or_404(request_id)

    patient_name = request.form.get('patient_name', '').strip()
    blood_group = request.form.get('blood_group', '').strip()
    units = int(request.form.get('units_required', 1))
    hospital = request.form.get('hospital_name', '').strip()
    city = request.form.get('city', '').strip()
    contact_person = request.form.get('contact_person', '').strip()
    contact_phone = request.form.get('contact_phone', '').strip()
    urgency = request.form.get('urgency', 'Normal')
    status = request.form.get('status', 'Active')

    if patient_name and blood_group and hospital and city and contact_person and contact_phone:
        req.patient_name = patient_name
        req.blood_group = blood_group
        req.units_required = units
        req.hospital_name = hospital
        req.city = city
        req.contact_person = contact_person
        req.contact_phone = contact_phone
        req.urgency = urgency
        req.status = status
        db.session.commit()
        flash(f"Emergency request for '{patient_name}' updated.", 'success')
    else:
        flash("Failed to update request. Missing required fields.", 'danger')

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/request/<int:request_id>/delete', methods=['POST'])
@admin_required
def delete_request(request_id):
    """Admin route to delete an emergency request."""
    req = EmergencyRequest.query.get_or_404(request_id)
    patient = req.patient_name
    db.session.delete(req)
    db.session.commit()
    flash(f"Emergency request for '{patient}' deleted.", 'info')
    return redirect(url_for('admin.dashboard'))
