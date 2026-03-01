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

# ─────────────────────────────────────────────
#  App Configuration
# ─────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'cpds_secret_key_2024'

# MySQL Configuration – update credentials before running
app.config['MYSQL_HOST']     = 'localhost'
app.config['MYSQL_USER']     = 'root'
app.config['MYSQL_PASSWORD'] = 'mysql'          # ← set your MySQL password here
app.config['MYSQL_DB']       = 'cpds_main'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# File upload settings
app.config['UPLOAD_FOLDER']    = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024   # 5 MB
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

mysql = MySQL(app)


@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(role):
    """Decorator – ensures the correct role is logged in."""
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

# ── Student Auth ──────────────────────────────
@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        name   = request.form['name'].strip()
        email  = request.form['email'].strip()
        password = generate_password_hash(request.form['password'])
        branch = request.form['branch']
        cgpa   = float(request.form['cgpa'])
        skills = request.form['skills'].strip()
        phone  = request.form['phone'].strip()

        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM students WHERE email=%s", (email,))
        if cur.fetchone():
            flash('Email already registered.', 'danger')
            return redirect(url_for('student_register'))

        cur.execute(
            "INSERT INTO students (name,email,password,branch,cgpa,skills,phone) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (name, email, password, branch, cgpa, skills, phone)
        )
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


# ── Company Auth ──────────────────────────────
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


# ── Admin Auth ────────────────────────────────
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

    # Stats
    cur.execute("SELECT COUNT(*) AS cnt FROM applications WHERE student_id=%s", (sid,))
    total_apps = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) AS cnt FROM applications WHERE student_id=%s AND status='Selected'", (sid,))
    selected   = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) AS cnt FROM applications WHERE student_id=%s AND status='Shortlisted'", (sid,))
    shortlisted = cur.fetchone()['cnt']

    # Eligible jobs count
    cur.execute(
        "SELECT COUNT(*) AS cnt FROM jobs WHERE min_cgpa<=%s AND deadline>=CURDATE() AND (eligible_branch=%s OR eligible_branch='All')",
        (student['cgpa'], student['branch'])
    )
    eligible_jobs = cur.fetchone()['cnt']

    # Recent applications
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
        name   = request.form['name'].strip()
        branch = request.form['branch']
        cgpa   = float(request.form['cgpa'])
        skills = request.form['skills'].strip()
        phone  = request.form['phone'].strip()

        resume_filename = None
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename and allowed_file(file.filename):
                resume_filename = secure_filename(f"resume_{sid}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], resume_filename))

        if resume_filename:
            cur.execute(
                "UPDATE students SET name=%s,branch=%s,cgpa=%s,skills=%s,phone=%s,resume=%s WHERE id=%s",
                (name, branch, cgpa, skills, phone, resume_filename, sid)
            )
        else:
            cur.execute(
                "UPDATE students SET name=%s,branch=%s,cgpa=%s,skills=%s,phone=%s WHERE id=%s",
                (name, branch, cgpa, skills, phone, sid)
            )
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
        cid        = session['user_id']
        role       = request.form['role'].strip()
        package    = float(request.form['package'])
        min_cgpa   = float(request.form['min_cgpa'])
        eligible_branch = request.form['eligible_branch']
        skills     = request.form['skills'].strip()
        deadline   = request.form['deadline']
        description = request.form.get('description', '').strip()
        location   = request.form.get('location', '').strip()

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
        SELECT a.*, s.name, s.email, s.branch, s.cgpa, s.skills, s.phone, s.resume
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
    if status not in ('Applied', 'Shortlisted', 'Rejected', 'Selected'):
        flash('Invalid status.', 'danger')
        return redirect(request.referrer)

    cur = mysql.connection.cursor()
    cur.execute("UPDATE applications SET status=%s WHERE id=%s", (status, app_id))
    mysql.connection.commit()
    cur.close()
    flash(f'Application status updated to {status}.', 'success')
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

    # Branch-wise stats
    cur.execute("""
        SELECT s.branch,
               COUNT(DISTINCT s.id) AS total_students,
               COUNT(DISTINCT CASE WHEN a.status='Selected' THEN a.student_id END) AS placed
        FROM students s
        LEFT JOIN applications a ON s.id=a.student_id
        GROUP BY s.branch
    """)
    branch_stats = cur.fetchall()

    # Recent applications
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


# ─────────────────────────────────────────────
#  Run
# ─────────────────────────────────────────────
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True);