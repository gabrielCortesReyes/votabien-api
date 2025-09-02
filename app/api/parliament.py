# ============================
# PARLIAMENT API
# ============================

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db.base import get_db
from app.db.models import ParliamentMember, Party, PartyMembership, Attendance
from app.schemas.schemas import (
    ParliamentMemberSchema,
    PartyWithMembershipSchema,
    MemberWithCurrentPartySchema,
    MemberWithAllPartiesSchema,
    MembershipSchema,
    AttendanceSchema,
    MemberAttendanceResponseSchema,
)

router = APIRouter(prefix="/parliament", tags=["parliament"])

# ------------------------------------------------------------
# Lista de Diputados
# ------------------------------------------------------------
@router.get("/", response_model=List[ParliamentMemberSchema])
async def list_members(db: Session = Depends(get_db)):
    rows = db.query(ParliamentMember).all()
    return rows

# ------------------------------------------------------------
# Detalle por ID
# ------------------------------------------------------------
@router.get("/{id}", response_model=ParliamentMemberSchema)
async def get_member_by_id(id: int, db: Session = Depends(get_db)):
    m = db.query(ParliamentMember).filter(ParliamentMember.id == id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Not found")
    return m

# ------------------------------------------------------------
# Diputado + Partido Actual
# ------------------------------------------------------------
@router.get("/{id}/party", response_model=MemberWithCurrentPartySchema)
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
    ) or (
        db.query(PartyMembership)
        .filter(PartyMembership.parliament_member_id == id)
        .order_by(PartyMembership.start_date.desc())
        .first()
    )

    result = {"member": member, "party": None}

    if current_membership:
        party = db.query(Party).filter(Party.id == current_membership.party_id).first()
        if party:
            result["party"] = PartyWithMembershipSchema(
                **party.__dict__,
                membership=MembershipSchema(
                    start_date=current_membership.start_date,
                    end_date=current_membership.end_date,
                ),
            )

    return result

# ------------------------------------------------------------
# Diputado + Historial de Partidos
# ------------------------------------------------------------
@router.get("/{id}/parties", response_model=MemberWithAllPartiesSchema)
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

    parties = [
        PartyWithMembershipSchema(
            **p.__dict__,
            membership=MembershipSchema(
                start_date=pm.start_date, end_date=pm.end_date
            ),
        )
        for pm, p in rows
    ]

    return {"member": member, "parties": parties}

# ------------------------------------------------------------
# Asistencia de un Diputado
# ------------------------------------------------------------
@router.get("/{id}/attendances", response_model=MemberAttendanceResponseSchema)
async def get_member_attendance(id: int, db: Session = Depends(get_db)):

    member = db.query(ParliamentMember).filter(ParliamentMember.id == id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Not found")

    detail: List[Attendance] = (
        db.query(Attendance)
        .filter(Attendance.parliament_member_id == id)
        .order_by(Attendance.id.asc())
        .all()
    )

    PRESENT_ALIASES = {"asiste"}
    total_sessions = len(detail)
    present = 0
    for a in detail:
        t = (a.attendance_type or "").strip().lower()
        if t in PRESENT_ALIASES:
            present += 1

    absent = max(total_sessions - present, 0)
    present_pct = round((present / total_sessions) * 100, 2) if total_sessions else 0.0

    return {
        "member": member,
        "resume": {
            "total_sessions": total_sessions,
            "attendance": present,
            "absence": absent,
            "attendance_percentage": present_pct,
        },
        "detail": detail,
    }