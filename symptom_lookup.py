import pandas as pd

# Load your dataset
df = pd.read_csv("Reduced_Diseases_and_Symptoms.csv")
df.columns = df.columns.str.strip().str.lower()

def get_symptoms_for_disease(disease_name):
    disease_rows = df[df["diseases"].str.lower() == disease_name.lower()]
    symptoms = [
        col for col in df.columns
        if col != "diseases" and disease_rows[col].sum() > 0
    ]
    return symptoms

# Example usage:
disease_input = input("Enter disease name: ")
symptoms = get_symptoms_for_disease(disease_input)
print(f"Symptoms for {disease_input}:", symptoms)