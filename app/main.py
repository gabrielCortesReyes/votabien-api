# app/main.py
# uvicorn app.main:app --reload
# http://localhost:8000/docs

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import parliament

from app.api import parliament
from app.api import parties

app = FastAPI(title="VotaBien API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parliament.router, prefix=settings.api_prefix)
app.include_router(parties.router, prefix=settings.api_prefix)


@app.get(settings.api_prefix + "/health")
def health():
    return {"status": "ok"}
