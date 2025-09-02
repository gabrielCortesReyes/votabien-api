# ============================
# SESSIONS API
# ============================

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session, joinedload

from app.db.base import get_db
from app.db.models import LegislativeSession, Attendance
from app.schemas.schemas import (
    LegislativeSessionSchema,
    AttendanceSchema,
    AttendanceWithMemberSchema,
    SessionWithAttendancesAndMembersSchema,
    ParliamentMemberSchema,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])

# ------------------------------------------------------------
# Lista de Sesiones
# ------------------------------------------------------------
@router.get("/", response_model=List[LegislativeSessionSchema])
def list_sessions(db: Session = Depends(get_db)):
    rows = (
        db.query(LegislativeSession)
        .order_by(LegislativeSession.start_date.desc(), LegislativeSession.id.desc())
        .all()
    )
    return rows

# ------------------------------------------------------------
# Detalle de una Sesión
# ------------------------------------------------------------
@router.get("/{id}", response_model=LegislativeSessionSchema)
def get_session(id: int, db: Session = Depends(get_db)):
    s = db.query(LegislativeSession).filter(LegislativeSession.id == id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Not found")
    return s

# ------------------------------------------------------------
# Asistencias de una Sesión + Datos del Diputado
# ------------------------------------------------------------
@router.get("/{id}/attendances", response_model=SessionWithAttendancesAndMembersSchema)
def get_session_attendances(id: int, db: Session = Depends(get_db)):
    s = db.query(LegislativeSession).filter(LegislativeSession.id == id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Not found")

    rows = (
        db.query(Attendance)
        .options(joinedload(Attendance.member))
        .filter(Attendance.session_id == id)
        .order_by(Attendance.id.asc())
        .all()
    )

    result = []
    for a in rows:
        base_att = AttendanceSchema.model_validate(a, from_attributes=True).model_dump()
        result.append(
            AttendanceWithMemberSchema(
                **base_att,
                member=ParliamentMemberSchema.model_validate(a.member, from_attributes=True),
            )
        )

    return {"session": s, "attendances": result}