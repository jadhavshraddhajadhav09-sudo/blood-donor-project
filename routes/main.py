from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import Donor, EmergencyRequest, BLOOD_COMPATIBILITY

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Home page route with statistics and featured emergency requests."""
    total_donors = Donor.query.count()

    # Calculate eligible donors count (last_donation_date is None or >= 90 days ago)
    all_donors = Donor.query.all()
    eligible_donors_count = sum(1 for d in all_donors if d.is_eligible and d.is_available)

    active_requests = EmergencyRequest.query.filter_by(status='Active').order_by(
        EmergencyRequest.urgency == 'Critical',
        EmergencyRequest.created_at.desc()
    ).limit(3).all()

    active_requests_count = EmergencyRequest.query.filter_by(status='Active').count()
    fulfilled_requests_count = EmergencyRequest.query.filter_by(status='Fulfilled').count()

    return render_template(
        'home.html',
        total_donors=total_donors,
        eligible_donors_count=eligible_donors_count,
        active_requests_count=active_requests_count,
        fulfilled_requests_count=fulfilled_requests_count,
        featured_requests=active_requests,
        blood_groups=['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    )

@main_bp.route('/about')
def about():
    """About page route with donation rules and blood compatibility guide."""
    return render_template('about.html', blood_matrix=BLOOD_COMPATIBILITY)

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page route with contact form handling."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()

        if name and email and message:
            flash(f"Thank you, {name}! Your message has been received. Our team will contact you shortly.", "success")
            return redirect(url_for('main.contact'))
        else:
            flash("Please fill in all required fields.", "danger")

    return render_template('contact.html')
