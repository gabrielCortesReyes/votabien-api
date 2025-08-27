from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base

class Party(Base):
    __tablename__ = "party"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)

class ParliamentMember(Base):
    __tablename__ = "parliament_member"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String, index=True)
    party_id: Mapped[int | None] = mapped_column(ForeignKey("party.id"), nullable=True)
    district: Mapped[str | None] = mapped_column(String, nullable=True)

    party = relationship("Party", lazy="joined")

class LawProject(Base):
    __tablename__ = "law_projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[str | None] = mapped_column(String, index=True)  # ej: "Boletín 12345-06"
    name: Mapped[str] = mapped_column(String, index=True)
    admission_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    legislative_stage: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)  # "Aprobado", "En discusión", etc.
