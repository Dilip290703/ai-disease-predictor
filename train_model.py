import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load the dataset
df = pd.read_csv('symptom_disease.csv')

# Separate features and target
X = df.drop('disease', axis=1)
y = df['disease']

# Train the model
model = RandomForestClassifier()
model.fit(X, y)

# Save the trained model
with open('disease_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Model trained and saved as disease_model.pkl")
