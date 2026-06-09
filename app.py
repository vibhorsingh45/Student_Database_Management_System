from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_this'

# ── SQLite DB config ───────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")


# ── Helper: DB Connection ───────────────────────────────────────────
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # dict-like access
    return conn


# ── Helper: Password Hashing ────────────────────────────────────────
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ── Home ─────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('register'))


# ── Register ─────────────────────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        roll = request.form['roll']
        city = request.form['city']
        dob = request.form['dob']
        gender = request.form['gender']
        email = request.form['email']
        password = hash_password(request.form['password'])
        course = request.form.get('course', 'General')

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Check duplicate
            cur.execute("SELECT id FROM students WHERE roll=? OR email=?", (roll, email))
            existing = cur.fetchone()

            if existing:
                error = "A student with this Roll No. or Email already exists."
            else:
                cur.execute("""
                    INSERT INTO students (name, age, roll, city, dob, gender, email, password, course)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, age, roll, city, dob, gender, email, password, course))

                conn.commit()
                conn.close()
                return redirect(url_for('login'))

            conn.close()

        except Exception as e:
            error = str(e)

    return render_template('register.html', error=error)


# ── Login ────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        roll = request.form['roll']
        password = hash_password(request.form['password'])

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("SELECT * FROM students WHERE roll=? AND password=?", (roll, password))
            student = cur.fetchone()
            conn.close()

            if student:
                session['student_id'] = student['id']
                session['student_name'] = student['name']
                return redirect(url_for('dashboard'))
            else:
                error = "Invalid Roll No. or Password."

        except Exception as e:
            error = str(e)

    return render_template('login.html', error=error)


# ── Logout ───────────────────────────────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ── Dashboard ───────────────────────────────────────────────────────
@app.route('/dashboard')
def dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM students WHERE id=?", (session['student_id'],))
    student = cur.fetchone()

    cur.execute("""
        SELECT subject,
               COUNT(*) as total,
               SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) as present
        FROM attendance
        WHERE student_id=?
        GROUP BY subject
    """, (session['student_id'],))
    attendance = cur.fetchall()

    cur.execute("""
        SELECT * FROM results
        WHERE student_id=?
        ORDER BY exam_date DESC
        LIMIT 5
    """, (session['student_id'],))
    results = cur.fetchall()

    conn.close()

    return render_template('dashboard.html',
                           student=student,
                           attendance=attendance,
                           results=results)


# ── Profile ──────────────────────────────────────────────────────────
@app.route('/profile')
def profile():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM students WHERE id=?", (session['student_id'],))
    student = cur.fetchone()

    conn.close()
    return render_template('profile.html', student=student)


# ── Results ──────────────────────────────────────────────────────────
@app.route('/results')
def results():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM results
        WHERE student_id=?
        ORDER BY exam_date DESC
    """, (session['student_id'],))

    results = cur.fetchall()
    conn.close()

    return render_template('results.html', results=results)


# ── Attendance ───────────────────────────────────────────────────────
@app.route('/attendance')
def attendance():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT subject,
               COUNT(*) as total,
               SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) as present
        FROM attendance
        WHERE student_id=?
        GROUP BY subject
    """, (session['student_id'],))
    data = cur.fetchall()

    cur.execute("""
        SELECT * FROM attendance
        WHERE student_id=?
        ORDER BY date DESC
    """, (session['student_id'],))
    records = cur.fetchall()

    conn.close()

    return render_template('attendance.html', data=data, records=records)


# ── Study Material ───────────────────────────────────────────────────
@app.route('/study-material')
def study_material():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM study_materials ORDER BY subject, title")
    materials = cur.fetchall()

    conn.close()
    return render_template('study_material.html', materials=materials)


# ── Store ────────────────────────────────────────────────────────────
@app.route('/store')
def store():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM store_items WHERE stock > 0")
    items = cur.fetchall()

    conn.close()
    return render_template('store.html', items=items)


# ── Suggestions ──────────────────────────────────────────────────────
@app.route('/suggestions')
def suggestions():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM suggestions
        WHERE student_id=?
        ORDER BY created_at DESC
    """, (session['student_id'],))

    sugg = cur.fetchall()
    conn.close()

    return render_template('suggestions.html', suggestions=sugg)


# ── Progress ─────────────────────────────────────────────────────────
@app.route('/progress')
def progress():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT subject,
               AVG(marks_obtained) as avg_marks,
               MAX(marks_obtained) as best,
               MIN(marks_obtained) as lowest,
               COUNT(*) as exams
        FROM results
        WHERE student_id=?
        GROUP BY subject
    """, (session['student_id'],))

    progress_data = cur.fetchall()
    conn.close()

    return render_template('progress.html', progress_data=progress_data)


# ── API: Progress Data ───────────────────────────────────────────────
@app.route('/api/progress-data')
def progress_data_api():
    if 'student_id' not in session:
        return jsonify([])

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT subject, marks_obtained, exam_date
        FROM results
        WHERE student_id=?
        ORDER BY exam_date
    """, (session['student_id'],))

    rows = cur.fetchall()
    conn.close()

    return jsonify([
        {
            'subject': r['subject'],
            'marks': float(r['marks_obtained']),
            'date': str(r['exam_date'])
        }
        for r in rows
    ])


# ── Run App ──────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, port=5001)