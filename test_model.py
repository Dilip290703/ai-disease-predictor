# test_model.py
import pickle
import json
import numpy as np

# ===== 1. Load artifacts =====
with open("disease_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("label_encoder.pkl", "rb") as f:
    le = pickle.load(f)

with open("feature_list.pkl", "rb") as f:
    features = pickle.load(f)

with open("model_meta.json", "r") as f:
    meta = json.load(f)

print("✅ Model & metadata loaded")
print(f"Model Accuracy: {meta['accuracy']:.4f}")
print(f"Number of Diseases: {meta['num_diseases']}")

# ===== 2. User Input Symptoms =====
print("\nAvailable symptoms:")
print(", ".join(features))

user_input = input("\nEnter symptoms separated by commas (e.g., fever,cough,headache): ").strip().lower()
selected = [s.strip().replace(" ", "_") for s in user_input.split(",") if s.strip()]

# ===== 3. Convert input into feature vector =====
x = [1 if f.lower() in selected else 0 for f in features]
x = np.array(x).reshape(1, -1)

# ===== 4. Prediction =====
probs = model.predict_proba(x)[0]
classes = le.inverse_transform(np.arange(len(probs)))

# Get Top-3 predictions
top3 = sorted(zip(classes, probs), key=lambda x: x[1], reverse=True)[:3]

print("\n🎯 Top Predictions:")
for disease, p in top3:
    print(f"- {disease}: {p*100:.2f}%")
