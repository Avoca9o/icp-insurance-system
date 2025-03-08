from docx import Document
from typing import Dict

from config.diagnosis_config import diagnosis_config

def create_docx_file(filename: str, data: Dict):
    doc = Document()
    doc.add_heading('Diagnosis Coefficients', level=0)
    
    i = 1
    for diagnosis_code, coefficient in data.items():
        doc.add_paragraph(f'{i}) {diagnosis_config[diagnosis_code]} ({diagnosis_code}): {coefficient}')
        i += 1
    
    if not filename.endswith('.docx'):
        filename += '.docx'
    doc.save(filename)