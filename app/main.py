# ============================
# MAIN APP
# ============================
# Run: uvicorn app.main:app --reload
# Docs: http://localhost:8000/docs

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import parliament, parties, sessions, territory, laws

# ------------------------------------------------------------
# Inicialización de la App
# ------------------------------------------------------------
app = FastAPI(title="VotaBien API", version="0.1.0")

# ------------------------------------------------------------
# Configuración de CORS
# ------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------
# Routers
# ------------------------------------------------------------
app.include_router(parliament.router, prefix=settings.api_prefix)
app.include_router(parties.router, prefix=settings.api_prefix)
app.include_router(sessions.router, prefix=settings.api_prefix)
app.include_router(territory.router, prefix=settings.api_prefix)
app.include_router(laws.router, prefix=settings.api_prefix)

# ------------------------------------------------------------
# Endpoint de Health Check
# ------------------------------------------------------------
@app.get(settings.api_prefix + "/health")
def health():
    return {"status": "ok"}