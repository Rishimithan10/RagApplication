from pdfminer.high_level import extract_text
from utils import latency

def extract_text_from_pdf(file_path):
    with latency.measure("1. PDF Extraction"):
        text = extract_text(file_path)
    return text
