import pdfplumber
import docx

# -------- PDF --------
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.lower()

# -------- DOCX --------
def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return "\n".join(text).lower()

# -------- TXT --------
def extract_text_from_txt(file):
    text = file.read().decode("utf-8")
    return text.lower()