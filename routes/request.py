from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from models import db, EmergencyRequest, Donor, BLOOD_COMPATIBILITY
from utils.validators import validate_request_form, VALID_BLOOD_GROUPS, VALID_URGENCIES

request_bp = Blueprint('request', __name__)

@request_bp.route('/emergency-request', methods=['GET', 'POST'])
def create_request():
    """Submit Emergency Blood Request route."""
    if request.method == 'POST':
        is_valid, errors, data = validate_request_form(request.form)

        if not is_valid:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'request_create.html',
                form_data=request.form,
                blood_groups=VALID_BLOOD_GROUPS,
                urgencies=VALID_URGENCIES
            )

        try:
            req = EmergencyRequest(**data)
            db.session.add(req)
            db.session.commit()
            flash('Emergency Blood Request posted successfully! Matching donors can now view and respond to your request.', 'success')
            return redirect(url_for('request.active_requests'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting request: {str(e)}', 'danger')
            return render_template(
                'request_create.html',
                form_data=request.form,
                blood_groups=VALID_BLOOD_GROUPS,
                urgencies=VALID_URGENCIES
            )

    return render_template(
        'request_create.html',
        form_data={},
        blood_groups=VALID_BLOOD_GROUPS,
        urgencies=VALID_URGENCIES
    )


@request_bp.route('/active-requests', methods=['GET'])
def active_requests():
    """Active and Emergency Blood Requests page."""
    status_filter = request.args.get('status', 'Active')
    blood_group_filter = request.args.get('blood_group', '').strip().upper()
    city_filter = request.args.get('city', '').strip()

    query = EmergencyRequest.query

    if status_filter in ['Active', 'Fulfilled']:
        query = query.filter_by(status=status_filter)

    if blood_group_filter and blood_group_filter in VALID_BLOOD_GROUPS:
        query = query.filter_by(blood_group=blood_group_filter)

    if city_filter:
        query = query.filter(EmergencyRequest.city.ilike(f'%{city_filter}%'))

    # Sort order: Critical urgency first, then Urgent, then Normal, then newest first
    requests_list = query.order_by(
        EmergencyRequest.urgency == 'Critical',
        EmergencyRequest.urgency == 'Urgent',
        EmergencyRequest.created_at.desc()
    ).all()

    return render_template(
        'active_requests.html',
        requests=requests_list,
        selected_status=status_filter,
        selected_bg=blood_group_filter,
        selected_city=city_filter,
        blood_groups=VALID_BLOOD_GROUPS
    )


@request_bp.route('/request/<int:request_id>/fulfill', methods=['POST'])
def fulfill_request(request_id):
    """Mark an emergency request as Fulfilled."""
    req = EmergencyRequest.query.get_or_404(request_id)
    req.status = 'Fulfilled'
    db.session.commit()
    flash(f'Request for patient {req.patient_name} marked as Fulfilled. Thank you!', 'success')
    return redirect(url_for('request.active_requests'))


@request_bp.route('/api/request/<int:request_id>/matching-donors', methods=['GET'])
def get_matching_donors(request_id):
    """API endpoint to retrieve compatible available donors for an emergency request."""
    req = EmergencyRequest.query.get_or_404(request_id)

    # Compatible blood groups for this patient's blood group
    compatible_groups = BLOOD_COMPATIBILITY.get(req.blood_group, [req.blood_group])

    # Query donors in the same city or all cities matching compatible groups and available
    matching_donors = Donor.query.filter(
        Donor.blood_group.in_(compatible_groups),
        Donor.is_available == True
    ).all()

    # Filter for eligible donors (>= 90 days since last donation)
    results = []
    for d in matching_donors:
        if d.is_eligible:
            is_same_city = (d.city.lower().strip() == req.city.lower().strip())
            donor_dict = d.to_dict()
            donor_dict['is_same_city'] = is_same_city
            results.append(donor_dict)

    # Prioritize same city donors first
    results.sort(key=lambda x: not x['is_same_city'])

    return jsonify({
        'success': True,
        'request_id': req.id,
        'patient_name': req.patient_name,
        'blood_group_needed': req.blood_group,
        'compatible_groups': compatible_groups,
        'matching_donors': results
    })
