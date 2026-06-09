-- Run this ONCE to set up / upgrade your database
-- mysql -u root -p studentdb2 < setup_db.sql

USE studentdb2;

-- ── Students table (adds new columns to existing) ───────────────────────────
CREATE TABLE IF NOT EXISTS students (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    age        INT,
    roll       VARCHAR(20) UNIQUE NOT NULL,
    city       VARCHAR(50),
    dob        DATE,
    gender     VARCHAR(10),
    email      VARCHAR(100) UNIQUE,
    password   VARCHAR(64),
    course     VARCHAR(100) DEFAULT 'General',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add columns if you already have an older students table:
-- ALTER TABLE students ADD COLUMN email VARCHAR(100) UNIQUE;
-- ALTER TABLE students ADD COLUMN password VARCHAR(64);
-- ALTER TABLE students ADD COLUMN course VARCHAR(100) DEFAULT 'General';

-- ── Attendance ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS attendance (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject    VARCHAR(100),
    date       DATE,
    status     ENUM('Present','Absent') DEFAULT 'Present',
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- ── Results ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS results (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    student_id     INT NOT NULL,
    subject        VARCHAR(100),
    exam_name      VARCHAR(100),
    marks_obtained DECIMAL(5,2),
    total_marks    DECIMAL(5,2) DEFAULT 100,
    exam_date      DATE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- ── Study Materials ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS study_materials (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    subject     VARCHAR(100),
    title       VARCHAR(200),
    description TEXT,
    file_url    VARCHAR(500),
    type        ENUM('PDF','Video','Notes','Quiz') DEFAULT 'Notes',
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Store Items ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS store_items (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(200),
    description TEXT,
    price       DECIMAL(8,2),
    stock       INT DEFAULT 0,
    category    VARCHAR(100),
    image_url   VARCHAR(500)
);

-- ── Suggestions ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS suggestions (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    student_id  INT NOT NULL,
    title       VARCHAR(200),
    message     TEXT,
    type        ENUM('Academic','Career','Study Tips','General') DEFAULT 'General',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- ── Sample data ───────────────────────────────────────────────────────────────
INSERT IGNORE INTO study_materials (subject, title, description, file_url, type) VALUES
('Mathematics', 'Calculus Chapter 1', 'Introduction to limits and derivatives', '/static/materials/calc1.pdf', 'PDF'),
('Physics',     'Mechanics Notes',    'Newton laws and motion',                 '/static/materials/mech.pdf', 'Notes'),
('Chemistry',   'Organic Chemistry',  'Carbon compounds and reactions',          'https://youtu.be/example',  'Video'),
('Computer Sc', 'Python Basics',      'Variables, loops, functions',             '/static/materials/py.pdf',  'PDF');

INSERT IGNORE INTO store_items (name, description, price, stock, category) VALUES
('Scientific Calculator', 'Casio FX-991ES Plus', 899.00, 50, 'Electronics'),
('Physics Textbook',      'NCERT Class 12 Physics Vol 1 & 2', 350.00, 30, 'Books'),
('Geometry Box',          'Full set with compass, protractor', 120.00, 100, 'Stationery'),
('Graph Notebook',        '200-page graph paper notebook', 80.00, 200, 'Stationery'),
('Pen Set (12)',          'Blue, black, red ink pens', 60.00, 150, 'Stationery'),
('USB Flash Drive 32GB',  'For storing notes and projects', 450.00, 75, 'Electronics');
