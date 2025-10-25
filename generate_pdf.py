# generate_pdf.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import datetime
import os
import json

# Load disease info JSON
with open("disease_info.json", "r") as f:
    DISEASE_INFO = json.load(f)

def create_report(user_name, symptoms, disease, confidence=None):
    # Fetch doctor, remedies, precautions
    info = DISEASE_INFO.get(disease.lower(), {
        "doctor": "General Physician",
        "remedies": ["No data available"],
        "precautions": ["No data available"]
    })

    # File path
    report_folder = "reports"
    os.makedirs(report_folder, exist_ok=True)
    file_path = os.path.join(report_folder, f"{user_name}_report.pdf")

    # PDF setup
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterTitle', alignment=1, fontSize=20, spaceAfter=12, textColor=colors.HexColor("#4A148C")))
    styles.add(ParagraphStyle(name='SubHeading', fontSize=13, textColor=colors.HexColor("#6A1B9A"), spaceAfter=6))
    styles.add(ParagraphStyle(name='Body', fontSize=11, leading=16))

    elements = []

    # Header
    elements.append(Paragraph("MedPredict AI - Disease Prediction Report", styles['CenterTitle']))
    elements.append(Spacer(1, 12))

    # User & Date
    date_str = datetime.datetime.now().strftime("%d %B %Y, %I:%M %p")
    user_table = Table([
        ["Name:", user_name],
        ["Date:", date_str]
    ], colWidths=[80, 400])
    user_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ede7f6")),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.gray),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.gray)
    ]))
    elements.append(user_table)
    elements.append(Spacer(1, 20))

    # Disease details
    elements.append(Paragraph("Predicted Disease:", styles['SubHeading']))
    elements.append(Paragraph(f"<b>{disease.title()}</b>", styles['Body']))
    if confidence:
        elements.append(Paragraph(f"Confidence: <b>{confidence*100:.2f}%</b>", styles['Body']))
    elements.append(Spacer(1, 15))

    # Doctor
    elements.append(Paragraph("Recommended Doctor:", styles['SubHeading']))
    elements.append(Paragraph(f"{info['doctor']}", styles['Body']))
    elements.append(Spacer(1, 15))

    # Symptoms
    elements.append(Paragraph("Reported Symptoms:", styles['SubHeading']))
    sym_text = ", ".join(symptoms) if symptoms else "Not specified"
    elements.append(Paragraph(sym_text, styles['Body']))
    elements.append(Spacer(1, 15))

    # Remedies
    elements.append(Paragraph("Home Remedies:", styles['SubHeading']))
    for r in info.get("remedies", []):
        elements.append(Paragraph(f"• {r}", styles['Body']))
    elements.append(Spacer(1, 15))

    # Precautions
    elements.append(Paragraph("Precautions:", styles['SubHeading']))
    for p in info.get("precautions", []):
        elements.append(Paragraph(f"• {p}", styles['Body']))
    elements.append(Spacer(1, 20))

    # Footer
    elements.append(Paragraph(
        "This is an AI-generated report for educational purposes only. Please consult a certified doctor for professional medical advice.",
        ParagraphStyle(name='Footer', fontSize=9, textColor=colors.gray, alignment=1)
    ))

    # Build PDF
    doc.build(elements)
    print(f"Report generated: {file_path}")
    return file_path
