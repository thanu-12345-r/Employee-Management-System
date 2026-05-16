from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret"

def get_db():
    return sqlite3.connect("employees.db")

def create_tables():
    con = get_db()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS employee (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        eid TEXT,
        ename TEXT,
        dept TEXT,
        salary TEXT,
        email TEXT,
        phone TEXT
    )
    """)

    con.commit()
    con.close()

create_tables()

# ---------------- HOME PAGE ----------------

@app.route('/')
def home():
    return render_template("login.html")

# ---------------- REGISTER ----------------

@app.route('/register', methods=["GET", "POST"])
def register():

    if request.method == "POST":

        uname = request.form["username"]
        pwd = request.form["password"]
        role = request.form["role"]

        con = get_db()
        cur = con.cursor()

        query = """
        INSERT INTO users(username, password, role)
        VALUES(?, ?, ?)
        """

        cur.execute(query, (uname, pwd, role))

        con.commit()
        con.close()

        flash("Registration Successful!", "success")

        return redirect("/login")

    return render_template("register.html")

# ---------------- LOGIN ----------------

@app.route('/login', methods=["GET", "POST"])
def login():

    if request.method == "POST":

        uname = request.form["username"]
        pwd = request.form["password"]

        con = get_db()
        cur = con.cursor()

        query = """
        SELECT * FROM users
        WHERE username=? AND password=?
        """

        cur.execute(query, (uname, pwd))

        user = cur.fetchone()

        con.close()

        if user:

            session["admin"] = uname

            flash("Login Successful!", "success")

            return redirect("/dashboard")

        else:

            flash("Invalid Username or Password", "danger")

            return redirect("/login")

    return render_template("login.html")

# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
def dashboard():

    if "admin" not in session:
        return redirect("/login")

    return render_template("dashboard.html")

# ---------------- ADD EMPLOYEE ----------------

@app.route('/add', methods=["GET", "POST"])
def add_employee():

    if "admin" not in session:
        return redirect("/login")

    if request.method == "POST":

        eid = request.form["eid"]
        ename = request.form["ename"]
        dept = request.form["dept"]
        salary = request.form["salary"]
        email = request.form["email"]
        phone = request.form["phone"]

        con = get_db()
        cur = con.cursor()

        query = """
        INSERT INTO employee(eid, ename, dept, salary, email, phone)
        VALUES(?, ?, ?, ?, ?, ?)
        """

        data = (eid, ename, dept, salary, email, phone)

        cur.execute(query, data)

        con.commit()
        con.close()

        flash("Employee Added Successfully!", "success")

        return redirect("/view")

    return render_template("add_employee.html")

# ---------------- VIEW EMPLOYEES ----------------

@app.route('/view')
def view_employee():

    if "admin" not in session:
        return redirect("/login")

    con = get_db()
    cur = con.cursor()

    query = "SELECT * FROM employee"

    cur.execute(query)

    employees = cur.fetchall()

    con.close()

    return render_template("view_employee.html", employees=employees)

# ---------------- EDIT EMPLOYEE ----------------

@app.route('/edit/<eid>')
def edit_employee(eid):

    if "admin" not in session:
        return redirect("/login")

    con = get_db()
    cur = con.cursor()

    query = "SELECT * FROM employee WHERE id=?"

    cur.execute(query, (eid,))

    emp = cur.fetchone()

    con.close()

    return render_template("edit_employee.html", emp=emp)

# ---------------- UPDATE EMPLOYEE ----------------

@app.route('/update', methods=["POST"])
def update_employee():

    if "admin" not in session:
        return redirect("/login")

    eid = request.form["eid"]
    ename = request.form["ename"]
    edept = request.form["edept"]
    esalary = request.form["esalary"]
    ephone = request.form["ephone"]

    con = get_db()
    cur = con.cursor()

    query = """
    UPDATE employee
    SET ename=?,
        dept=?,
        salary=?,
        phone=?
    WHERE id=?
    """

    data = (ename, edept, esalary, ephone, eid)

    try:
        cur.execute(query, data)
        con.commit()
    except Exception as e:
        return str(e)

    con.close()

    flash("Employee Updated Successfully!", "success")
    return redirect("/view")

# ---------------- DELETE EMPLOYEE ----------------

@app.route('/delete/<eid>')
def delete_employee(eid):

    if "admin" not in session:
        return redirect("/login")

    con = get_db()
    cur = con.cursor()

    query = "DELETE FROM employee WHERE id=?"

    cur.execute(query, (eid,))

    con.commit()
    con.close()

    flash("Employee Deleted Successfully!", "success")

    return redirect("/view")

# ---------------- ABOUT PAGE ----------------

@app.route('/about')
def about():
    return render_template("about.html")

# ---------------- SETTINGS PAGE ------------
@app.route('/settings')
def settings():

    if "admin" not in session:
        return redirect("/login")

    return render_template("settings.html")

# ---------------- FORGOT PASSWORD ----------------

@app.route('/forgot-password', methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        uname = request.form["username"]
        new_pwd = request.form["new_password"]
        confirm_pwd = request.form["confirm_password"]

        if new_pwd != confirm_pwd:
            flash("Passwords do not match!", "danger")
            return redirect("/forgot-password")

        con = get_db()
        cur = con.cursor()

        query = "SELECT * FROM users WHERE username=?"
        cur.execute(query, (uname,))
        user = cur.fetchone()

        if not user:
            con.close()
            flash("Username not found!", "danger")
            return redirect("/forgot-password")

        query = "UPDATE users SET password=? WHERE username=?"
        cur.execute(query, (new_pwd, uname))
        con.commit()
        con.close()

        flash("Password reset successful. Please login with your new password.", "success")
        return redirect("/login")

    return render_template("forgot_password.html")

# ---------------- CONTACT PAGE ----------------

@app.route('/contact')
def contact():
    return render_template("contact.html")

# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():

    session.clear()

    flash("Logged Out Successfully!", "info")

    return redirect("/login")

# ---------------- RUN SERVER ----------------

import os

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

