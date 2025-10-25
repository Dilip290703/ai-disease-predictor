# app.py
import mysql.connector
import json
import pickle
import numpy as np
import os
from generate_pdf import create_report
from flask import Flask, render_template, request, session, redirect, url_for, flash
from auth import auth_bp, bcrypt
from flask import send_from_directory

# ===== DB connection =====
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="MITDc@29072003",   # change if needed
        database="disease_app"
    )

# ===== Flask setup =====
app = Flask(__name__)
app.secret_key = 'your_secret_key'   # change to a strong random key
bcrypt.init_app(app)
app.register_blueprint(auth_bp)

# ===== Load model artifacts =====
with open('disease_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('label_encoder.pkl', 'rb') as f:
    label_encoder = pickle.load(f)

with open('feature_list.pkl', 'rb') as f:
    FEATURE_LIST = pickle.load(f)

# Load disease info (doctor + remedies + precautions)
with open("disease_info.json", "r") as f:
    DISEASE_INFO = json.load(f)

# ===== Load disease info JSON =====
try:
    with open("disease_info.json", "r") as f:
        disease_info = json.load(f)
except Exception:
    disease_info = {}

# ===== Helpers =====
def is_admin():
    return session.get('role') == 'admin'

def sanitize_symptom(s: str) -> str:
    return (s or '').strip().lower().replace(' ', '_')

def build_input_vector(selected_symptoms):
    selected_set = set(selected_symptoms)
    return [1 if feat in selected_set else 0 for feat in FEATURE_LIST]

# ===== Routes =====
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict', methods=['GET'])
def index():
    return render_template('index.html', symptoms=FEATURE_LIST)

@app.route('/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        flash('Please log in to access prediction.')
        return redirect(url_for('auth.login'))

    raw = request.form.get('symptoms', '')
    selected_symptoms = []

    # Parse Tagify JSON
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            for item in data:
                val = sanitize_symptom((item.get('value') if isinstance(item, dict) else str(item)))
                if val:
                    selected_symptoms.append(val)
        else:
            selected_symptoms = [sanitize_symptom(x) for x in str(raw).split(',') if x.strip()]
    except Exception:
        selected_symptoms = [sanitize_symptom(x) for x in raw.split(',') if x.strip()]

    # 🚨 Rule: Require at least 5 symptoms
    if len(selected_symptoms) < 5:
        return render_template(
            'result.html',
            prediction=None,
            error="Please select at least 5 symptoms for accurate prediction."
        )

    # Build input
    input_vec = build_input_vector(selected_symptoms)
    input_vec = np.array(input_vec, dtype=np.float32).reshape(1, -1)

    # Predict + probability
    pred_encoded = model.predict(input_vec)[0]
    probas = model.predict_proba(input_vec)[0]
    confidence = float(probas[pred_encoded]) if pred_encoded < len(probas) else None

    disease = label_encoder.inverse_transform([pred_encoded])[0]

    # Attach info (doctor/remedies/precautions)
    info = disease_info.get(disease.lower(), {})
    enriched_prediction = {
        "disease": disease,
        "confidence": confidence,
        "doctor": info.get("doctor", "Consult a General Physician"),
        "remedies": info.get("remedies", ["No remedies available"]),
        "precautions": info.get("precautions", ["No precautions available"])
    }

    # Save to DB
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO predictions (user_email, prediction, symptoms, timestamp)
            VALUES (%s, %s, %s, NOW())
            """,
            (
                str(session.get('user') or ''),
                disease,
                ", ".join(selected_symptoms)
            )
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("DB insert error:", e)

    # Generate PDF
    report_path = create_report(
        session.get('user') or '',
        selected_symptoms,
        disease
    )

    return render_template(
        'result.html',
        prediction=enriched_prediction,
        user=session.get('name') or session.get('user'),
        report_link = f"/reports/{os.path.basename(report_path)}" if report_path else None
    )

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/doctor/<disease>')
def doctor_page(disease):
    disease_key = disease.strip().lower()

    # Fetch info from JSON
    info = DISEASE_INFO.get(disease_key, {
        "doctor": "General Physician",
        "remedies": ["No data available"],
        "precautions": ["No data available"]
    })

    return render_template(
        "doctor.html",
        disease=disease,
        doctor=info["doctor"],
        remedies=info.get("remedies", []),
        precautions=info.get("precautions", []),
        google_api_key="AIzaSyCojlbzzWiC7puLXVgpyaYQhSx39vtyCrM"  # Pass API key
    )


@app.route('/admin')
def admin_panel():
    if 'user' not in session or not is_admin():
        flash("Access denied: Admins only.")
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, role FROM users")
    users = cur.fetchall()
    cur.execute("SELECT id, user_email, prediction, symptoms, timestamp FROM predictions ORDER BY timestamp DESC")
    predictions = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("admin.html", users=users, predictions=predictions)



@app.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if not is_admin():
        flash("Access denied.")
        return redirect(url_for('admin_panel'))
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        cur.execute("UPDATE users SET name=%s, email=%s, role=%s WHERE id=%s", (name, email, role, user_id))
        conn.commit()
        cur.close()
        conn.close()
        flash("User updated.")
        return redirect(url_for('admin_panel'))
    cur.execute("SELECT id, name, email, role FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('edit_user.html', user=user)

@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not is_admin():
        flash("Access denied.")
        return redirect(url_for('admin_panel'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("User deleted.")
    return redirect(url_for('admin_panel'))



@app.route('/admin/prediction/delete/<int:prediction_id>', methods=['POST'])
def delete_prediction(prediction_id):
    if not is_admin():
        flash("Access denied.")
        return redirect(url_for('admin_panel'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM predictions WHERE id=%s", (prediction_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Prediction deleted.")
    return redirect(url_for('admin_panel'))



@app.route('/remedies/<disease>')
def remedies_page(disease):
    disease_key = disease.strip().lower()
    info = DISEASE_INFO.get(disease_key, {
        "doctor": "General Physician",
        "remedies": ["No data available"],
        "precautions": ["No data available"]
    })

    return render_template(
        "remedies.html",
        disease=disease,
        remedies=info.get("remedies", []),
        precautions=info.get("precautions", [])
    )


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('name', None)
    session.pop('role', None)
    flash('Logged out successfully.')
    return redirect(url_for('auth.login'))


@app.route('/reports/<path:filename>')
def serve_report(filename):
    return send_from_directory('reports', filename)

if __name__ == '__main__':
    app.run(debug=True)
