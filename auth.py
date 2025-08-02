from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from flask_bcrypt import Bcrypt

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

# Database connection helper
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="MITDc@29072003",  # Update if needed
        database="disease_app"
    )

# Register Route
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                        (name, email, password, 'user'))  # default role
            conn.commit()
            flash("Registered successfully. Please log in.")
            return redirect(url_for('auth.login'))
        except mysql.connector.errors.IntegrityError:
            flash("User with this email already exists.")
        finally:
            cur.close()
            conn.close()
    return render_template('register.html')


# Login Route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_input = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)  # Fetch rows as dicts
        cur.execute("SELECT id, name, email, password, role FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and bcrypt.check_password_hash(user['password'], password_input):
            session['user'] = user['email']
            session['name'] = user['name']
            session['role'] = user['role']
            flash('Login successful.')

            if user['role'] == 'admin':
                return redirect(url_for('admin_panel'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Invalid email or password.')     
    return render_template('login.html')


# Logout Route
@auth_bp.route('/logout')
def logout():
    session.clear()  # clears user and role
    flash('Logged out successfully.')
    return redirect(url_for('auth.login'))
