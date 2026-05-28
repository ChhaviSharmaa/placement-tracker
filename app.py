from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "placement_secret_key"

# ---------------- DATABASE CONNECTION ----------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="placement_management"
)

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

        print("DEBUG USER:", user)

        if user:
            session['user'] = user[1]  # username
            return redirect('/')
        else:
            return "Invalid Credentials"

    return render_template('login.html')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


# ---------------- DASHBOARD ----------------
@app.route('/')
def home():

    if 'user' not in session:
        return redirect('/login')

    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM students WHERE status='Placed'")
    placed_students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM students WHERE status='Not Placed'")
    not_placed_students = cur.fetchone()[0]

    placement_rate = round((placed_students / total_students) * 100, 2) if total_students > 0 else 0

    return render_template(
        'index.html',
        total=total_students,
        placed=placed_students,
        not_placed=not_placed_students,
        rate=placement_rate
    )


# ---------------- STUDENTS ----------------
@app.route('/students')
def students():

    if 'user' not in session:
        return redirect('/login')

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

    if request.method == 'POST':
        name = request.form['name']
        branch = request.form['branch']
        company = request.form['company']
        status = request.form['status']

        cur = conn.cursor()

        cur.execute(
            "INSERT INTO students (name, branch, company, status) VALUES (%s, %s, %s, %s)",
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

    cur = conn.cursor()

    cur.execute("DELETE FROM students WHERE id = %s", (id,))
    conn.commit()

    return redirect('/students')


# ---------------- EDIT STUDENT ----------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):

    if 'user' not in session:
        return redirect('/login')

    cur = conn.cursor()

    if request.method == 'POST':

        name = request.form['name']
        branch = request.form['branch']
        company = request.form['company']
        status = request.form['status']

        cur.execute("""
            UPDATE students
            SET name=%s, branch=%s, company=%s, status=%s
            WHERE id=%s
        """, (name, branch, company, status, id))

        conn.commit()

        return redirect('/students')

    cur.execute("SELECT * FROM students WHERE id=%s", (id,))
    student = cur.fetchone()

    return render_template('edit_student.html', student=student)


# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(debug=True)