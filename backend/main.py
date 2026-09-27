from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router


app = FastAPI(
    title="LegalEase API",
    description="AI-Powered Legal Document Generator",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def root():
    return {
        "message": "LegalEase API is running",
        "status": "healthy"
    }


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }


app.include_router(router)python _m uvicorn