from pdfminer.high_level import extract_text
def extract_text_from_pdf(file_path):
    text = extract_text(file_path)
    return text