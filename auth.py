# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
import mysql.connector

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Lalit@94",  # Change as needed
        database="disease_app",
        auth_plugin="mysql_native_password"
    )

# ===== REGISTER =====
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if password != confirm:
            flash("Passwords do not match.")
            return redirect(url_for('auth.register'))

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                        (name, email, hashed_pw, 'user'))
            conn.commit()
            flash("Registration successful! Please log in.")
            return redirect(url_for('auth.login'))
        except mysql.connector.IntegrityError:
            flash("Email already registered.")
        finally:
            cur.close()
            conn.close()

    return render_template('register.html')

# ===== LOGIN =====
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and bcrypt.check_password_hash(user['password'], password):
            # Store session data
            session['user'] = user['email']
            session['name'] = user['name']
            session['role'] = user['role']

            # Flash message
            flash(f"Welcome {user['name']}! You are logged in as {user['role'].capitalize()}.")

            # Redirect based on role
            if user['role'] == 'admin':
                return redirect(url_for('admin_panel'))  # Direct to Admin Panel
            else:
                return redirect(url_for('home'))  # Normal users go to Home
        else:
            flash("Invalid credentials.")
            return redirect(url_for('auth.login'))

    return render_template('login.html')

# ===== ADMIN LOGIN =====
@auth_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email = %s AND role = 'admin'", (email,))
        admin = cur.fetchone()
        cur.close()
        conn.close()

        if admin and bcrypt.check_password_hash(admin['password'], password):
            session['user'] = admin['email']
            session['name'] = admin['name']
            session['role'] = 'admin'
            flash("Welcome Admin!")
            return redirect(url_for('admin_panel'))
        else:
            flash("Invalid admin credentials.")
            return redirect(url_for('auth.admin_login'))

    return render_template('admin_login.html')


# ===== LOGOUT =====
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('auth.login'))
