from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db
from app.core.config import settings

# Model sólo se usa si USE_MOCK = False
from app.db.models import ParliamentMember

router = APIRouter(prefix="/parliament-members", tags=["parliament-members"])

# ---------- MOCK DATA ----------
MOCK_MEMBERS: List[Dict[str, Any]] = [
    {"id": 1, "name": "Diputado Juan Pérez", "party": "Independiente", "district": "Santiago Centro"},
    {"id": 2, "name": "Diputada Ana Gómez",  "party": "Partido X",     "district": "Valparaíso"},
    {"id": 3, "name": "Diputado Carlos Ruiz","party": "Partido Y",     "district": "Ñuñoa"},
]

def _apply_member_filters(items: List[Dict[str, Any]], q: str | None, party: str | None) -> List[Dict[str, Any]]:
    data = items
    if q:
        q_low = q.lower()
        data = [x for x in data if q_low in x.get("name","").lower()]
    if party:
        data = [x for x in data if x.get("party") == party]
    return data

# ---------- ROUTES ----------

@router.get("")
def list_members(
    db: Session = Depends(get_db),
    q: str | None = Query(None, description="Buscar por nombre"),
    party: str | None = Query(None, description="Nombre del partido"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    if settings.use_mock:
        data = _apply_member_filters(MOCK_MEMBERS, q, party)
        return {"items": data[offset:offset+limit], "limit": limit, "offset": offset, "count": len(data), "source": "mock"}

    try:
        stmt = select(ParliamentMember).order_by(ParliamentMember.full_name.asc())
        if q:
            stmt = stmt.where(ParliamentMember.full_name.ilike(f"%{q}%"))
        # Nota: para party por nombre, deberíamos unir a Party. Lo dejamos para cuando esté el esquema real.

        rows = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
        items = [
            {
                "id": r.id,
                "name": r.full_name,
                "party": getattr(r.party, "name", None),
                "district": r.district,
            } for r in rows
        ]
        return {"items": items, "limit": limit, "offset": offset, "count": len(items), "source": "db"}
    except Exception:
        data = _apply_member_filters(MOCK_MEMBERS, q, party)
        return {"items": data[offset:offset+limit], "limit": limit, "offset": offset, "count": len(data), "source": "mock-fallback"}

@router.get("/{id}")
def get_member(id: int, db: Session = Depends(get_db)):
    if settings.use_mock:
        for m in MOCK_MEMBERS:
            if m["id"] == id:
                return {
                    **m,
                    "last_votes": [
                        {"project": "Reforma a la Educación", "vote": "A favor"},
                        {"project": "Ley de Transporte", "vote": "En contra"},
                    ]
                }
        raise HTTPException(404, "Member not found (mock)")

    try:
        obj = db.get(ParliamentMember, id)
        if not obj:
            raise HTTPException(404, "Member not found")
        return {
            "id": obj.id,
            "name": obj.full_name,
            "party": getattr(obj.party, "name", None),
            "district": obj.district,
            "last_votes": [
                {"project": "Reforma a la Educación", "vote": "A favor"},
                {"project": "Ley de Transporte", "vote": "En contra"},
            ],
        }
    except HTTPException:
        raise
    except Exception:
        for m in MOCK_MEMBERS:
            if m["id"] == id:
                return {
                    **m,
                    "last_votes": [
                        {"project": "Reforma a la Educación", "vote": "A favor"},
                        {"project": "Ley de Transporte", "vote": "En contra"},
                    ]
                }
        raise HTTPException(404, "Member not found (mock-fallback)")

