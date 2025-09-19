import pickle
from sklearn.preprocessing import LabelEncoder

# 🔹 List of all 41 diseases (from standard dataset)
diseases = [
    'Fungal infection', 'Allergy', 'GERD', 'Chronic cholestasis',
    'Drug Reaction', 'Peptic ulcer disease', 'AIDS', 'Diabetes ',
    'Gastroenteritis', 'Bronchial Asthma', 'Hypertension ', 'Migraine',
    'Cervical spondylosis', 'Paralysis (brain hemorrhage)', 'Jaundice',
    'Malaria', 'Chicken pox', 'Dengue', 'Typhoid', 'hepatitis A',
    'Hepatitis B', 'Hepatitis C', 'Hepatitis D', 'Hepatitis E',
    'Alcoholic hepatitis', 'Tuberculosis', 'Common Cold', 'Pneumonia',
    'Dimorphic hemmorhoids(piles)', 'Heart attack', 'Varicose veins',
    'Hypothyroidism', 'Hyperthyroidism', 'Hypoglycemia',
    'Osteoarthristis', 'Arthritis', '(vertigo) Paroymsal  Positional Vertigo',
    'Acne', 'Urinary tract infection', 'Psoriasis', 'Impetigo'
]

# Create and fit encoder
le = LabelEncoder()
le.fit(diseases)

# Save the encoder
with open("label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)

print("✅ label_encoder.pkl created successfully!")
