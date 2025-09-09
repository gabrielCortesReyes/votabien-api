# ============================
# LAWS API
# ============================

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, or_
from typing import Dict, Any, List, Optional

from app.db.base import get_db
from app.db.models import (
    LawProject, LawProjectVote, LawProjectVoteDetail, LawProjectAuthor, LawProjectMatter, LawProjectMinistry,
    ParliamentMember, PartyMembership, Party, Ministry, Matter)
from app.schemas.schemas import ( LawProjectWithVotesSchema, LawProjectDetailSchema, PaginatedLawProjectsSchema)

router = APIRouter(prefix="/laws", tags=["laws"])

# ------------------------------------------------------------
# Proyecto + Lista
# ------------------------------------------------------------
@router.get("/", response_model=PaginatedLawProjectsSchema)
def list_law_projects(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Página (1-based)"),
    size: int = Query(20, ge=1, le=100, description="Ítems por página"),
):

    total = db.query(func.count(LawProject.id)).scalar() or 0

    pages = (total + size - 1) // size if total else 0
    offset = (page - 1) * size

    items = (
        db.query(LawProject)
        .order_by(LawProject.entry_date.desc(), LawProject.id.desc())
        .limit(size)
        .offset(offset)
        .all()
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
    }

# ------------------------------------------------------------
# Proyecto + Votos
# ------------------------------------------------------------
@router.get("/{id}/detail")
def get_law_project_detail(id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    proj: Optional[LawProject] = (
        db.query(LawProject)
        .filter(LawProject.id == id)
        .first()
    )
    if not proj:
        raise HTTPException(status_code=404, detail="Law project not found")

    vote: Optional[LawProjectVote] = (
        db.query(LawProjectVote)
        .filter(LawProjectVote.law_project_id == id)
        .order_by(LawProjectVote.date.desc(), LawProjectVote.id.desc())
        .first()
    )
    if not vote:
        return {
            "proyecto": {
                "detail": {
                    "id": None,
                    "law_project_id": proj.id,
                    "description": None,
                    "date": None,
                    "total_yes": 0,
                    "total_no": 0,
                    "total_abstention": 0,
                    "total_excused": 0,
                    "quorum": None,
                    "result": None,
                    "vote_type": None,
                    "constitutional_stage": None,
                    "regulatory_stage": None,
                    "article": None,
                    "type": None,
                    "detalle": {
                        "votacion": [],
                        "authors": [],
                        "ministries": [],
                        "matters": [],
                    },
                }
            }
        }

    detail_rows: List[LawProjectVoteDetail] = (
        db.query(LawProjectVoteDetail)
        .filter(LawProjectVoteDetail.vote_id == vote.id)
        .order_by(LawProjectVoteDetail.id.asc())
        .all()
    )
    member_ids = [d.parliament_member_id for d in detail_rows if d.parliament_member_id]
    members_by_id: Dict[int, ParliamentMember] = {}
    party_by_member: Dict[int, Optional[str]] = {}

    if member_ids:
        members = db.query(ParliamentMember).filter(ParliamentMember.id.in_(member_ids)).all()
        members_by_id = {m.id: m for m in members}

        pm_rows = (
            db.query(PartyMembership, Party)
            .join(Party, Party.id == PartyMembership.party_id)
            .filter(PartyMembership.parliament_member_id.in_(member_ids))
            .order_by(
                PartyMembership.parliament_member_id.asc(),
                PartyMembership.end_date.isnot(None),
                PartyMembership.start_date.desc(),
            )
            .all()
        )
        seen = set()
        for pm, p in pm_rows:
            if pm.parliament_member_id in seen:
                continue
            party_by_member[pm.parliament_member_id] = p.abbreviation or p.name
            seen.add(pm.parliament_member_id)

    detalle_votacion = []
    for d in detail_rows:
        m = members_by_id.get(d.parliament_member_id) if d.parliament_member_id else None
        if m:
            full_name = " ".join(filter(None, [
                (m.first_name or "").strip(),
                (m.middle_name or "").strip(),
                (m.last_name or "").strip(),
                (m.second_last_name or "").strip(),
            ])).strip() or "N/D"
            party_name = party_by_member.get(m.id)
        else:
            full_name = "N/D"
            party_name = None

        detalle_votacion.append({
            "id": d.id,
            "name": full_name,
            "party": party_name,
            "vote": d.vote_option,
        })

    author_rows = (
        db.query(LawProjectAuthor, ParliamentMember)
        .join(ParliamentMember, ParliamentMember.id == LawProjectAuthor.parliament_member_id)
        .filter(LawProjectAuthor.law_project_id == id)
        .order_by(LawProjectAuthor.id.asc())
        .all()
    )

    author_ids = [pm.id for _, pm in author_rows]
    author_party: Dict[int, Optional[str]] = {}
    if author_ids:
        apm_rows = (
            db.query(PartyMembership, Party)
            .join(Party, Party.id == PartyMembership.party_id)
            .filter(PartyMembership.parliament_member_id.in_(author_ids))
            .order_by(
                PartyMembership.parliament_member_id.asc(),
                PartyMembership.end_date.isnot(None),
                PartyMembership.start_date.desc(),
            )
            .all()
        )
        seen = set()
        for pm, p in apm_rows:
            if pm.parliament_member_id in seen:
                continue
            author_party[pm.parliament_member_id] = p.abbreviation or p.name
            seen.add(pm.parliament_member_id)

    authors_detail = []
    for _, pm in author_rows:
        authors_detail.append({
            "id": pm.id,
            "parlid": pm.parlid,
            "role": pm.role,
            "first_name": pm.first_name,
            "middle_name": pm.middle_name,
            "last_name": pm.last_name,
            "second_last_name": pm.second_last_name,
            "birth_date": pm.birth_date.isoformat() if pm.birth_date else None,
            "gender": pm.gender,
            "region": pm.region,
            "constituency": pm.constituency,
            "party": author_party.get(pm.id),
            "phone": pm.phone,
            "email": pm.email,
            "curriculum": pm.curriculum,
        })

    ministries = (
        db.query(Ministry)
        .join(LawProjectMinistry, LawProjectMinistry.ministry_id == Ministry.id)
        .filter(LawProjectMinistry.law_project_id == proj.id)
        .order_by(Ministry.name.asc())
        .all()
    )
    matters = (
        db.query(Matter)
        .join(LawProjectMatter, LawProjectMatter.matter_id == Matter.id)
        .filter(LawProjectMatter.law_project_id == proj.id)
        .order_by(Matter.name.asc())
        .all()
    )

    return {
        "proyecto": {
            "detail": {
                "id": vote.id,
                "law_project_id": vote.law_project_id,
                "description": vote.description,
                "date": vote.date.isoformat() if vote.date else None,
                "total_yes": vote.total_yes,
                "total_no": vote.total_no,
                "total_abstention": vote.total_abstention,
                "total_excused": vote.total_excused,
                "quorum": vote.quorum,
                "result": vote.result,
                "vote_type": vote.vote_type,
                "constitutional_stage": vote.constitutional_stage,
                "regulatory_stage": vote.regulatory_stage,
                "article": vote.article,
                "type": vote.type,
                "detalle": {
                    "votacion": detalle_votacion,
                    "authors": authors_detail,
                    "ministries": [{"id": m.id, "name": m.name} for m in ministries],
                    "matters": [{"id": mt.id, "name": mt.name} for mt in matters],
                },
            }
        }
    }