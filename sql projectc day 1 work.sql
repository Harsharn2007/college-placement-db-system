DROP DATABASE IF EXISTS cpds_main;
CREATE DATABASE cpds_main;
USE cpds_main;
CREATE TABLE admin (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    username   VARCHAR(100) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    email      VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE students (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(150)  NOT NULL,
    email      VARCHAR(150)  NOT NULL UNIQUE,
    password   VARCHAR(255)  NOT NULL,
    branch     VARCHAR(100)  NOT NULL,
    cgpa       DECIMAL(3,2)  CHECK (cgpa BETWEEN 0 AND 10),
    skills     TEXT,
    phone      VARCHAR(15),
    resume     VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE companies (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(200) NOT NULL,
    email      VARCHAR(150) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    industry   VARCHAR(100),
    website    VARCHAR(255),
    about      TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE jobs (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    company_id       INT NOT NULL,
    role             VARCHAR(200) NOT NULL,
    package          DECIMAL(8,2),
    min_cgpa         DECIMAL(3,2),
    eligible_branch  VARCHAR(100) DEFAULT 'All',
    skills           TEXT,
    description      TEXT,
    location         VARCHAR(200),
    deadline         DATE NOT NULL,
    posted_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_job_company
        FOREIGN KEY (company_id)
        REFERENCES companies(id)
        ON DELETE CASCADE
);
CREATE TABLE applications (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    student_id  INT NOT NULL,
    job_id      INT NOT NULL,
    status      ENUM('Applied','Shortlisted','Rejected','Selected') DEFAULT 'Applied',
    applied_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY unique_application (student_id, job_id),

    CONSTRAINT fk_app_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_app_job
        FOREIGN KEY (job_id)
        REFERENCES jobs(id)
        ON DELETE CASCADE
);
CREATE INDEX idx_jobs_company    ON jobs(company_id);
CREATE INDEX idx_apps_student    ON applications(student_id);
CREATE INDEX idx_apps_job        ON applications(job_id);
CREATE INDEX idx_apps_status     ON applications(status);
CREATE INDEX idx_students_branch ON students(branch);
SHOW TABLES;
INSERT INTO admin (username, password, email) VALUES
('placement_admin', 'changethislater', 'placementadmin@cpds.edu');
INSERT INTO students (name, email, password, branch, cgpa, skills, phone) VALUES
('Rahul Verma',      'rahul.v@cpds.edu',    'samplepass', 'CSE', 8.75, 'Python, Django, MySQL, React',        '9811001101'),
('Nisha Sharma',     'nisha.s@cpds.edu',    'samplepass', 'IT',  8.20, 'Java, Spring Boot, AWS',              '9811001102'),
('Amit Chauhan',     'amit.c@cpds.edu',     'samplepass', 'ECE', 7.90, 'C++, Embedded Systems, VLSI',         '9811001103'),
('Pooja Agarwal',    'pooja.a@cpds.edu',    'samplepass', 'CSE', 9.10, 'Machine Learning, Python, TensorFlow','9811001104'),
('Suresh Yadav',     'suresh.y@cpds.edu',   'samplepass', 'ME',  7.50, 'AutoCAD, MATLAB, Solidworks',         '9811001105'),
('Kavya Reddy',      'kavya.r@cpds.edu',    'samplepass', 'CSE', 8.60, 'JavaScript, Node.js, MongoDB',        '9811001106'),
('Manish Tiwari',    'manish.t@cpds.edu',   'samplepass', 'IT',  7.80, 'PHP, Laravel, MySQL',                 '9811001107'),
('Deepika Nair',     'deepika.n@cpds.edu',  'samplepass', 'ECE', 8.40, 'Signal Processing, MATLAB, Python',   '9811001108'),
('Harsh Malhotra',   'harsh.m@cpds.edu',    'samplepass', 'CSE', 6.80, 'HTML, CSS, JavaScript',               '9811001109'),
('Tanvi Desai',      'tanvi.d@cpds.edu',    'samplepass', 'CE',  7.20, 'AutoCAD, Staad Pro, ETABS',           '9811001110');
INSERT INTO companies (name, email, password, industry, website, about) VALUES
('Nexora Technologies',     'hr@nexora.cpds.org',      'samplepass', 'Information Technology', 'https://nexora.example.com',    'Leading software solutions provider with 5000+ employees.'),
('Brightwave Systems',      'campus@brightwave.cpds.org', 'samplepass', 'IT Services',         'https://brightwave.example.com','Global IT services and digital consulting firm.'),
('Cloudpeak Inc',           'talent@cloudpeak.cpds.org','samplepass', 'E-Commerce / Cloud',    'https://cloudpeak.example.com', 'Cloud infrastructure and e-commerce platform provider.'),
('Zenith Infotech',         'recruit@zenith.cpds.org', 'samplepass', 'IT Consulting',          'https://zenith.example.com',    'Multinational IT consulting and business solutions.'),
('Stellartech Engineering', 'careers@stellar.cpds.org','samplepass', 'Engineering',            'https://stellar.example.com',   'Industrial automation and embedded systems company.');
INSERT INTO jobs (company_id, role, package, min_cgpa, eligible_branch, skills, description, location, deadline) VALUES
(1, 'Software Engineer',          12.00, 7.50, 'CSE', 'Python, Django, SQL',          'Build and maintain scalable web applications.',         'Bangalore',  DATE_ADD(CURDATE(), INTERVAL 30 DAY)),
(1, 'Data Analyst',               10.00, 7.00, 'IT',  'Python, Excel, Power BI',      'Analyze business data and create dashboards.',          'Hyderabad',  DATE_ADD(CURDATE(), INTERVAL 25 DAY)),
(2, 'Systems Engineer',            8.00, 6.50, 'All', 'Java, OOPS, SQL',              'System design and development for enterprise clients.', 'Pune',       DATE_ADD(CURDATE(), INTERVAL 45 DAY)),
(3, 'Cloud Developer',            22.00, 8.50, 'CSE', 'AWS, Docker, Python',          'Work on large scale distributed cloud systems.',        'Hyderabad',  DATE_ADD(CURDATE(), INTERVAL 20 DAY)),
(4, 'Associate Consultant',        7.50, 6.00, 'All', 'Communication, Aptitude',      'IT project management and client consulting.',          'Chennai',    DATE_ADD(CURDATE(), INTERVAL 60 DAY)),
(5, 'Embedded Engineer',           9.00, 7.00, 'ECE', 'C, RTOS, Embedded C, UART',   'Design firmware for industrial automation systems.',    'Noida',      DATE_ADD(CURDATE(), INTERVAL 35 DAY)),
(1, 'Machine Learning Engineer',  18.00, 8.00, 'CSE', 'Python, TensorFlow, sklearn',  'Develop ML models for product recommendation.',        'Bangalore',  DATE_ADD(CURDATE(), INTERVAL 15 DAY)),
(3, 'Cloud Support Engineer',     15.00, 7.50, 'IT',  'AWS, Linux, Networking',       'Provide cloud infrastructure support and automation.', 'Mumbai',     DATE_ADD(CURDATE(), INTERVAL 40 DAY));
INSERT INTO applications (student_id, job_id, status) VALUES
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
-- Check all tables exist
SHOW TABLES;

-- Check row counts
SELECT COUNT(*) AS total_students    FROM students;
SELECT COUNT(*) AS total_companies   FROM companies;
SELECT COUNT(*) AS total_jobs        FROM jobs;
SELECT COUNT(*) AS total_applications FROM applications;
SELECT COUNT(*) AS total_admins      FROM admin;

-- Check foreign keys are working
SELECT s.name, j.role, a.status
FROM applications a
JOIN students s ON a.student_id = s.id
JOIN jobs j     ON a.job_id     = j.id;

-- Check job filtering logic works
SELECT j.role, j.package, j.min_cgpa, j.eligible_branch
FROM jobs j
WHERE j.min_cgpa <= 8.75
AND j.deadline >= CURDATE()
AND (j.eligible_branch = 'CSE' OR j.eligible_branch = 'All');
