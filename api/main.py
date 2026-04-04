from fastapi import FastAPI, UploadFile, File
from PyPDF2 import PdfReader
import io

app = FastAPI()

@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        from PyPDF2 import PdfReader
        import io

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
        return {"error": str(e)}