# 🩸 Community Blood Donor Registry and Emergency Request System

A modern, responsive, full-stack web application designed for voluntary blood donor registration, emergency blood request management, automated 90-day eligibility checking, and instant donor matching.

Built as a **College Mini Project** using **Python Flask**, **SQLite (SQLAlchemy ORM)**, **Bootstrap 5**, and **Chart.js**.

---

## 🌟 Key Features

### 🩸 Donor Management & Registration
- **Comprehensive Fields**: Full name, age (18–65), gender, 10-digit phone number, email, blood group (A+, A-, B+, B-, AB+, AB-, O+, O-), city, area, last donation date, availability status, and privacy consent.
- **Automated 90-Day Eligibility Rule**: Donors are automatically flagged as **Eligible** only if $\ge 90$ days have elapsed since their last donation (or if first-time donor). Donors within 90 days are shown in a **Cooling Period** state with days remaining.
- **Duplicate Prevention**: Backend & frontend validation blocks duplicate 10-digit phone numbers and enforces valid input formats.

### 🔍 Find Donors & Privacy Protection
- **Instant Search & Filter**: Filter donors by blood group, city/location, and availability status.
- **Privacy Masking**: Donor phone numbers are masked by default (e.g., `98765*****`) to protect user privacy.
- **One-Click Contact Reveal**: Users click **Show Contact** to retrieve the verified number and launch a direct phone call (`tel:` protocol).

### 🚨 Emergency Blood Requests
- **Request Creation**: Submit patient requirements specifying blood group, bags/units required, hospital name, city, urgency level (Critical / Urgent / Normal), required-by date, and case notes.
- **Urgency Ordering**: Active requests are automatically prioritized with **Critical** requests at the top.
- **Automated Donor Matching**: Click **Matching Donors** on any request to view compatible available donors in that city based on medical blood compatibility rules (including Universal Donor O- and Universal Recipient AB+).
- **Fulfill Status**: Requesters or admins can mark completed requests as **Fulfilled**.

### 🛡️ Admin Dashboard & Analytics
- **Secure Authentication**: Password-protected admin portal with Werkzeug password hashing.
- **Interactive Chart**: Real-time **Chart.js** bar chart displaying donor distribution across blood groups.
- **Summary Cards**: Quick count stats for total donors, eligible donors, active requests, and fulfilled requests.
- **Full CRUD Management**: View, edit, and delete donor profiles and emergency requests.

### 🔒 Security & Deployment Ready
- **Security Protections**: SQL Injection protection via SQLAlchemy ORM, XSS prevention via Jinja2 auto-escaping, CSRF token validation via Flask-WTF.
- **Custom Error Pages**: Styled 404 and 500 pages.
- **Environment Variables**: Key settings managed securely via `.env` file using `python-dotenv`.
- **Render Deployment Ready**: Includes `Procfile` (`web: gunicorn app:app`) and `requirements.txt`.

---

## 📁 Project Directory Structure

```text
blood donar p1/
├── app.py                   # Main Flask application entrypoint & factory
├── config.py                # Application configuration & env settings
├── models.py                # SQLAlchemy Models (Donor, EmergencyRequest, AdminUser)
├── requirements.txt         # Python dependencies
├── Procfile                 # Deployment file for Render / Heroku
├── .env.example             # Template for environment variables
├── .env                     # Local environment variables
├── README.md                # Project documentation
├── routes/
│   ├── main.py              # Routes for Home, About, Contact
│   ├── donor.py             # Routes for Donor Registration, Search & Contact Reveal API
│   ├── request.py           # Routes for Emergency Requests & Matching Donors API
│   └── admin.py             # Routes for Admin Auth, Dashboard & CRUD operations
├── utils/
│   ├── validators.py        # Form & input validation routines
│   └── seed.py              # Database seeding script for sample donors & requests
├── static/
│   ├── css/
│   │   └── style.css        # Custom CSS styles, glassmorphism & animations
│   ├── js/
│   │   └── main.js          # Client-side AJAX, modal handlers, phone unmasking & Chart.js
│   └── images/
│       └── logo.svg         # Blood drop vector logo
└── templates/
    ├── base.html            # Base Jinja2 layout template with Navbar & Footer
    ├── home.html            # Landing page with stats, search & urgent requests
    ├── donor_register.html  # Donor registration form
    ├── find_donors.html     # Searchable donor directory with cards
    ├── request_create.html  # Post emergency request form
    ├── active_requests.html # Active emergency requests list & matching donors modal
    ├── about.html           # About page & blood compatibility chart
    ├── contact.html         # Contact support page
    ├── 404.html             # Friendly 404 error page
    ├── 500.html             # Friendly 500 error page
    └── admin/
        ├── login.html       # Secure Admin Login
        ├── dashboard.html   # Admin Dashboard with Stats, Chart & CRUD
        └── edit_donor.html  # Admin edit donor form
```

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.8 or higher installed on your system.

### Step 1: Clone or Open Project Directory
Navigated to your project folder:
```bash
cd "c:\Users\Admin\OneDrive\Desktop\blood donar p1"
```

### Step 2: Create a Virtual Environment (Optional but Recommended)
On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```
On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

Upon launching, the app will automatically create the SQLite database (`instance/blood_donor.db`) and seed initial sample donors, active emergency requests, and the default admin account.

### Step 5: Access the Website
Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 🔑 Admin Credentials Configuration

- **Admin Login URL**: `http://127.0.0.1:5000/admin/login`
- **Configured in `.env`**:
  - `ADMIN_USERNAME`: Configured in your local `.env` file (e.g., `admin`)
  - `ADMIN_PASSWORD`: Configured in your local `.env` file (e.g., `AdminSecurePass2026!`)

*(Note: `.env.example` contains placeholders only for security best practices.)*


---

## 🌐 Deploying to Render

Deploying this Flask application on [Render](https://render.com) is free and straightforward:

1. **Push to GitHub**: Commit your project files and push them to a GitHub repository.
2. **Create New Web Service on Render**:
   - Connect your GitHub repository.
   - Select **Python** runtime environment.
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
3. **Set Environment Variables**:
   Add the following in Render's Environment Settings:
   - `SECRET_KEY`: *Any random strong secret string*
   - `ADMIN_USERNAME`: `admin`
   - `ADMIN_PASSWORD`: *Your custom password*
4. **Deploy**: Render will automatically build and deploy your live URL!

---

## 🔒 Privacy & Safety Statement

> **Privacy Note**: Donor contact details stored in LifeBlood Registry are used strictly for emergency blood donation requests. Phone numbers are masked in public search results and accessed only on demand by verified users.
