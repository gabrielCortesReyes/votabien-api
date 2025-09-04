from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import cast, String

from app.db.base import get_db
from app.db.models import District, Commune, DistrictCommune, ParliamentMember
from app.schemas.schemas import ( 
    DistrictSchema, 
    CommuneSchema,
    ParliamentMemberSchema, 
    DistrictWithCommunesAndMembersSchema,
)

router = APIRouter(prefix="/territory", tags=["territory"])

# ------------------------------------------------------------
# Lista de Distritos, Comunas y Diputados
# ------------------------------------------------------------
@router.get("/districts", response_model=List[DistrictWithCommunesAndMembersSchema])
def list_districts_with_communes_and_members(
    db: Session = Depends(get_db),
) -> List[DistrictWithCommunesAndMembersSchema]:
    districts = db.query(District).order_by(District.number.asc()).all()

    dc_rows = (
        db.query(DistrictCommune.district_id, Commune)
        .join(Commune, Commune.id == DistrictCommune.commune_id)
        .all()
    )
    communes_by_district: Dict[int, List[Commune]] = {}
    for d_id, c in dc_rows:
        communes_by_district.setdefault(d_id, []).append(c)

    mm_rows = (
        db.query(ParliamentMember.constituency, ParliamentMember)
        .filter(ParliamentMember.constituency.isnot(None))
        .all()
    )
    members_by_const: Dict[str, List[ParliamentMember]] = {}
    for const, m in mm_rows:
        members_by_const.setdefault(const, []).append(m)

    result: List[DistrictWithCommunesAndMembersSchema] = []
    for d in districts:
        key = str(d.number)
        communes = sorted(communes_by_district.get(d.id, []), key=lambda c: c.name or "")
        members = sorted(members_by_const.get(key, []), key=lambda m: (m.last_name or "", m.first_name or ""))
        result.append({"district": d, "communes": communes, "members": members})
    return result

# ------------------------------------------------------------
# Lista de Comunas
# ------------------------------------------------------------
@router.get("/communes", response_model=List[CommuneSchema])
def list_communes(db: Session = Depends(get_db)) -> List[Commune]:
    return db.query(Commune).order_by(Commune.id.asc()).all()

# ------------------------------------------------------------
# Detalle de Distrito con Comunas y Diputados
# ------------------------------------------------------------
@router.get("/districts/{district_id}", response_model=DistrictWithCommunesAndMembersSchema)
def get_district_with_communes_and_members(district_id: int, db: Session = Depends(get_db)):
    d = db.query(District).filter(District.id == district_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="District not found")

    communes = (
        db.query(Commune)
        .join(DistrictCommune, DistrictCommune.commune_id == Commune.id)
        .filter(DistrictCommune.district_id == district_id)
        .order_by(Commune.name.asc())
        .all()
    )

    members = (
        db.query(ParliamentMember)
        .filter(ParliamentMember.constituency == str(d.number))
        .order_by(ParliamentMember.last_name.asc(), ParliamentMember.first_name.asc())
        .all()
    )

    return {"district": d, "communes": communes, "members": members}