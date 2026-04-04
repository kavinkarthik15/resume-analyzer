from fastapi import FastAPI, UploadFile, File
from PyPDF2 import PdfReader
import io
import logging

from ml.analyzer_pipeline import CompleteResumeAnalysis as ResumeAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

analyzer = ResumeAnalyzer()
# Provide alias for the expected method name
analyzer.analyze_resume = analyzer.analyze_resume_text

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        # File validation
        if not file.filename.endswith((".pdf", ".txt")):
            return {"error": "Only PDF or TXT files allowed"}

        # File size limit (2MB)
        if len(contents) > 2 * 1024 * 1024:
            return {"error": "File too large"}

        logger.info("Processing resume")

        if file.filename.endswith(".pdf"):
            pdf = PdfReader(io.BytesIO(contents))
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        else:
            text = contents.decode("utf-8", errors="ignore")

        if not text.strip():
            return {"error": "No text extracted from file"}

        result = analyzer.analyze_resume(text)

        return result

    except Exception as e:
        return {
            "success": False,
            "error": "Internal processing error"
        }