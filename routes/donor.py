from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from models import db, Donor
from utils.validators import validate_donor_form, VALID_BLOOD_GROUPS

donor_bp = Blueprint('donor', __name__)

@donor_bp.route('/register-donor', methods=['GET', 'POST'])
def register():
    """Register as Blood Donor route."""
    if request.method == 'POST':
        is_valid, errors, data = validate_donor_form(request.form)

        if not is_valid:
            for error in errors:
                flash(error, 'danger')
            return render_template('donor_register.html', form_data=request.form, blood_groups=VALID_BLOOD_GROUPS)

        # Check for duplicate phone number
        existing_phone = Donor.query.filter_by(phone_number=data['phone_number']).first()
        if existing_phone:
            flash('A donor with this 10-digit phone number is already registered.', 'warning')
            return render_template('donor_register.html', form_data=request.form, blood_groups=VALID_BLOOD_GROUPS)

        try:
            donor = Donor(**data)
            db.session.add(donor)
            db.session.commit()
            flash('Registration successful! Thank you for joining our life-saving donor registry.', 'success')
            return redirect(url_for('donor.find_donors', blood_group=donor.blood_group, city=donor.city))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during registration: {str(e)}', 'danger')
            return render_template('donor_register.html', form_data=request.form, blood_groups=VALID_BLOOD_GROUPS)

    return render_template('donor_register.html', form_data={}, blood_groups=VALID_BLOOD_GROUPS)


@donor_bp.route('/find-donors', methods=['GET'])
def find_donors():
    """Find and search donors route with filtering by blood group, city, and availability."""
    blood_group = request.args.get('blood_group', '').strip().upper()
    city = request.args.get('city', '').strip()
    availability = request.args.get('availability', 'all').strip()

    query = Donor.query

    if blood_group and blood_group in VALID_BLOOD_GROUPS:
        query = query.filter_by(blood_group=blood_group)

    if city:
        query = query.filter(Donor.city.ilike(f'%{city}%'))

    if availability == 'available':
        query = query.filter_by(is_available=True)

    donors_list = query.order_by(Donor.is_available.desc(), Donor.created_at.desc()).all()

    # Get list of unique cities for quick filter dropdown
    cities = db.session.query(Donor.city).distinct().order_by(Donor.city).all()
    city_options = [c[0] for c in cities if c[0]]

    return render_template(
        'find_donors.html',
        donors=donors_list,
        selected_bg=blood_group,
        selected_city=city,
        selected_availability=availability,
        blood_groups=VALID_BLOOD_GROUPS,
        cities=city_options
    )


@donor_bp.route('/api/donor/<int:donor_id>/contact', methods=['GET'])
def get_donor_contact(donor_id):
    """API endpoint to reveal full phone number when 'Show Contact' is clicked."""
    donor = Donor.query.get_or_404(donor_id)
    return jsonify({
        'success': True,
        'donor_id': donor.id,
        'phone_number': donor.phone_number,
        'full_name': donor.full_name
    })
