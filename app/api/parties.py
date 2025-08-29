from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.db.base import get_db
from app.db.models import Party, ParliamentMember, PartyMembership

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
def list_parties(db: Session = Depends(get_db)):
    rows = db.query(Party).all()
    return [serialize_party(p) for p in rows]

@router.get("/{id}", response_model=Dict[str, Any])
def get_party_with_current_members(id: int, db: Session = Depends(get_db)):
    party = db.query(Party).filter(Party.id == id).first()
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")

    now = func.now()
    rows = (
        db.query(ParliamentMember, PartyMembership)
        .join(PartyMembership, PartyMembership.parliament_member_id == ParliamentMember.id)
        .filter(
            PartyMembership.party_id == id,
            or_(PartyMembership.end_date.is_(None), PartyMembership.end_date > now),
        )
        .order_by(ParliamentMember.last_name.asc(), ParliamentMember.first_name.asc())
        .all()
    )

    members = []
    for m, pm in rows:
        item = serialize_member(m)
        item["membership"] = {
            "start_date": pm.start_date.isoformat() if pm.start_date else None,
            "end_date": pm.end_date.isoformat() if pm.end_date else None,
        }
        members.append(item)

    data = serialize_party(party)
    data["members"] = members
    return data

@router.get("/{id}/members", response_model=List[Dict[str, Any]])
def get_party_current_members(id: int, db: Session = Depends(get_db)):
    party = db.query(Party).filter(Party.id == id).first()
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")

    now = func.now()
    rows = (
        db.query(ParliamentMember, PartyMembership)
        .join(PartyMembership, PartyMembership.parliament_member_id == ParliamentMember.id)
        .filter(
            PartyMembership.party_id == id,
            or_(PartyMembership.end_date.is_(None), PartyMembership.end_date > now),
        )
        .order_by(ParliamentMember.last_name.asc(), ParliamentMember.first_name.asc())
        .all()
    )

    results = []
    for m, pm in rows:
        item = serialize_member(m)
        item["membership"] = {
            "start_date": pm.start_date.isoformat() if pm.start_date else None,
            "end_date": pm.end_date.isoformat() if pm.end_date else None,
        }
        results.append(item)

    return results