from fastapi import FastAPI, UploadFile, File
from ml.analyzer_pipeline import CompleteResumeAnalysis

app = FastAPI()
analyzer = CompleteResumeAnalysis()

@app.get("/")
def root():
    return {"message": "Resume Analyzer API running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")

    result = analyzer.analyze_resume_text(text)
    
    return result