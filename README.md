# 🎓 College Placement Database System (CPDS)

A full-featured **College Placement Management System** built with **Python Flask** and **MySQL** — designed for educational institutions to manage the entire campus recruitment lifecycle.

---

## 🌟 Features

### 👨‍🎓 Student Module
- Register / Login with hashed passwords
- Create & edit profile (Name, Branch, CGPA, Skills, Resume)
- View **eligible** jobs automatically filtered by CGPA & branch
- Apply to jobs with one click
- Track application status in real time (Applied → Shortlisted → Selected / Rejected)

### 🏢 Company Module
- Register / Login
- Post jobs with role, package, CGPA threshold, branch eligibility, deadline
- Browse applicants for each job (sorted by CGPA)
- Update application status: Shortlist / Reject / Select students
- View/download student resumes

### 🛡️ Admin Module
- Secure admin login
- Dashboard with KPI cards and **Chart.js** visualisations
- Branch-wise placement statistics
- Manage all students, companies, jobs, and applications
- Generate **Placement Report** (placed vs not-yet-placed)
- Delete students/companies (cascades cleanly)

---

## 🗂️ Project Structure

```
college_placement/
├── app.py                   # Main Flask application (all routes)
├── setup_admin.py           # One-time admin account creator
├── database.sql             # Full schema + sample data
├── requirements.txt         # Python dependencies
├── README.md
├── static/
│   ├── css/
│   │   └── style.css        # Custom styles
│   └── uploads/             # Student resumes (PDF/DOC)
└── templates/
    ├── base.html             # Shared layout (navbar, flash, footer)
    ├── index.html            # Landing page
    ├── auth/
    │   ├── student_login.html
    │   ├── student_register.html
    │   ├── company_login.html
    │   ├── company_register.html
    │   └── admin_login.html
    ├── student/
    │   ├── dashboard.html
    │   ├── profile.html
    │   ├── jobs.html
    │   └── applications.html
    ├── company/
    │   ├── dashboard.html
    │   ├── post_job.html
    │   ├── jobs.html
    │   └── applicants.html
    └── admin/
        ├── dashboard.html
        ├── students.html
        ├── companies.html
        ├── jobs.html
        ├── applications.html
        └── report.html
```

---

## 🛢️ Database Schema

```
admin          students        companies
  └──────────────────────────────────┐
                    ↓                ↓
                  jobs  ←── company_id (FK)
                    ↓
              applications
               ├── student_id (FK → students)
               └── job_id     (FK → jobs)
```

| Table        | Primary Key | Foreign Keys                      |
|--------------|-------------|-----------------------------------|
| `admin`      | `id`        | —                                 |
| `students`   | `id`        | —                                 |
| `companies`  | `id`        | —                                 |
| `jobs`       | `id`        | `company_id → companies(id)`      |
| `applications`| `id`       | `student_id → students(id)`, `job_id → jobs(id)` |

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/college-placement-db-system.git
cd college-placement-db-system
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Linux note:** you may need `sudo apt install libmysqlclient-dev` before pip install.

### 4. Create the MySQL database

```bash
mysql -u root -p
```

```sql
source database.sql;
```

### 5. Configure database credentials

Open `app.py` and update:

```python
app.config['MYSQL_HOST']     = 'localhost'
app.config['MYSQL_USER']     = 'root'
app.config['MYSQL_PASSWORD'] = 'YOUR_MYSQL_PASSWORD'
app.config['MYSQL_DB']       = 'college_placement_db'
```

### 6. Create the admin account

```bash
python setup_admin.py
```

Default credentials created: `admin` / `admin@123`

### 7. Run the application

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## 🔐 Default Login Credentials

| Role    | URL                    | Username / Email         | Password    |
|---------|------------------------|--------------------------|-------------|
| Admin   | `/admin/login`         | `admin`                  | `admin@123` |
| Student | `/student/login`       | Register first           | —           |
| Company | `/company/login`       | Register first           | —           |

---

## 🖥️ Tech Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| Backend     | Python 3.x, Flask 3.x             |
| Database    | MySQL 8.x, Flask-MySQLdb          |
| Frontend    | HTML5, Bootstrap 5.3, Bootstrap Icons |
| Charts      | Chart.js 4.x                      |
| Security    | Werkzeug password hashing, Flask sessions |

---

## 📸 Screenshots

| Page | Description |
|------|-------------|
| Landing Page | Hero section with role-based login |
| Student Dashboard | KPI cards + recent applications |
| Jobs Page | Filtered job listings with apply button |
| Company Applicants | Sortable table with status updates |
| Admin Dashboard | Charts + branch-wise placement stats |
| Placement Report | Placed vs not-placed summary |

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🤝 Contributing

Pull requests are welcome! Please open an issue first to discuss changes.

---

**Built with ❤️ using Flask & MySQL**
