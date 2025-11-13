# AI Disease Predictor 🧠💊

A Flask-based AI-powered disease prediction web app that takes user symptoms and predicts likely illnesses using a trained Machine Learning model. Includes secure login, PDF report generation, and modern UI styling.

## 🔍 Features

- 🔐 User Authentication (Register, Login, Logout)
- 📊 Symptom-based Disease Prediction using ML
- 🧾 PDF Report Generation (FPDF)
- 💾 Prediction History (coming soon)
- 📬 Email Report (optional feature)
- 🎨 Modern Purple-Themed UI (Bootstrap 5)

## 🛠️ Tech Stack

- Python 3, Flask
- MySQL 
- FPDF for PDF reports
- Bootstrap 5 + HTML/CSS
- scikit-learn (for ML model)

## 🚀 Setup Instructions

```bash
# 1. Clone the repo
git clone https://github.com/your-username/ai-disease-predictor.git
cd ai-disease-predictor

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate    # On Windows
source venv/bin/activate   # On Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Flask app
python app.py
```

## 📂 Folder Structure

```
ai-disease-predictor/
│
├── app.py
├── auth.py
├── generate_pdf.py
├── disease_model.pkl
├── templates/
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   └── ...
├── static/
│   └── reports/
├── fonts/
│   └── DejaVuSans.ttf
└── requirements.txt
```

## ✍️ Team

- Dilip Choudhary (Developer)
- Lalit Yelane (Front-End)


## 📜 License

This project is for educational purposes only. Not intended for clinical use.
