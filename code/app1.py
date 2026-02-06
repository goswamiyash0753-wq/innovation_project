from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 1. Users Table (Module 1)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    # 2. Exams Table (Module 2)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            duration INTEGER, -- In minutes
            total_marks INTEGER,
            tab_switch_limit INTEGER DEFAULT 3,
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        )
    ''')
    
    # 3. Questions Table (Module 3)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER,
            question_text TEXT NOT NULL,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_option TEXT,
            FOREIGN KEY (exam_id) REFERENCES exams (id)
        )
    ''')
    
    # 4. Student Answers Table (Module 3)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            exam_id INTEGER,
            question_id INTEGER,
            selected_option TEXT,
            FOREIGN KEY (student_id) REFERENCES users (id),
            FOREIGN KEY (exam_id) REFERENCES exams (id),
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )
    ''')
    
    # 5. Exam Results Table (Module 3 Improvement)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exam_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            exam_id INTEGER,
            score INTEGER,
            total_marks INTEGER,
            submission_time TEXT,
            FOREIGN KEY (student_id) REFERENCES users (id),
            FOREIGN KEY (exam_id) REFERENCES exams (id)
        )
    ''')
    
    # 6. Violations Table (Module 4)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            exam_id INTEGER,
            violation_count INTEGER DEFAULT 0,
            last_violation_time TEXT,
            FOREIGN KEY (student_id) REFERENCES users (id),
            FOREIGN KEY (exam_id) REFERENCES exams (id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# --- HELPER FUNCTIONS ---
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- ROUTES ---

@app.route('/')
def index():
    return redirect(url_for('login'))

# 1. User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)', 
                           (name, email, hashed_password, role))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists.', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html')

# 2. User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            
            if user['role'] == 'Student':
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('teacher_dashboard'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html')

# 3. Student Dashboard
@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session['user_role'] != 'Student':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    exams = conn.execute('SELECT * FROM exams').fetchall()
    conn.close()
    return render_template('student_dashboard.html', name=session['user_name'], exams=exams)

# 4. Teacher Dashboard
@app.route('/teacher/dashboard')
def teacher_dashboard():
    if 'user_id' not in session or session['user_role'] != 'Teacher':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    exams = conn.execute('SELECT * FROM exams WHERE teacher_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('teacher_dashboard.html', name=session['user_name'], exams=exams)

# --- MODULE 2: EXAM CREATION ---
@app.route('/teacher/create_exam', methods=['GET', 'POST'])
def create_exam():
    if 'user_id' not in session or session['user_role'] != 'Teacher':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        duration = request.form['duration']
        total_marks = request.form['total_marks']
        limit = request.form['tab_switch_limit']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO exams (teacher_id, title, description, duration, total_marks, tab_switch_limit) VALUES (?, ?, ?, ?, ?, ?)',
                       (session['user_id'], title, description, duration, total_marks, limit))
        conn.commit()
        conn.close()
        flash('Exam created successfully!', 'success')
        return redirect(url_for('teacher_dashboard'))
    
    return render_template('create_exam.html')

# --- IMPROVEMENT: TEACHER ADD QUESTIONS ---
@app.route('/teacher/exam/<int:exam_id>/add_questions', methods=['GET', 'POST'])
def add_questions(exam_id):
    if 'user_id' not in session or session['user_role'] != 'Teacher':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    exam = conn.execute('SELECT * FROM exams WHERE id = ? AND teacher_id = ?', (exam_id, session['user_id'])).fetchone()
    
    if not exam:
        conn.close()
        flash('Exam not found or unauthorized.', 'danger')
        return redirect(url_for('teacher_dashboard'))
    
    if request.method == 'POST':
        question_text = request.form['question_text']
        a = request.form['option_a']
        b = request.form['option_b']
        c = request.form['option_c']
        d = request.form['option_d']
        correct = request.form['correct_option']
        
        conn.execute('INSERT INTO questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_option) VALUES (?, ?, ?, ?, ?, ?, ?)',
                       (exam_id, question_text, a, b, c, d, correct))
        conn.commit()
        flash('Question added!', 'success')
    
    questions = conn.execute('SELECT * FROM questions WHERE exam_id = ?', (exam_id,)).fetchall()
    conn.close()
    return render_template('add_questions.html', exam=exam, questions=questions)

# --- MODULE 3 & 4: EXAM ATTEMPT & ANTI-CHEAT ---
@app.route('/student/exam/<int:exam_id>/attempt', methods=['GET', 'POST'])
def attempt_exam(exam_id):
    if 'user_id' not in session or session['user_role'] != 'Student':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Check if already attempted
    previous_result = conn.execute('SELECT * FROM exam_results WHERE student_id = ? AND exam_id = ?', (session['user_id'], exam_id)).fetchone()
    if previous_result:
        conn.close()
        flash('You have already attempted this exam.', 'info')
        return redirect(url_for('student_dashboard'))
    
    exam = conn.execute('SELECT * FROM exams WHERE id = ?', (exam_id,)).fetchone()
    questions = conn.execute('SELECT * FROM questions WHERE exam_id = ?', (exam_id,)).fetchall()
    
    if request.method == 'POST':
        # Grade the exam
        score = 0
        for q in questions:
            selected = request.form.get(f'q_{q["id"]}')
            # Save individual answer
            conn.execute('INSERT INTO student_answers (student_id, exam_id, question_id, selected_option) VALUES (?, ?, ?, ?)',
                           (session['user_id'], exam_id, q['id'], selected))
            if selected == q['correct_option']:
                score += (exam['total_marks'] // len(questions)) if len(questions) > 0 else 0
        
        # Save final result
        conn.execute('INSERT INTO exam_results (student_id, exam_id, score, total_marks, submission_time) VALUES (?, ?, ?, ?, ?)',
                       (session['user_id'], exam_id, score, exam['total_marks'], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        return redirect(url_for('exam_result', exam_id=exam_id))
    
    conn.close()
    return render_template('attempt_exam.html', exam=exam, questions=questions)

@app.route('/student/exam/<int:exam_id>/result')
def exam_result(exam_id):
    if 'user_id' not in session or session['user_role'] != 'Student':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    result = conn.execute('SELECT * FROM exam_results WHERE student_id = ? AND exam_id = ?', (session['user_id'], exam_id)).fetchone()
    exam = conn.execute('SELECT * FROM exams WHERE id = ?', (exam_id,)).fetchone()
    conn.close()
    
    if not result:
        return redirect(url_for('student_dashboard'))
    
    return render_template('exam_result.html', result=result, exam=exam)

# --- MODULE 4: VIOLATION LOGGING ---
@app.route('/api/violation', methods=['POST'])
def log_violation():
    data = request.json
    student_id = session.get('user_id')
    exam_id = data.get('exam_id')
    
    if not student_id or not exam_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    v = conn.execute('SELECT * FROM violations WHERE student_id = ? AND exam_id = ?', (student_id, exam_id)).fetchone()
    
    if v:
        count = v['violation_count'] + 1
        conn.execute('UPDATE violations SET violation_count = ?, last_violation_time = ? WHERE id = ?',
                       (count, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), v['id']))
    else:
        count = 1
        conn.execute('INSERT INTO violations (student_id, exam_id, violation_count, last_violation_time) VALUES (?, ?, ?, ?)',
                       (student_id, exam_id, 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    conn.close()
    return jsonify({'count': count})

# --- IMPROVEMENT: STUDENT EXAM HISTORY ---
@app.route('/student/history')
def student_history():
    if 'user_id' not in session or session['user_role'] != 'Student':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    history = conn.execute('''
        SELECT r.*, e.title 
        FROM exam_results r 
        JOIN exams e ON r.exam_id = e.id 
        WHERE r.student_id = ?
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('student_history.html', history=history)

# 5. Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    