from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db
from app.core.config import settings

# Model sólo se usa si USE_MOCK = False
from app.db.models import LawProject

router = APIRouter(prefix="/law-projects", tags=["law-projects"])

# ---------- MOCK DATA ----------
MOCK_PROJECTS: List[Dict[str, Any]] = [
    {"id": 1, "project_id": "12345-06", "name": "Reforma a la Educación", "status": "En discusión", "admission_date": str(date.today()), "stage": "Primer trámite"},
    {"id": 2, "project_id": "67890-07", "name": "Ley de Transporte",       "status": "Aprobado",     "admission_date": str(date.today()), "stage": "Segundo trámite"},
    {"id": 3, "project_id": "11121-08", "name": "Seguridad Pública",       "status": "Rechazado",    "admission_date": str(date.today()), "stage": "Comisión"},
]

def _apply_mock_filters(items: List[Dict[str, Any]], q: str | None, status: str | None, voted: str | None) -> List[Dict[str, Any]]:
    data = items
    if q:
        q_low = q.lower()
        data = [x for x in data if q_low in (x.get("name","").lower() + " " + x.get("project_id","").lower())]
    if status:
        data = [x for x in data if x.get("status") == status]
    if voted == "today":
        today_str = str(date.today())
        data = [x for x in data if str(x.get("admission_date")) == today_str]
    return data

# ---------- ROUTES ----------

@router.get("")
def list_law_projects(
    db: Session = Depends(get_db),
    q: str | None = Query(None, description="Texto a buscar en el nombre"),
    status: str | None = Query(None, description="Estado: Aprobado/Rechazado/En discusión..."),
    voted: str | None = Query(None, description="today|week (mock de filtro de votación)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    # Si estamos en modo MOCK o falla la DB, respondemos con mock
    if settings.use_mock:
        data = _apply_mock_filters(MOCK_PROJECTS, q, status, voted)
        return {"items": data[offset:offset+limit], "limit": limit, "offset": offset, "count": len(data), "source": "mock"}

    try:
        stmt = select(LawProject).order_by(LawProject.admission_date.desc().nullslast())
        if q:
            stmt = stmt.where(LawProject.name.ilike(f"%{q}%"))
        if status:
            stmt = stmt.where(LawProject.status == status)
        if voted == "today":
            stmt = stmt.where(LawProject.admission_date == date.today())

        rows = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
        items = [
            {
                "id": r.id,
                "project_id": r.project_id,
                "name": r.name,
                "admission_date": r.admission_date,
                "stage": r.legislative_stage,
                "status": r.status,
            } for r in rows
        ]
        return {"items": items, "limit": limit, "offset": offset, "count": len(items), "source": "db"}
    except Exception:
        # Fallback silencioso a MOCK si la tabla no existe u otro error
        data = _apply_mock_filters(MOCK_PROJECTS, q, status, voted)
        return {"items": data[offset:offset+limit], "limit": limit, "offset": offset, "count": len(data), "source": "mock-fallback"}

@router.get("/{id}")
def get_law_project(id: int, db: Session = Depends(get_db)):
    if settings.use_mock:
        for p in MOCK_PROJECTS:
            if p["id"] == id:
                return {
                    **p,
                    "summary": "Resumen de prueba para el proyecto.",
                    "votes": {"favor": 70, "contra": 20, "abst": 10},
                }
        raise HTTPException(404, "Law project not found (mock)")

    try:
        obj = db.get(LawProject, id)
        if not obj:
            raise HTTPException(404, "Law project not found")
        return {
            "id": obj.id,
            "project_id": obj.project_id,
            "name": obj.name,
            "admission_date": obj.admission_date,
            "stage": obj.legislative_stage,
            "status": obj.status,
            "votes": {"favor": 70, "contra": 20, "abst": 10},  # TODO: reemplazar por datos reales
            "summary": "Resumen del proyecto (desde DB cuando exista columna/relación)."
        }
    except HTTPException:
        raise
    except Exception:
        # Fallback a mock si algo peta
        for p in MOCK_PROJECTS:
            if p["id"] == id:
                return {
                    **p,
                    "summary": "Resumen de prueba para el proyecto.",
                    "votes": {"favor": 70, "contra": 20, "abst": 10},
                }
        raise HTTPException(404, "Law project not found (mock-fallback)")

