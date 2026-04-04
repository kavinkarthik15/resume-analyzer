import re
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document


def clean_text(text: str) -> str:
    """Clean extracted resume text based on Phase 1 rules."""
    text = text.lower()
    text = text.replace("\n", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_from_pdf(file_path: str) -> str:
    """Extract raw text from PDF using PyMuPDF."""
    collected = []
    with fitz.open(file_path) as doc:
        for page in doc:
            collected.append(page.get_text("text"))
    return "\n".join(collected)


def _extract_from_docx(file_path: str) -> str:
    """Extract raw text from DOCX using python-docx."""
    document = Document(file_path)
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def _extract_from_txt(file_path: str) -> str:
    """Extract raw text from TXT file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def extract_text(file_path: str) -> str:
    """Extract and clean text from a PDF, DOCX, or TXT resume file."""
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        raw_text = _extract_from_pdf(file_path)
    elif extension == ".docx":
        raw_text = _extract_from_docx(file_path)
    elif extension == ".txt":
        raw_text = _extract_from_txt(file_path)
    else:
        raise ValueError("Unsupported file format. Please upload a PDF, DOCX, or TXT file.")

    return clean_text(raw_text)
