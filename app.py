from flask import Flask, render_template, request, redirect, session
import mysql.connector
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


# ---------------- GEMINI CLIENT ----------------
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# ---------------- DATABASE CONNECTION ----------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.getenv("DB_PASSWORD"),
    database="placement_management"
)


# ---------------- ADMIN CHECK ----------------
def is_admin():
    return session.get('role') == 'admin'


# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username'].strip()
        password = request.form['password'].strip()

        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )

        user = cur.fetchone()

        if user:
            session['user'] = user[1]
            session['role'] = user[3]
            session['student_id'] = user[4]

            if user[3] == 'student':
                return redirect('/student-dashboard')

            return redirect('/')

        else:
            return "Invalid Credentials"

    return render_template('login.html')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():

    session.pop('user', None)
    session.pop('role', None)
    session.pop('student_id', None)

    return redirect('/login')


# ---------------- ADMIN DASHBOARD ----------------
@app.route('/')
def home():

    if 'user' not in session:
        return redirect('/login')

    if not is_admin():
        return "Access Denied"

    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM students WHERE status='Placed'")
    placed_students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM students WHERE status='Not Placed'")
    not_placed_students = cur.fetchone()[0]

    placement_rate = round(
        (placed_students / total_students) * 100, 2
    ) if total_students > 0 else 0

    return render_template(
        'index.html',
        total=total_students,
        placed=placed_students,
        not_placed=not_placed_students,
        rate=placement_rate
    )


# ---------------- STUDENT DASHBOARD ----------------
@app.route('/student-dashboard')
def student_dashboard():

    if 'user' not in session:
        return redirect('/login')

    if session.get('role') != 'student':
        return "Access Denied"

    student_id = session.get('student_id')

    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM students WHERE id=%s",
        (student_id,)
    )

    student = cur.fetchone()

    if not student:
        return "Student record not found"

    return render_template(
        'student_dashboard.html',
        student=student
    )


# ---------------- AI JOB MATCH ----------------
@app.route('/ai-match', methods=['GET', 'POST'])
def ai_match():

    if 'user' not in session:
        return redirect('/login')

    if session.get('role') != 'student':
        return "Access Denied"

    if request.method == 'POST':

        resume = request.form['resume'].strip()
        job_description = request.form['job_description'].strip()

        # ---------------- AI PROMPT ----------------
        prompt = f"""
You are a recruitment assistant.

Analyze the student's resume against the job description.

Return the following:

1. Match percentage
2. Matched skills
3. Missing skills
4. Improvement suggestions

Keep the answer clear, practical and easy to understand.

STUDENT RESUME:
{resume}

JOB DESCRIPTION:
{job_description}
"""

        # ---------------- CALL GEMINI ----------------
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        result = response.text

        return render_template(
            'ai_result.html',
            result=result
        )

    return render_template('ai_match.html')


# ---------------- STUDENTS ----------------
@app.route('/students')
def students():

    if 'user' not in session:
        return redirect('/login')

    if not is_admin():
        return "Access Denied"

    search = request.args.get('search')
    status_filter = request.args.get('status')

    query = "SELECT * FROM students WHERE 1=1"
    values = []

    if search:
        query += " AND name LIKE %s"
        values.append("%" + search + "%")

    if status_filter and status_filter != "All":
        query += " AND status=%s"
        values.append(status_filter)

    cur = conn.cursor()
    cur.execute(query, values)

    students_data = cur.fetchall()

    return render_template(
        'students.html',
        students=students_data,
        search=search,
        status_filter=status_filter
    )


# ---------------- ADD STUDENT ----------------
@app.route('/add', methods=['GET', 'POST'])
def add_student():

    if 'user' not in session:
        return redirect('/login')

    if not is_admin():
        return "Access Denied"

    if request.method == 'POST':

        name = request.form['name']
        branch = request.form['branch']
        company = request.form['company']
        status = request.form['status']

        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO students
            (name, branch, company, status)
            VALUES (%s, %s, %s, %s)
            """,
            (name, branch, company, status)
        )

        conn.commit()

        return redirect('/students')

    return render_template('add_student.html')


# ---------------- DELETE STUDENT ----------------
@app.route('/delete/<int:id>')
def delete_student(id):

    if 'user' not in session:
        return redirect('/login')

    if not is_admin():
        return "Access Denied"

    cur = conn.cursor()

    cur.execute(
        "DELETE FROM students WHERE id = %s",
        (id,)
    )

    conn.commit()

    return redirect('/students')


# ---------------- EDIT STUDENT ----------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):

    if 'user' not in session:
        return redirect('/login')

    if not is_admin():
        return "Access Denied"

    cur = conn.cursor()

    if request.method == 'POST':

        name = request.form['name']
        branch = request.form['branch']
        company = request.form['company']
        status = request.form['status']

        cur.execute(
            """
            UPDATE students
            SET name=%s,
                branch=%s,
                company=%s,
                status=%s
            WHERE id=%s
            """,
            (name, branch, company, status, id)
        )

        conn.commit()

        return redirect('/students')

    cur.execute(
        "SELECT * FROM students WHERE id=%s",
        (id,)
    )

    student = cur.fetchone()

    return render_template(
        'edit_student.html',
        student=student
    )


# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(debug=True)