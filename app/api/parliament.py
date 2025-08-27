from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.base import get_db
from app.core.config import settings
from app.db.models import ParliamentMember

router = APIRouter(prefix="/parliament", tags=["parliament"])

def serialize_member(m: ParliamentMember) -> Dict[str, Any]:
    return{
        "id": m.id,
        "parlid": m.parlid,
        "role": m.role,
        "first_name": m.first_name,
        "middle_name": m.middle_name,
        "last_name": m.last_name,
        "second_last_name": m.second_last_name,
        "birth_date": m.birth_date.isoformat() if m.birth_date else None,
        "gender": m.gender,
        "region": m.region,
        "constituency": m.constituency,
        "party_id": m.party_id,
        "phone": m.phone,
        "email": m.email,
        "curriculum": m.curriculum,
    }

@router.get("/", response_model=List[Dict[str, Any]])
async def list_members(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    rows = db.query(ParliamentMember).offset(offset).limit(limit).all()
    return [serialize_member(m) for m in rows]

@router.get("/{id}", response_model=Dict[str, Any])
async def get_member_by_id(id: int, db: Session = Depends(get_db)):
    m = db.query(ParliamentMember).filter(ParliamentMember.id == id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Not found")
    return serialize_member(m)



## endpoint para que traiga un parlamentario por su ID
## otra ruta que traiga partidos todos los politicos
## endpoint traerlos por id
