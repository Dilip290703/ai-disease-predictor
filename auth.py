# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
import mysql.connector

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="MITDc@29072003",  # Change as needed
        database="disease_app"
    )

# ===== REGISTER =====
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
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
            session['user'] = user['email']
            session['name'] = user['name']
            session['role'] = user['role']
            flash("Login successful!")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials.")
            return redirect(url_for('auth.login'))

    return render_template('login.html')

# ===== LOGOUT =====
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('auth.login'))
