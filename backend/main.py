from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.resume import router as resume_router
from .routes.job import router as job_router
from .routes.chat import router as chat_router
from .routes.ml import router as ml_router
from .routes.rewrite import router as rewrite_router

app = FastAPI(title="AI Resume Analyzer API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resume_router, prefix="/api", tags=["Resume"])
app.include_router(job_router, prefix="/api", tags=["Job"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(ml_router, prefix="/api", tags=["ML"])
app.include_router(rewrite_router, prefix="/api", tags=["Rewrite"])

@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)