from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import Party, ParliamentMember

router = APIRouter(prefix="/parties", tags=["parties"])

def serialize_party(p: Party) -> Dict[str, Any]:
    return {
        "id": p.id,
        "name": p.name,
        "abbreviation": p.abbreviation,
        "img_url": p.img_url,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }

def serialize_member(m: ParliamentMember) -> Dict[str, Any]:
    return {
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
def list_parties(
    db: Session = Depends(get_db),
    expand: str | None = Query(None, description='Usa "members" para incluir políticos por partido'),
):
    rows = db.query(Party).all()
    data = [serialize_party(p) for p in rows]

    if expand == "members":
        # añadir miembros
        for item in data:
            members = db.query(ParliamentMember).filter(
                ParliamentMember.party_id == item["id"]
            ).all()
            item["members"] = [serialize_member(m) for m in members]
    return data

@router.get("/{id}", response_model=Dict[str, Any])
def get_party_by_id(
    id: int,
    db: Session = Depends(get_db),
    expand: str | None = Query(None, description='Usa "members" para incluir políticos del partido'),
):
    p = db.query(Party).filter(Party.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    item = serialize_party(p)

    if expand == "members":
        members = db.query(ParliamentMember).filter(
            ParliamentMember.party_id == id
        ).all()
        item["members"] = [serialize_member(m) for m in members]
    return item

@router.get("/{id}/members", response_model=List[Dict[str, Any]])
def get_party_members(id: int, db: Session = Depends(get_db)):
    members = db.query(ParliamentMember).filter(ParliamentMember.party_id == id).all()
    return [serialize_member(m) for m in members]
