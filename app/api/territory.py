from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import District, Commune, DistrictCommune
from app.schemas.schemas import ( 
    DistrictSchema, 
    CommuneSchema, 
    DistrictWithCommunesSchema,
)

router = APIRouter(prefix="/territory", tags=["territory"])

# ------------------------------------------------------------
# Lista de Distritos y Comunas
# ------------------------------------------------------------
@router.get("/districts", response_model=List[DistrictWithCommunesSchema])
def list_districts_with_communes(db: Session = Depends(get_db)) -> List[DistrictWithCommunesSchema]:
    districts = db.query(District).order_by(District.number.asc()).all()

    rows = (
        db.query(DistrictCommune.district_id, Commune)
        .join(Commune, Commune.id == DistrictCommune.commune_id)
        .all()
    )

    by_district: Dict[int, List[Commune]] = {}
    for d_id, commune in rows:
        by_district.setdefault(d_id, []).append(commune)

    result: List[DistrictWithCommunesSchema] = []
    for d in districts:
        communes = sorted(by_district.get(d.id, []), key=lambda c: c.name or "")
        result.append({"district": d, "communes": communes})
    return result

# ------------------------------------------------------------
# Lista de Comunas
# ------------------------------------------------------------
@router.get("/communes", response_model=List[CommuneSchema])
def list_communes(db: Session = Depends(get_db)) -> List[Commune]:
    return db.query(Commune).order_by(Commune.id.asc()).all()

# ------------------------------------------------------------
# Detalle de Distrito con Comunas
# ------------------------------------------------------------
@router.get("/districts/{district_id}", response_model=DistrictWithCommunesSchema)
def get_district_with_communes(district_id: int, db: Session = Depends(get_db)):
    d = db.query(District).filter(District.id == district_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="District not found")

    q = (
        db.query(Commune)
        .join(DistrictCommune, DistrictCommune.commune_id == Commune.id)
        .filter(DistrictCommune.district_id == district_id)
        .order_by(Commune.name.asc())
        .all()
    )
    return {"district": d, "communes": q}