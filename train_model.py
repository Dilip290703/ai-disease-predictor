# train_model.py
import pandas as pd
import pickle
import json
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from lightgbm import LGBMClassifier

# ===== 1. Load dataset =====
DATASET_FILE = "Reduced_Diseases_and_Symptoms.csv"

df = pd.read_csv(DATASET_FILE)
print("Dataset shape:", df.shape)

# ===== 2. Clean column names =====
df.columns = df.columns.str.replace('[^A-Za-z0-9_]+', '_', regex=True)

# ===== 3. Separate features & target =====
if 'diseases' not in df.columns:
    raise ValueError("'diseases' column not found in dataset.")

X = df.drop('diseases', axis=1)
y = df['diseases']

# Ensure features are numeric
X = X.apply(pd.to_numeric, errors='coerce').fillna(0).astype('float32')

# ===== 4. Encode labels =====
le = LabelEncoder()
y = le.fit_transform(y)

# ===== 5. Split =====
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ===== 6. Train LightGBM =====
model = LGBMClassifier(
    n_estimators=200,
    learning_rate=0.05,
    num_leaves=31,
    subsample=0.8,
    colsample_bytree=0.8,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)

# Cross-validation (optional but recommended)
scores = cross_val_score(model, X, y, cv=5, scoring="accuracy", n_jobs=-1)
print(f"✅ Cross-validated Accuracy: {scores.mean():.4f} ± {scores.std():.4f}")

# Train final model
model.fit(X_train, y_train)

# ===== 7. Evaluate =====
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Hold-out Accuracy: {acc:.4f}")

# ===== 8. Save model, label encoder, and features =====
with open('disease_model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('label_encoder.pkl', 'wb') as f:
    pickle.dump(le, f)

with open('feature_list.pkl', 'wb') as f:
    pickle.dump(list(X.columns), f)

meta = {
    "features": list(X.columns),
    "classes": le.classes_.tolist(),
    "accuracy": float(acc),
    "num_diseases": len(le.classes_)
}
with open("model_meta.json", "w") as f:
    json.dump(meta, f, indent=2)

print("✅ Model, Label Encoder, Feature List, and Metadata saved successfully!")
