-- ═══════════════════════════════════════════════════════════
--  College Placement Database System — Schema & Sample Data
--  Database: college_placement_db
-- ═══════════════════════════════════════════════════════════

CREATE DATABASE IF NOT EXISTS college_placement_db;
USE college_placement_db;

-- ─────────────────────────────────────────────
--  TABLE: admin
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS admin (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email    VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────
--  TABLE: students
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS students (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(150)  NOT NULL,
    email      VARCHAR(150)  NOT NULL UNIQUE,
    password   VARCHAR(255)  NOT NULL,
    branch     VARCHAR(100)  NOT NULL,
    cgpa       DECIMAL(3,2)  NOT NULL CHECK (cgpa BETWEEN 0 AND 10),
    skills     TEXT,
    phone      VARCHAR(15),
    resume     VARCHAR(255),                         -- stored filename
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────
--  TABLE: companies
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS companies (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(200)  NOT NULL,
    email      VARCHAR(150)  NOT NULL UNIQUE,
    password   VARCHAR(255)  NOT NULL,
    industry   VARCHAR(100),
    website    VARCHAR(255),
    about      TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────
--  TABLE: jobs
--  One Company → Many Jobs
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jobs (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    company_id      INT          NOT NULL,
    role            VARCHAR(200) NOT NULL,
    package         DECIMAL(8,2) NOT NULL COMMENT 'LPA (Lakhs Per Annum)',
    min_cgpa        DECIMAL(3,2) NOT NULL,
    eligible_branch VARCHAR(100) NOT NULL DEFAULT 'All',
    skills          TEXT,
    description     TEXT,
    location        VARCHAR(200),
    deadline        DATE         NOT NULL,
    posted_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_job_company FOREIGN KEY (company_id)
        REFERENCES companies(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────
--  TABLE: applications
--  One Student → Many Applications
--  One Job     → Many Applications
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS applications (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    student_id  INT NOT NULL,
    job_id      INT NOT NULL,
    status      ENUM('Applied','Shortlisted','Rejected','Selected') NOT NULL DEFAULT 'Applied',
    applied_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY unique_application (student_id, job_id),

    CONSTRAINT fk_app_student FOREIGN KEY (student_id)
        REFERENCES students(id) ON DELETE CASCADE,
    CONSTRAINT fk_app_job    FOREIGN KEY (job_id)
        REFERENCES jobs(id)     ON DELETE CASCADE
);

-- ─────────────────────────────────────────────
--  Indexes for performance
-- ─────────────────────────────────────────────
CREATE INDEX idx_jobs_company    ON jobs(company_id);
CREATE INDEX idx_jobs_deadline   ON jobs(deadline);
CREATE INDEX idx_apps_student    ON applications(student_id);
CREATE INDEX idx_apps_job        ON applications(job_id);
CREATE INDEX idx_apps_status     ON applications(status);
CREATE INDEX idx_students_branch ON students(branch);


-- ═══════════════════════════════════════════════════════════
--  SAMPLE DATA
-- ═══════════════════════════════════════════════════════════

-- Admin  (password: admin@123)
INSERT INTO admin (username, password, email) VALUES
('admin', 'pbkdf2:sha256:600000$x3mK8vQn$e3c2a1b4d5f6e7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2', 'admin@cpds.edu');

-- ── Students (password for all: Pass@123)  ────────────────
-- We store hashed passwords; the raw value is Pass@1234
INSERT INTO students (name,email,password,branch,cgpa,skills,phone) VALUES
('Aarav Sharma',   'aarav@student.com',   'pbkdf2:sha256:600000$salt1$hashvalue1placeholder000000000000000000000000000000000000000', 'CSE', 8.75, 'Python, Django, MySQL, React', '9876543201'),
('Priya Patel',    'priya@student.com',   'pbkdf2:sha256:600000$salt2$hashvalue2placeholder000000000000000000000000000000000000000', 'IT',  8.20, 'Java, Spring Boot, AWS', '9876543202'),
('Rohan Mehta',    'rohan@student.com',   'pbkdf2:sha256:600000$salt3$hashvalue3placeholder000000000000000000000000000000000000000', 'ECE', 7.90, 'C++, Embedded Systems, VLSI', '9876543203'),
('Sneha Gupta',    'sneha@student.com',   'pbkdf2:sha256:600000$salt4$hashvalue4placeholder000000000000000000000000000000000000000', 'CSE', 9.10, 'Machine Learning, Python, TensorFlow', '9876543204'),
('Karan Singh',    'karan@student.com',   'pbkdf2:sha256:600000$salt5$hashvalue5placeholder000000000000000000000000000000000000000', 'ME',  7.50, 'AutoCAD, MATLAB, Solidworks', '9876543205'),
('Ananya Reddy',   'ananya@student.com',  'pbkdf2:sha256:600000$salt6$hashvalue6placeholder000000000000000000000000000000000000000', 'CSE', 8.60, 'JavaScript, Node.js, MongoDB', '9876543206'),
('Vikram Joshi',   'vikram@student.com',  'pbkdf2:sha256:600000$salt7$hashvalue7placeholder000000000000000000000000000000000000000', 'IT',  7.80, 'PHP, Laravel, MySQL', '9876543207'),
('Meera Nair',     'meera@student.com',   'pbkdf2:sha256:600000$salt8$hashvalue8placeholder000000000000000000000000000000000000000', 'ECE', 8.40, 'Signal Processing, MATLAB, Python', '9876543208'),
('Arjun Kumar',    'arjun@student.com',   'pbkdf2:sha256:600000$salt9$hashvalue9placeholder000000000000000000000000000000000000000', 'CSE', 6.80, 'HTML, CSS, JavaScript', '9876543209'),
('Divya Sharma',   'divya@student.com',   'pbkdf2:sha256:600000$salt0$hashvalue0placeholder000000000000000000000000000000000000000', 'CE',  7.20, 'AutoCAD, Staad Pro, ETABS', '9876543210');

-- NOTE: Run the following in Python to get correct hashes, then replace above:
-- from werkzeug.security import generate_password_hash
-- print(generate_password_hash('Pass@1234'))

-- ── Companies (password for all: Comp@123)  ──────────────
INSERT INTO companies (name,email,password,industry,website,about) VALUES
('TechCorp India',      'hr@techcorp.com',      'pbkdf2:sha256:600000$csalt1$chashvalue1placeholder00000000000000000000000000000000000', 'Information Technology', 'https://techcorp.example.com', 'Leading software solutions provider in India with 10,000+ employees.'),
('Infosys Limited',     'campus@infosys.com',   'pbkdf2:sha256:600000$csalt2$chashvalue2placeholder00000000000000000000000000000000000', 'IT Services',            'https://infosys.example.com', 'Global leader in next-generation digital services and consulting.'),
('Amazon India',        'campus@amazon.in',     'pbkdf2:sha256:600000$csalt3$chashvalue3placeholder00000000000000000000000000000000000', 'E-Commerce / Cloud',     'https://amazon.example.in',  'World-class e-commerce and cloud computing giant.'),
('Tata Consultancy',    'talent@tcs.com',       'pbkdf2:sha256:600000$csalt4$chashvalue4placeholder00000000000000000000000000000000000', 'IT Consulting',          'https://tcs.example.com',    'Multinational IT services, consulting, and business solutions.'),
('Siemens India',       'careers@siemens.in',   'pbkdf2:sha256:600000$csalt5$chashvalue5placeholder00000000000000000000000000000000000', 'Engineering',            'https://siemens.example.in', 'Global powerhouse in electronics and electrical engineering.');

-- ── Jobs  ─────────────────────────────────────────────────
INSERT INTO jobs (company_id,role,package,min_cgpa,eligible_branch,skills,description,location,deadline) VALUES
(1, 'Software Engineer',         12.00, 7.50, 'CSE',  'Python, Django, SQL',          'Build and maintain scalable web applications.',             'Bangalore',  DATE_ADD(CURDATE(), INTERVAL 30 DAY)),
(1, 'Data Analyst',              10.00, 7.00, 'IT',   'Python, Excel, Power BI',      'Analyze business data and create dashboards.',             'Hyderabad',  DATE_ADD(CURDATE(), INTERVAL 25 DAY)),
(2, 'Systems Engineer',           8.00, 6.50, 'All',  'Java, OOPS, SQL',              'System design and development for enterprise clients.',    'Pune',       DATE_ADD(CURDATE(), INTERVAL 45 DAY)),
(3, 'SDE-1',                     22.00, 8.50, 'CSE',  'DSA, Java/C++, System Design', 'Work on world-scale distributed systems at Amazon.',       'Hyderabad',  DATE_ADD(CURDATE(), INTERVAL 20 DAY)),
(4, 'Associate Consultant',       7.50, 6.00, 'All',  'Communication, Aptitude',      'Consulting and IT project management.',                    'Chennai',    DATE_ADD(CURDATE(), INTERVAL 60 DAY)),
(5, 'Embedded Engineer',          9.00, 7.00, 'ECE',  'C, RTOS, Embedded C, UART',   'Design firmware for industrial automation systems.',       'Noida',      DATE_ADD(CURDATE(), INTERVAL 35 DAY)),
(1, 'Machine Learning Engineer', 18.00, 8.00, 'CSE',  'Python, TensorFlow, sklearn',  'Develop ML models for product recommendation engines.',   'Bangalore',  DATE_ADD(CURDATE(), INTERVAL 15 DAY)),
(3, 'Cloud Support Engineer',    15.00, 7.50, 'IT',   'AWS, Linux, Networking',       'Provide cloud infrastructure support and automation.',    'Mumbai',     DATE_ADD(CURDATE(), INTERVAL 40 DAY));

-- ── Applications  ─────────────────────────────────────────
INSERT INTO applications (student_id,job_id,status) VALUES
(1, 1, 'Selected'),
(4, 7, 'Shortlisted'),
(6, 1, 'Applied'),
(2, 2, 'Selected'),
(7, 2, 'Rejected'),
(3, 6, 'Shortlisted'),
(8, 6, 'Applied'),
(4, 4, 'Applied'),
(1, 7, 'Shortlisted'),
(9, 3, 'Applied'),
(5, 5, 'Applied'),
(10, 5, 'Applied');
