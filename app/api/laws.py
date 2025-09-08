# ============================
# LAWS API
# ============================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.db.base import get_db
from app.db.models import (LawProject, LawProjectVote, LawProjectVoteDetail, LawProjectAuthor, LawProjectMatter, LawProjectMinistry)
from app.schemas.schemas import ( LawProjectWithVotesSchema, LawProjectDetailSchema)

router = APIRouter(prefix="/laws", tags=["laws"])

# ------------------------------------------------------------
# Proyecto + Votos
# ------------------------------------------------------------
@router.get("/{id}", response_model=LawProjectWithVotesSchema)
def get_law_project(id: int, db: Session = Depends(get_db)) -> LawProjectWithVotesSchema:
    proj = (
        db.query(LawProject)
        .options(selectinload(LawProject.votes))
        .filter(LawProject.id == id)
        .first()
    )
    if not proj:
        raise HTTPException(status_code=404, detail="Law project not found")

    return {"project": proj, "votes": proj.votes}

# ------------------------------------------------------------
# Proyecto + Detalle Completo
# ------------------------------------------------------------
@router.get("/{id}/detail", response_model=LawProjectDetailSchema)
def get_law_project_detail(id: int, db: Session = Depends(get_db)) -> LawProjectDetailSchema:
    proj = db.query(LawProject).filter(LawProject.id == id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Law project not found")

    votes = (
        db.query(LawProjectVote)
        .filter(LawProjectVote.law_project_id == id)
        .order_by(LawProjectVote.id.asc())
        .all()
    )
    vote_ids = [v.id for v in votes]

    vote_details = []
    if vote_ids:
        vote_details = (
            db.query(LawProjectVoteDetail)
            .filter(LawProjectVoteDetail.vote_id.in_(vote_ids))
            .order_by(LawProjectVoteDetail.id.asc())
            .all()
        )

    authors = (
        db.query(LawProjectAuthor)
        .filter(LawProjectAuthor.law_project_id == id)
        .order_by(LawProjectAuthor.id.asc())
        .all()
    )
    matters = (
        db.query(LawProjectMatter)
        .filter(LawProjectMatter.law_project_id == id)
        .order_by(LawProjectMatter.id.asc())
        .all()
    )
    ministries = (
        db.query(LawProjectMinistry)
        .filter(LawProjectMinistry.law_project_id == id)
        .order_by(LawProjectMinistry.id.asc())
        .all()
    )

    return {
        "project": proj,
        "authors": authors,
        "matters": matters,
        "ministries": ministries,
        "votes": votes,
        "vote_details": vote_details,
    }