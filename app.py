"""
College Placement Database System
Main Flask Application
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ─────────────────────────────────────────────
#  App Configuration
# ─────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'cpds_secret_key_2024'

# MySQL Configuration
app.config['MYSQL_HOST']        = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER']        = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD']    = os.environ.get('MYSQL_PASSWORD', 'mysql')
app.config['MYSQL_DB']          = os.environ.get('MYSQL_DATABASE', 'cpds_main')
app.config['MYSQL_PORT']        = int(os.environ.get('MYSQL_PORT', 3306))

# File upload settings
app.config['UPLOAD_FOLDER']      = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

# Email Configuration
SMTP_EMAIL    = 'sharnk027@gmail.com'
SMTP_PASSWORD = 'zguhkniyyosiwmyf'
SMTP_SERVER   = 'smtp.gmail.com'
SMTP_PORT     = 587

mysql = MySQL(app)


@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}


# ─────────────────────────────────────────────
#  Email Functions
# ─────────────────────────────────────────────
def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From']    = SMTP_EMAIL
        msg['To']      = to_email
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def send_shortlist_email(student_name, student_email, company_name, job_role):
    subject = f"Congratulations! You are Shortlisted - {job_role} at {company_name}"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px;">
      <div style="max-width: 600px; margin: auto; background: white;
                  border-radius: 10px; padding: 30px;
                  border-top: 5px solid #ffc107;">
        <h2 style="color: #ffc107;">You Have Been Shortlisted!</h2>
        <p>Dear <strong>{student_name}</strong>,</p>
        <p>You have been <strong>shortlisted</strong> for:</p>
        <div style="background: #fff8e1; padding: 15px;
                    border-radius: 8px; margin: 20px 0;">
          <p><strong>Company:</strong> {company_name}</p>
          <p><strong>Job Role:</strong> {job_role}</p>
          <p><strong>Status:</strong>
             <span style="color: #ffc107; font-weight: bold;">Shortlisted</span></p>
        </div>
        <p>Please log in to your placement portal to check updates.</p>
        <a href="http://127.0.0.1:5000/student/login"
           style="background: #ffc107; color: white; padding: 12px 25px;
                  text-decoration: none; border-radius: 5px;
                  display: inline-block; margin-top: 10px;">
          View Application Status
        </a>
        <br><br>
        <p style="color: #888; font-size: 12px;">
          College Placement Database System<br>
          This is an automated email. Please do not reply.
        </p>
      </div>
    </body>
    </html>
    """
    return send_email(student_email, subject, body)


def send_selected_email(student_name, student_email, company_name, job_role, package):
    subject = f"Congratulations! You are Selected - {job_role} at {company_name}"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px;">
      <div style="max-width: 600px; margin: auto; background: white;
                  border-radius: 10px; padding: 30px;
                  border-top: 5px solid #28a745;">
        <h2 style="color: #28a745;">Congratulations! You Are Selected!</h2>
        <p>Dear <strong>{student_name}</strong>,</p>
        <p>You have been <strong>selected</strong> for:</p>
        <div style="background: #e8f5e9; padding: 15px;
                    border-radius: 8px; margin: 20px 0;">
          <p><strong>Company:</strong> {company_name}</p>
          <p><strong>Job Role:</strong> {job_role}</p>
          <p><strong>Package:</strong> {package} LPA</p>
          <p><strong>Status:</strong>
             <span style="color: #28a745; font-weight: bold;">Selected</span></p>
        </div>
        <p>The company will contact you soon with joining details.</p>
        <a href="http://127.0.0.1:5000/student/login"
           style="background: #28a745; color: white; padding: 12px 25px;
                  text-decoration: none; border-radius: 5px;
                  display: inline-block; margin-top: 10px;">
          View Application Status
        </a>
        <br><br>
        <p style="color: #888; font-size: 12px;">
          College Placement Database System<br>
          This is an automated email. Please do not reply.
        </p>
      </div>
    </body>
    </html>
    """
    return send_email(student_email, subject, body)


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or session.get('role') != role:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for(f'{role}_login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ─────────────────────────────────────────────
#  Home
# ─────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


# ══════════════════════════════════════════════
#  AUTHENTICATION ROUTES
# ══════════════════════════════════════════════

# Student Auth
@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        name       = request.form['name'].strip()
        email      = request.form['email'].strip()
        password   = generate_password_hash(request.form['password'])
        branch     = request.form['branch']
        cgpa       = float(request.form['cgpa'])
        skills     = request.form['skills'].strip()
        phone      = request.form['phone'].strip()
        college    = request.form.get('college', '').strip()
        department = request.form.get('department', '').strip()

        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM students WHERE email=%s", (email,))
        if cur.fetchone():
            flash('Email already registered.', 'danger')
            return redirect(url_for('student_register'))

        cur.execute("""
            INSERT INTO students
            (name, email, password, branch, cgpa, skills, phone, college, department)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, email, password, branch, cgpa, skills, phone, college, department))
        mysql.connection.commit()
        cur.close()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('student_login'))
    return render_template('auth/student_register.html')


@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email    = request.form['email'].strip()
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students WHERE email=%s", (email,))
        student = cur.fetchone()
        cur.close()
        if student and check_password_hash(student['password'], password):
            session['user_id']   = student['id']
            session['user_name'] = student['name']
            session['role']      = 'student'
            flash(f"Welcome back, {student['name']}!", 'success')
            return redirect(url_for('student_dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/student_login.html')


@app.route('/student/logout')
def student_logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('student_login'))


# Company Auth
@app.route('/company/register', methods=['GET', 'POST'])
def company_register():
    if request.method == 'POST':
        name     = request.form['name'].strip()
        email    = request.form['email'].strip()
        password = generate_password_hash(request.form['password'])
        industry = request.form['industry'].strip()
        website  = request.form.get('website', '').strip()
        about    = request.form.get('about', '').strip()

        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM companies WHERE email=%s", (email,))
        if cur.fetchone():
            flash('Email already registered.', 'danger')
            return redirect(url_for('company_register'))

        cur.execute(
            "INSERT INTO companies (name,email,password,industry,website,about) VALUES (%s,%s,%s,%s,%s,%s)",
            (name, email, password, industry, website, about)
        )
        mysql.connection.commit()
        cur.close()
        flash('Company registered successfully!', 'success')
        return redirect(url_for('company_login'))
    return render_template('auth/company_register.html')


@app.route('/company/login', methods=['GET', 'POST'])
def company_login():
    if request.method == 'POST':
        email    = request.form['email'].strip()
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM companies WHERE email=%s", (email,))
        company = cur.fetchone()
        cur.close()
        if company and check_password_hash(company['password'], password):
            session['user_id']   = company['id']
            session['user_name'] = company['name']
            session['role']      = 'company'
            flash(f"Welcome, {company['name']}!", 'success')
            return redirect(url_for('company_dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/company_login.html')


@app.route('/company/logout')
def company_logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('company_login'))


# Admin Auth
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admin WHERE username=%s", (username,))
        admin = cur.fetchone()
        cur.close()
        if admin and check_password_hash(admin['password'], password):
            session['user_id']   = admin['id']
            session['user_name'] = admin['username']
            session['role']      = 'admin'
            flash('Admin logged in.', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('auth/admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Admin logged out.', 'info')
    return redirect(url_for('admin_login'))


# ══════════════════════════════════════════════
#  STUDENT ROUTES
# ══════════════════════════════════════════════
@app.route('/student/dashboard')
@login_required('student')
def student_dashboard():
    cur = mysql.connection.cursor()
    sid = session['user_id']
    cur.execute("SELECT * FROM students WHERE id=%s", (sid,))
    student = cur.fetchone()

    cur.execute("SELECT COUNT(*) AS cnt FROM applications WHERE student_id=%s", (sid,))
    total_apps = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) AS cnt FROM applications WHERE student_id=%s AND status='Selected'", (sid,))
    selected = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) AS cnt FROM applications WHERE student_id=%s AND status='Shortlisted'", (sid,))
    shortlisted = cur.fetchone()['cnt']

    cur.execute(
        "SELECT COUNT(*) AS cnt FROM jobs WHERE min_cgpa<=%s AND deadline>=CURDATE() AND (eligible_branch=%s OR eligible_branch='All')",
        (student['cgpa'], student['branch'])
    )
    eligible_jobs = cur.fetchone()['cnt']

    cur.execute("""
        SELECT a.*, j.role, j.package, c.name AS company_name
        FROM applications a
        JOIN jobs j ON a.job_id=j.id
        JOIN companies c ON j.company_id=c.id
        WHERE a.student_id=%s
        ORDER BY a.applied_at DESC LIMIT 5
    """, (sid,))
    recent_apps = cur.fetchall()
    cur.close()

    return render_template('student/dashboard.html',
                           student=student, total_apps=total_apps,
                           selected=selected, shortlisted=shortlisted,
                           eligible_jobs=eligible_jobs, recent_apps=recent_apps)


@app.route('/student/profile', methods=['GET', 'POST'])
@login_required('student')
def student_profile():
    cur = mysql.connection.cursor()
    sid = session['user_id']
    if request.method == 'POST':
        name       = request.form['name'].strip()
        branch     = request.form['branch']
        cgpa       = float(request.form['cgpa'])
        skills     = request.form['skills'].strip()
        phone      = request.form['phone'].strip()
        college    = request.form.get('college', '').strip()
        department = request.form.get('department', '').strip()

        resume_filename = None
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename and allowed_file(file.filename):
                resume_filename = secure_filename(f"resume_{sid}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], resume_filename))

        if resume_filename:
            cur.execute("""
                UPDATE students
                SET name=%s, branch=%s, cgpa=%s, skills=%s, phone=%s,
                    college=%s, department=%s, resume=%s
                WHERE id=%s
            """, (name, branch, cgpa, skills, phone, college, department, resume_filename, sid))
        else:
            cur.execute("""
                UPDATE students
                SET name=%s, branch=%s, cgpa=%s, skills=%s, phone=%s,
                    college=%s, department=%s
                WHERE id=%s
            """, (name, branch, cgpa, skills, phone, college, department, sid))

        mysql.connection.commit()
        flash('Profile updated successfully!', 'success')

    cur.execute("SELECT * FROM students WHERE id=%s", (sid,))
    student = cur.fetchone()
    cur.close()
    return render_template('student/profile.html', student=student)


@app.route('/student/jobs')
@login_required('student')
def student_jobs():
    cur = mysql.connection.cursor()
    sid = session['user_id']
    cur.execute("SELECT * FROM students WHERE id=%s", (sid,))
    student = cur.fetchone()

    cur.execute("""
        SELECT j.*, c.name AS company_name, c.industry,
               (SELECT COUNT(*) FROM applications WHERE job_id=j.id AND student_id=%s) AS applied
        FROM jobs j
        JOIN companies c ON j.company_id=c.id
        WHERE j.min_cgpa<=%s AND j.deadline>=CURDATE()
          AND (j.eligible_branch=%s OR j.eligible_branch='All')
        ORDER BY j.posted_at DESC
    """, (sid, student['cgpa'], student['branch']))
    jobs = cur.fetchall()
    cur.close()
    return render_template('student/jobs.html', jobs=jobs, student=student)


@app.route('/student/apply/<int:job_id>', methods=['POST'])
@login_required('student')
def student_apply(job_id):
    sid = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM applications WHERE student_id=%s AND job_id=%s", (sid, job_id))
    if cur.fetchone():
        flash('You have already applied for this job.', 'warning')
    else:
        cur.execute("INSERT INTO applications (student_id, job_id, status) VALUES (%s,%s,'Applied')", (sid, job_id))
        mysql.connection.commit()
        flash('Application submitted successfully!', 'success')
    cur.close()
    return redirect(url_for('student_jobs'))


@app.route('/student/applications')
@login_required('student')
def student_applications():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT a.*, j.role, j.package, j.deadline, c.name AS company_name, c.industry
        FROM applications a
        JOIN jobs j ON a.job_id=j.id
        JOIN companies c ON j.company_id=c.id
        WHERE a.student_id=%s
        ORDER BY a.applied_at DESC
    """, (session['user_id'],))
    apps = cur.fetchall()
    cur.close()
    return render_template('student/applications.html', apps=apps)


# ══════════════════════════════════════════════
#  COMPANY ROUTES
# ══════════════════════════════════════════════
@app.route('/company/dashboard')
@login_required('company')
def company_dashboard():
    cid = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM companies WHERE id=%s", (cid,))
    company = cur.fetchone()

    cur.execute("SELECT COUNT(*) AS cnt FROM jobs WHERE company_id=%s", (cid,))
    total_jobs = cur.fetchone()['cnt']
    cur.execute("""
        SELECT COUNT(*) AS cnt FROM applications a
        JOIN jobs j ON a.job_id=j.id WHERE j.company_id=%s
    """, (cid,))
    total_apps = cur.fetchone()['cnt']
    cur.execute("""
        SELECT COUNT(*) AS cnt FROM applications a
        JOIN jobs j ON a.job_id=j.id WHERE j.company_id=%s AND a.status='Selected'
    """, (cid,))
    selected = cur.fetchone()['cnt']

    cur.execute("""
        SELECT j.*, COUNT(a.id) AS applicant_count
        FROM jobs j LEFT JOIN applications a ON j.id=a.job_id
        WHERE j.company_id=%s GROUP BY j.id ORDER BY j.posted_at DESC LIMIT 5
    """, (cid,))
    recent_jobs = cur.fetchall()
    cur.close()

    return render_template('company/dashboard.html',
                           company=company, total_jobs=total_jobs,
                           total_apps=total_apps, selected=selected,
                           recent_jobs=recent_jobs)


@app.route('/company/post-job', methods=['GET', 'POST'])
@login_required('company')
def company_post_job():
    if request.method == 'POST':
        cid             = session['user_id']
        role            = request.form['role'].strip()
        package         = float(request.form['package'])
        min_cgpa        = float(request.form['min_cgpa'])
        eligible_branch = request.form['eligible_branch']
        skills          = request.form['skills'].strip()
        deadline        = request.form['deadline']
        description     = request.form.get('description', '').strip()
        location        = request.form.get('location', '').strip()

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO jobs (company_id,role,package,min_cgpa,eligible_branch,skills,deadline,description,location)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (cid, role, package, min_cgpa, eligible_branch, skills, deadline, description, location))
        mysql.connection.commit()
        cur.close()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('company_jobs'))
    return render_template('company/post_job.html')


@app.route('/company/jobs')
@login_required('company')
def company_jobs():
    cid = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT j.*, COUNT(a.id) AS applicant_count
        FROM jobs j LEFT JOIN applications a ON j.id=a.job_id
        WHERE j.company_id=%s GROUP BY j.id ORDER BY j.posted_at DESC
    """, (cid,))
    jobs = cur.fetchall()
    cur.close()
    return render_template('company/jobs.html', jobs=jobs)


@app.route('/company/applicants/<int:job_id>')
@login_required('company')
def company_applicants(job_id):
    cid = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM jobs WHERE id=%s AND company_id=%s", (job_id, cid))
    job = cur.fetchone()
    if not job:
        flash('Job not found.', 'danger')
        return redirect(url_for('company_jobs'))

    cur.execute("""
        SELECT a.*, s.name, s.email, s.branch, s.cgpa, s.skills,
               s.college, s.department, s.phone, s.resume
        FROM applications a
        JOIN students s ON a.student_id=s.id
        WHERE a.job_id=%s ORDER BY s.cgpa DESC
    """, (job_id,))
    applicants = cur.fetchall()
    cur.close()
    return render_template('company/applicants.html', job=job, applicants=applicants)


@app.route('/company/update-status/<int:app_id>', methods=['POST'])
@login_required('company')
def company_update_status(app_id):
    status = request.form['status']
    cur    = mysql.connection.cursor()

    cur.execute("""
        SELECT s.name, s.email, c.name AS company_name,
               j.role, j.package
        FROM applications a
        JOIN students s  ON a.student_id = s.id
        JOIN jobs j      ON a.job_id     = j.id
        JOIN companies c ON j.company_id = c.id
        WHERE a.id = %s
    """, (app_id,))
    details = cur.fetchone()

    cur.execute("UPDATE applications SET status=%s WHERE id=%s", (status, app_id))
    mysql.connection.commit()
    cur.close()

    if details:
        if status == 'Shortlisted':
            send_shortlist_email(
                details['name'],
                details['email'],
                details['company_name'],
                details['role']
            )
            flash(f"Status updated to Shortlisted. Email sent to {details['name']}.", 'success')
        elif status == 'Selected':
            send_selected_email(
                details['name'],
                details['email'],
                details['company_name'],
                details['role'],
                details['package']
            )
            flash(f"Congratulations email sent to {details['name']}.", 'success')
        else:
            flash(f"Status updated to {status}.", 'success')
    else:
        flash('Status updated.', 'success')

    return redirect(request.referrer)


@app.route('/company/delete-job/<int:job_id>', methods=['POST'])
@login_required('company')
def company_delete_job(job_id):
    cid = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM applications WHERE job_id=%s", (job_id,))
    cur.execute("DELETE FROM jobs WHERE id=%s AND company_id=%s", (job_id, cid))
    mysql.connection.commit()
    cur.close()
    flash('Job deleted.', 'info')
    return redirect(url_for('company_jobs'))


# ══════════════════════════════════════════════
#  ADMIN ROUTES
# ══════════════════════════════════════════════
@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) AS cnt FROM students")
    total_students = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) AS cnt FROM companies")
    total_companies = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) AS cnt FROM jobs")
    total_jobs = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) AS cnt FROM applications WHERE status='Selected'")
    total_placed = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) AS cnt FROM applications")
    total_apps = cur.fetchone()['cnt']

    cur.execute("""
        SELECT s.branch,
               COUNT(DISTINCT s.id) AS total_students,
               COUNT(DISTINCT CASE WHEN a.status='Selected' THEN a.student_id END) AS placed
        FROM students s
        LEFT JOIN applications a ON s.id=a.student_id
        GROUP BY s.branch
    """)
    branch_stats = cur.fetchall()

    cur.execute("""
        SELECT a.*, s.name AS student_name, j.role, c.name AS company_name
        FROM applications a
        JOIN students s ON a.student_id=s.id
        JOIN jobs j ON a.job_id=j.id
        JOIN companies c ON j.company_id=c.id
        ORDER BY a.applied_at DESC LIMIT 8
    """)
    recent_apps = cur.fetchall()
    cur.close()

    return render_template('admin/dashboard.html',
                           total_students=total_students, total_companies=total_companies,
                           total_jobs=total_jobs, total_placed=total_placed,
                           total_apps=total_apps, branch_stats=branch_stats,
                           recent_apps=recent_apps)


@app.route('/admin/students')
@login_required('admin')
def admin_students():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT s.*,
               COUNT(DISTINCT a.id) AS total_apps,
               SUM(CASE WHEN a.status='Selected' THEN 1 ELSE 0 END) AS selected
        FROM students s LEFT JOIN applications a ON s.id=a.student_id
        GROUP BY s.id ORDER BY s.name
    """)
    students = cur.fetchall()
    cur.close()
    return render_template('admin/students.html', students=students)


@app.route('/admin/companies')
@login_required('admin')
def admin_companies():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT c.*, COUNT(DISTINCT j.id) AS total_jobs,
               COUNT(DISTINCT CASE WHEN a.status='Selected' THEN a.id END) AS total_hired
        FROM companies c
        LEFT JOIN jobs j ON c.id=j.company_id
        LEFT JOIN applications a ON j.id=a.job_id
        GROUP BY c.id ORDER BY c.name
    """)
    companies = cur.fetchall()
    cur.close()
    return render_template('admin/companies.html', companies=companies)


@app.route('/admin/jobs')
@login_required('admin')
def admin_jobs():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT j.*, c.name AS company_name, COUNT(a.id) AS applicant_count
        FROM jobs j
        JOIN companies c ON j.company_id=c.id
        LEFT JOIN applications a ON j.id=a.job_id
        GROUP BY j.id ORDER BY j.posted_at DESC
    """)
    jobs = cur.fetchall()
    cur.close()
    return render_template('admin/jobs.html', jobs=jobs)


@app.route('/admin/applications')
@login_required('admin')
def admin_applications():
    status_filter = request.args.get('status', 'all')
    cur = mysql.connection.cursor()
    if status_filter != 'all':
        cur.execute("""
            SELECT a.*, s.name AS student_name, s.branch, s.cgpa,
                   s.college, s.department,
                   j.role, c.name AS company_name
            FROM applications a
            JOIN students s ON a.student_id=s.id
            JOIN jobs j ON a.job_id=j.id
            JOIN companies c ON j.company_id=c.id
            WHERE a.status=%s ORDER BY a.applied_at DESC
        """, (status_filter,))
    else:
        cur.execute("""
            SELECT a.*, s.name AS student_name, s.branch, s.cgpa,
                   s.college, s.department,
                   j.role, c.name AS company_name
            FROM applications a
            JOIN students s ON a.student_id=s.id
            JOIN jobs j ON a.job_id=j.id
            JOIN companies c ON j.company_id=c.id
            ORDER BY a.applied_at DESC
        """)
    apps = cur.fetchall()
    cur.close()
    return render_template('admin/applications.html', apps=apps, status_filter=status_filter)


@app.route('/admin/delete-student/<int:sid>', methods=['POST'])
@login_required('admin')
def admin_delete_student(sid):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM applications WHERE student_id=%s", (sid,))
    cur.execute("DELETE FROM students WHERE id=%s", (sid,))
    mysql.connection.commit()
    cur.close()
    flash('Student deleted.', 'info')
    return redirect(url_for('admin_students'))


@app.route('/admin/delete-company/<int:cid>', methods=['POST'])
@login_required('admin')
def admin_delete_company(cid):
    cur = mysql.connection.cursor()
    cur.execute("""
        DELETE a FROM applications a
        JOIN jobs j ON a.job_id=j.id WHERE j.company_id=%s
    """, (cid,))
    cur.execute("DELETE FROM jobs WHERE company_id=%s", (cid,))
    cur.execute("DELETE FROM companies WHERE id=%s", (cid,))
    mysql.connection.commit()
    cur.close()
    flash('Company deleted.', 'info')
    return redirect(url_for('admin_companies'))


@app.route('/admin/report')
@login_required('admin')
def admin_report():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT s.name, s.branch, s.cgpa, s.skills,
               c.name AS company, j.role, j.package, a.status, a.applied_at
        FROM applications a
        JOIN students s ON a.student_id=s.id
        JOIN jobs j ON a.job_id=j.id
        JOIN companies c ON j.company_id=c.id
        WHERE a.status='Selected'
        ORDER BY j.package DESC
    """)
    placed = cur.fetchall()

    cur.execute("""
        SELECT s.name, s.branch, s.cgpa, s.skills
        FROM students s
        WHERE s.id NOT IN (
            SELECT DISTINCT student_id FROM applications WHERE status='Selected'
        )
    """)
    not_placed = cur.fetchall()
    cur.close()
    return render_template('admin/report.html', placed=placed, not_placed=not_placed)


@app.route('/test-email')
def test_email():
    result = send_email(
        'sharnk027@gmail.com',
        'Test Email from CPDS',
        '<h1>Email is working!</h1><p>Your email setup is correct.</p>'
    )
    if result:
        return 'Email sent successfully! Check your inbox.'
    else:
        return 'Email failed. Check CMD window for error.'


# ─────────────────────────────────────────────
#  Run
# ─────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)