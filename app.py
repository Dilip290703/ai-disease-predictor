import mysql.connector
from generate_pdf import create_report
from flask import Flask, render_template, request, session, redirect, url_for, flash
import pickle
import pandas as pd
from auth import auth_bp, bcrypt
import os

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="MITDc@29072003",  # Update if needed
        database="disease_app"
    )


# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Initialize Bcrypt for password hashing
bcrypt.init_app(app)

# Register Blueprint for auth routes
app.register_blueprint(auth_bp)

# Load trained model and symptom list
model = pickle.load(open('disease_model.pkl', 'rb'))
symptoms = ['fever', 'headache', 'cough', 'nausea', 'diarrhea']  # Match your CSV columns

def is_admin():
    return session.get('role') == 'admin'

@app.route('/admin')
def admin_panel():
    if 'user' not in session or not is_admin():
        flash("Access denied: Admins only.")
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get user data
    cur.execute("SELECT id, name, email, role FROM users")
    users = cur.fetchall()

    # Get prediction history
    cur.execute("SELECT id, user_email, prediction, symptoms, timestamp FROM predictions ORDER BY timestamp DESC")
    predictions = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("admin.html", users=users, predictions=predictions)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        flash('Please log in to access prediction.')
        return redirect(url_for('auth.login'))

    selected_symptoms = request.form.getlist('symptoms')
    input_data = [1 if s in selected_symptoms else 0 for s in symptoms]
    prediction = model.predict([input_data])[0]

    from datetime import datetime
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
      INSERT INTO predictions (user_email, prediction, symptoms, timestamp)
      VALUES (%s, %s, %s, NOW())
    """, (session['user'], prediction, ", ".join(selected_symptoms)))
    conn.commit()
    cur.close()
    conn.close()


    # Generate PDF report
    report_path = create_report(session['user'], selected_symptoms, prediction)

    return render_template('result.html',
                       prediction=prediction,
                       user=session['user'],
                       report_link='/' + report_path)



@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.')
    return redirect(url_for('auth.login'))

@app.route('/predict')
def index():
    return render_template('index.html', symptoms=symptoms)

if __name__ == '__main__':
    app.run(debug=True)
