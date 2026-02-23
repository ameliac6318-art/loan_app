from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # Required for sessions

# ---------------------------
# Admin credentials
# ---------------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

# ---------------------------
# Initialize database
# ---------------------------
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS applications
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  email TEXT,
                  phone TEXT,
                  amount INTEGER,
                  income INTEGER,
                  employment TEXT,
                  purpose TEXT,
                  status TEXT DEFAULT 'Pending')''')
    conn.commit()
    conn.close()

init_db()

# ---------------------------
# Routes
# ---------------------------

# Home page
@app.route('/')
def home():
    return render_template("index.html")


# Loan application
@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        amount = request.form['amount']
        income = request.form['income']
        employment = request.form['employment']
        purpose = request.form['purpose']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''INSERT INTO applications
                     (name, email, phone, amount, income, employment, purpose)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (name, email, phone, amount, income, employment, purpose))
        conn.commit()
        conn.close()

        return redirect(url_for('success'))

    return render_template("apply.html")


# Success page
@app.route('/success')
def success():
    return render_template("success.html")


# ---------------------------
# Admin Login
# ---------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return "❌ Invalid credentials"

    return render_template("login.html")


# Admin dashboard (protected)
@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM applications")
    applications = c.fetchall()
    conn.close()

    return render_template("admin.html", applications=applications)


# Approve / Reject (protected)
@app.route('/update_status/<int:app_id>/<status>')
def update_status(app_id, status):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE applications SET status = ? WHERE id = ?", (status, app_id))
    conn.commit()
    conn.close()

    return redirect(url_for('admin'))


# Logout
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))


# ---------------------------
# Run App
# ---------------------------
if __name__ == '__main__':
   port = int(os.environ.get("port", 5000))
   app.run(host="0.0.0.0.", port=port)