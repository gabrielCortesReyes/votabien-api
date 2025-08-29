from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy import and_, func

from app.db.base import get_db
from app.core.config import settings
from app.db.models import ParliamentMember, Party, PartyMembership

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

def serialize_party(p: Party) -> Dict[str, Any]:
    return {
        "id": p.id,
        "name": p.name,
        "abbreviation": p.abbreviation,

        "img_url": p.img_url,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
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

@router.get("/{id}/party", response_model=Dict[str, Any])
async def get_member_with_current_party(id: int, db: Session = Depends(get_db)):
    member: Optional[ParliamentMember] = (
        db.query(ParliamentMember).filter(ParliamentMember.id == id).first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Not found")
    
    current_membership: Optional[PartyMembership] = (
        db.query(PartyMembership)
        .filter(
            and_(
                PartyMembership.parliament_member_id == id,
                PartyMembership.end_date.is_(None),
            )
        )
        .order_by(PartyMembership.start_date.desc())
        .first()
    )

    if not current_membership:
        current_membership = (
            db.query(PartyMembership)
            .filter(PartyMembership.parliament_member_id == id)
            .order_by(PartyMembership.start_date.desc())
            .first()
        )

    result: Dict[str, Any] = {
        "member": serialize_member(member),
        "party": None,
    }

    if current_membership:
        party = db.query(Party).filter(Party.id == current_membership.party_id).first()
        if party:
            party_data = serialize_party(party)
            party_data["membership"] = {
                "start_date": current_membership.start_date.isoformat() if current_membership.start_date else None,
                "end_date": current_membership.end_date.isoformat() if current_membership.end_date else None,
            }
            result["party"] = party_data

    return result

@router.get("/{id}/parties", response_model=Dict[str, Any])
async def get_member_with_all_parties(id: int, db: Session = Depends(get_db)):
    member: Optional[ParliamentMember] = (
        db.query(ParliamentMember).filter(ParliamentMember.id == id).first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Not found")
    
    rows = (
        db.query(PartyMembership, Party)
        .join(Party, Party.id == PartyMembership.party_id)
        .filter(PartyMembership.parliament_member_id == id)
        .order_by(PartyMembership.start_date.asc())
        .all()
    )
    history = []
    for pm, p in rows:
        party_data = serialize_party(p)
        party_data["membership"] = {
            "start_date": pm.start_date.isoformat() if pm.start_date else None,
            "end_date": pm.end_date.isoformat() if pm.end_date else None,
        }
        history.append(party_data)

    return {
        "member": serialize_member(member),
        "parties": history, 
    }