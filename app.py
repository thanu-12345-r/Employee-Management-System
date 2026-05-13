from flask import Flask, render_template, request, redirect, session, flash
import pymysql

app = Flask(__name__)
app.secret_key = "secret"

# ---------------- DATABASE CONNECTION ----------------

def get_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="mysql",     # XAMPP default password is empty
        database="company",
        cursorclass=pymysql.cursors.Cursor
    )

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
        VALUES(%s, %s, %s)
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
        WHERE username=%s AND password=%s
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
        edept = request.form["edept"]
        esalary = request.form["esalary"]
        ephone = request.form["ephone"]

        con = get_db()
        cur = con.cursor()

        query = """
        INSERT INTO employee(eid, ename, edept, esalary, ephone)
        VALUES(%s, %s, %s, %s, %s)
        """

        data = (eid, ename, edept, esalary, ephone)

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

    query = "SELECT * FROM employee WHERE eid=%s"

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
    SET ename=%s,
        edept=%s,
        esalary=%s,
        ephone=%s
    WHERE eid=%s
    """

    data = (ename, edept, esalary, ephone, eid)

    cur.execute(query, data)

    con.commit()
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

    query = "DELETE FROM employee WHERE eid=%s"

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

        query = "SELECT * FROM users WHERE username=%s"
        cur.execute(query, (uname,))
        user = cur.fetchone()

        if not user:
            con.close()
            flash("Username not found!", "danger")
            return redirect("/forgot-password")

        query = "UPDATE users SET password=%s WHERE username=%s"
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

if __name__ == "__main__":
    app.run(debug=True)

    