from generate_pdf import create_report
from flask import Flask, render_template, request, session, redirect, url_for, flash
import pickle
import pandas as pd
from auth import auth_bp, bcrypt
import os

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
