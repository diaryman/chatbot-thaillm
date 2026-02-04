import json
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def export_conversation_to_pdf(conv_data):
    """
    Export a single conversation turn to PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(f"Smart Court AI - Conversation Export", styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Question
    elements.append(Paragraph(f"<b>Timestamp:</b> {conv_data['timestamp']}", styles['Normal']))
    elements.append(Paragraph(f"<b>Question:</b> {conv_data['question']}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Responses
    for resp in conv_data['responses']:
        elements.append(Paragraph(f"<b>Model: {resp['model_name']}</b>", styles['Heading3']))
        # We handle newlines in answer
        answer_text = resp['answer'].replace('\n', '<br/>')
        elements.append(Paragraph(answer_text, styles['Normal']))
        elements.append(Spacer(1, 10))
    
    # If there's a recommended answer
    if conv_data.get('comment'):
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"<b>Recommended / Corrected Answer:</b>", styles['Heading4']))
        elements.append(Paragraph(conv_data['comment'], styles['Normal']))

    doc.build(elements)
    pdf_value = buffer.getvalue()
    buffer.close()
    return pdf_value

def export_history_to_csv(history_data):
    """
    Export full history to CSV.
    """
    flat_data = []
    for conv in history_data:
        for resp in conv['responses']:
            flat_data.append({
                'Timestamp': conv['timestamp'],
                'Question': conv['question'],
                'Model': resp['model_name'],
                'Answer': resp['answer'],
                'Cost': resp['cost'],
                'Suggested Correct Answer': conv.get('comment', '')
            })
    df = pd.DataFrame(flat_data)
    return df.to_csv(index=False).encode('utf-8-sig')
