from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']

        cursor.execute(
            "SELECT * FROM students WHERE roll_no=?",
            (roll,)
        )

        student = cursor.fetchone()

        if student:
            conn.close()
            return redirect('/?message=duplicate_roll')

        cursor.execute(
            "INSERT INTO students(name, roll_no) VALUES (?, ?)",
            (name, roll)
        )

        conn.commit()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    today = str(date.today())

    cursor.execute(
        "SELECT COUNT(*) FROM attendance WHERE date=?",
        (today,)
    )

    present_today = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'index.html',
        students=students,
        total_students=total_students,
        present_today=present_today,
        message=request.args.get('message')
    )

@app.route('/mark/<int:id>')
def mark_attendance(id):

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    today = str(date.today())

    cursor.execute(
        "SELECT * FROM attendance WHERE student_id=? AND date=?",
        (id, today)
    )

    record = cursor.fetchone()

    if record:
        conn.close()
        return redirect('/?message=already')

    cursor.execute(
        "INSERT INTO attendance(student_id, date, status) VALUES (?, ?, ?)",
        (id, today, "Present")
    )

    conn.commit()
    conn.close()

    return redirect('/?message=success')

@app.route('/delete/<int:id>')
def delete_student(id):

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM attendance WHERE student_id=?",
        (id,)
    )

    cursor.execute(
        "DELETE FROM students WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/')

@app.route('/report')
def report():

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT students.name,
               students.roll_no,
               attendance.date,
               attendance.status
        FROM attendance
        JOIN students
        ON students.id = attendance.student_id
    """)

    records = cursor.fetchall()

    conn.close()

    return render_template('report.html', records=records)

@app.route('/percentage')
def percentage():

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, roll_no FROM students")
    students = cursor.fetchall()

    result = []

    cursor.execute("SELECT COUNT(DISTINCT date) FROM attendance")
    total_classes = cursor.fetchone()[0]

    for student in students:

        cursor.execute(
    "SELECT COUNT(DISTINCT date) FROM attendance WHERE student_id=?",
    (student[0],)
)
        present = cursor.fetchone()[0]

        if total_classes == 0:
            percent = 0
        else:
            percent = round((present / total_classes) * 100, 2)

        result.append(
            (student[1], student[2], percent)
        )

    conn.close()

    return render_template(
        'percentage.html',
        result=result
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)