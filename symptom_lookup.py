import pandas as pd

# Load your dataset
df = pd.read_csv("Reduced_Diseases_and_Symptoms.csv")
df.columns = df.columns.str.strip().str.lower()

# Filter pneumonia rows
pneumonia_rows = df[df["diseases"].str.lower() == "pneumonia"]

# Find all symptoms where at least one patient with pneumonia has value > 0
symptoms_for_pneumonia = [
    col for col in df.columns 
    if col != "diseases" and pneumonia_rows[col].sum() > 0
]

print("Symptoms for Pneumonia:", symptoms_for_pneumonia)
