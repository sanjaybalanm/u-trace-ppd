from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import io

def generate_pdf_report(user_name, risk_data):
    """
    Generates a PDF report for the PPD Risk Assessment.
    Returns the PDF content as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # --- Title ---
    title_style = styles['Title']
    title_style.textColor = colors.HexColor("#2C3E50")
    story.append(Paragraph("PPD Exposure Risk Assessment Report", title_style))
    story.append(Spacer(1, 12))

    # --- Header Info ---
    normal_style = styles['Normal']
    date_str = datetime.now().strftime("%B %d, %Y")
    
    header_data = [
        ["Patient Name:", user_name],
        ["Assessment Date:", date_str],
        ["Assessment ID:", f"PPD-{int(datetime.now().timestamp())}"]
    ]
    
    t_header = Table(header_data, colWidths=[1.5*inch, 4*inch])
    t_header.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 24))

    # --- Risk Result Section ---
    risk_level = risk_data.get("risk_level", "UNKNOWN")
    normalized_ppd = risk_data.get("normalized_ppd", risk_data.get("exposure_score", 0))
    
    # Color coding
    risk_color = colors.green
    if risk_level == "HIGH": risk_color = colors.red
    elif risk_level == "MEDIUM": risk_color = colors.orange
    
    risk_style = ParagraphStyle(
        'RiskStyle',
        parent=styles['Heading2'],
        textColor=risk_color,
        fontSize=18,
        spaceAfter=12
    )
    
    story.append(Paragraph(f"Risk Level: {risk_level}", risk_style))
    story.append(Paragraph(f"Exposure Score: {normalized_ppd} / 1.0", styles['Normal']))
    
    if "creatinine_value" in risk_data:
        creat_val = risk_data.get("creatinine_value")
        story.append(Paragraph(f"Creatinine Level: {creat_val} mg/dL", styles['Normal']))
        
    story.append(Spacer(1, 20))

    # --- Detailed Factors Table ---
    story.append(Paragraph("Detailed Factor Analysis", styles['Heading3']))
    
    details = risk_data.get("factor_details", [])
    if details:
        # Added "Value" column
        table_data = [["Factor", "Value", "Contribution", "Status"]]
        for item in details:
            factor_name = item.get("name", "Unknown")
            value = str(item.get("value", "N/A")) # Ensure it's a string
            contribution = f"{item.get('contribution', 0)}%"
            status = item.get("risk_level", "Normal")
            table_data.append([factor_name, value, contribution, status])
            
        # Adjusted widths for 4 columns
        t_factors = Table(table_data, colWidths=[2.5*inch, 2*inch, 1*inch, 1.5*inch])
        t_factors.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#34495E")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#ECF0F1")),
            ('GRID', (0,0), (-1,-1), 1, colors.white),
            # Align values to left/center
            ('ALIGN', (0,1), (1,-1), 'CENTER'),
        ]))
        story.append(t_factors)
    
    story.append(Spacer(1, 24))

    # --- Recommendations ---
    story.append(Paragraph("Clinical Recommendations", styles['Heading3']))
    recommendations = risk_data.get("health_recommendations", [])
    
    if not recommendations and risk_level == "HIGH":
        recommendations = [
            "Consult an occupational health specialist immediately.",
            "Use enhanced PPE (gloves, respiratory protection).",
            "Schedule a follow-up screening in 2 weeks."
        ]
    elif not recommendations:
        recommendations = ["Maintain current safety practices.", "Annual routine check-up."]
        
    for rec in recommendations:
        story.append(Paragraph(f"• {rec}", styles['Normal']))
        story.append(Spacer(1, 6))

    # --- Footer ---
    story.append(Spacer(1, 40))
    footer_text = "This report is computer-generated based on the PPD Risk Prediction System (Random Forest v1.0)."
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.gray)))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
