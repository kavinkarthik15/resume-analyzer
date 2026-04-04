from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
import io
import logging

from ml.analyzer_pipeline import CompleteResumeAnalysis as ResumeAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = ResumeAnalyzer()
# Provide alias for the expected method name
analyzer.analyze_resume = analyzer.analyze_resume_text


def error_response(message: str) -> dict:
    return {
        "success": False,
        "error": message
    }


def success_response(payload: dict) -> dict:
    response = dict(payload)
    response.setdefault("success", True)
    return response

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        # File validation
        if not file.filename.endswith((".pdf", ".txt")):
            return error_response("Only PDF or TXT files allowed")

        # File size limit (2MB)
        if len(contents) > 2 * 1024 * 1024:
            return error_response("File too large")

        logger.info("Processing resume")

        if file.filename.endswith(".pdf"):
            pdf = PdfReader(io.BytesIO(contents))
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        else:
            text = contents.decode("utf-8", errors="ignore")

        if not text.strip():
            return error_response("No text extracted from file")

        result = analyzer.analyze_resume(text)

        if isinstance(result, dict):
            return success_response(result)

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        return error_response(str(e))