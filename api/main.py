from fastapi import FastAPI, UploadFile, File
from PyPDF2 import PdfReader
import io

app = FastAPI()

@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    contents = await file.read()

    # Handle PDF files
    if file.filename.endswith(".pdf"):
        pdf = PdfReader(io.BytesIO(contents))
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
    else:
        # Handle text files
        text = contents.decode("utf-8", errors="ignore")

    # Call your analyzer
    result = analyzer.analyze_resume(text)

    return result