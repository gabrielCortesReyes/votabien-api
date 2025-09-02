# ============================
# PARTIES API
# ============================

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.db.base import get_db
from app.db.models import Party, ParliamentMember, PartyMembership
from app.schemas.schemas import (
    PartySchema,
    PartyWithMembersSchema,
    MemberWithMembershipSchema,
    MembershipSchema,
)

router = APIRouter(prefix="/parties", tags=["parties"])

# ------------------------------------------------------------
# Lista de Partidos
# ------------------------------------------------------------
@router.get("/", response_model=List[PartySchema])
def list_parties(db: Session = Depends(get_db)):
    return db.query(Party).all()

# ------------------------------------------------------------
# Partido + Diputados Actuales
# ------------------------------------------------------------ 
@router.get("/{id}", response_model=PartyWithMembersSchema)
def get_party_with_current_members(id: int, db: Session = Depends(get_db)):
    party = db.query(Party).filter(Party.id == id).first()
    if not party:
        raise HTTPException(status_code=404, detail="Not found")

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

    members = [
        MemberWithMembershipSchema(
            **m.__dict__,
            membership=MembershipSchema(
                start_date=pm.start_date, end_date=pm.end_date
            ),
        )
        for m, pm in rows
    ]

    return PartyWithMembersSchema(**party.__dict__, members=members)

# ------------------------------------------------------------
# Lista de Diputados Actuales de un Partido
# ------------------------------------------------------------
@router.get("/{id}/members", response_model=List[MemberWithMembershipSchema])
def get_party_current_members(id: int, db: Session = Depends(get_db)):
    party = db.query(Party).filter(Party.id == id).first()
    if not party:
        raise HTTPException(status_code=404, detail="Not found")

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

    return [
        MemberWithMembershipSchema(
            **m.__dict__,
            membership=MembershipSchema(
                start_date=pm.start_date, end_date=pm.end_date
            ),
        )
        for m, pm in rows
    ]