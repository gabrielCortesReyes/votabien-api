# app/main.py
# uvicorn app.main:app --reload
# http://localhost:8000/docs

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes_law_projects import router as law_projects_router
from app.api.routes_parliament_members import router as members_router

app = FastAPI(title="Legislative API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(law_projects_router, prefix=settings.api_prefix)
app.include_router(members_router,     prefix=settings.api_prefix)

@app.get(settings.api_prefix + "/health")
def health():
    return {"status": "ok"}
