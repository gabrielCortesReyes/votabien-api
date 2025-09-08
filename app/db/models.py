# ============================
# MODELS
# ============================

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, DateTime, Boolean, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class ParliamentMember(Base):
    __tablename__ = "parliament_member"

    id = Column(Integer, primary_key=True, index=True)
    parlid = Column(Integer, unique=True, nullable=False)
    role = Column(String(10), nullable=False)

    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=False)
    second_last_name = Column(String(50), nullable=True)

    birth_date = Column(Date, nullable=True)
    gender = Column(String(10), nullable=False)
    region = Column(String(100), nullable=True)
    constituency = Column(String(10), nullable=True)

    party_id = Column(Integer, ForeignKey("party.id"), nullable=True)

    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    curriculum = Column(Text, nullable=True)

    parties = relationship("Party", secondary="party_membership", back_populates="members")
    

class Party(Base):
    __tablename__ = "party"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    abbreviation = Column(String(10), nullable=True)

    img_url = Column(String(200), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    members = relationship("ParliamentMember", secondary="party_membership", back_populates="parties")


class PartyMembership(Base):
    __tablename__ = "party_membership"

    id = Column(Integer, primary_key=True, index=True)
    parliament_member_id = Column(Integer, ForeignKey("parliament_member.id"), nullable=False)
    party_id = Column(Integer, ForeignKey("party.id"), nullable=False)
    
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("legislative_sessions.id", ondelete="NO ACTION"), nullable=False)
    parliament_member_id = Column(Integer, ForeignKey("parliament_member.id", ondelete="NO ACTION"), nullable=False)

    attendance_type = Column(String(50), nullable=False)
    justification = Column(String(255), nullable=True)

    reduces_attendance = Column(Boolean, nullable=True)
    reduces_quorum = Column(Boolean, nullable=True)

    member = relationship("ParliamentMember", backref="attendances")
    session = relationship("LegislativeSession", backref="attendances")


class LegislativeSession(Base):
    __tablename__ = "legislative_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_number = Column(Integer, nullable=False)

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)

    session_type = Column(String(50), nullable=False)   
    session_status = Column(String(50), nullable=False)


class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, nullable=False, unique=True)


class Commune(Base):
    __tablename__ = "communes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)


class DistrictCommune(Base):
    __tablename__ = "district_communes"
    __table_args__ = {"schema": "public"}
    
    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    commune_id = Column(Integer, ForeignKey("communes.id"), nullable=False)


class LawProject(Base):
    __tablename__ = "law_projects"
    __table_args__ = {"schema": "public"}
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False, unique=True)
    bulletin_number = Column(String(20), nullable=False) 
    name = Column(String, nullable=False)
    
    entry_date = Column(Date, nullable=False)
    initiative_type = Column(String(50), nullable=False)
    
    origin_chamber = Column(String(50), nullable=False)
    admissible = Column(Boolean, nullable=False)
    admission_date = Column(Date, nullable=True)
    chamber_origin = Column(String(50), nullable=True)

    votes = relationship("LawProjectVote", back_populates="project", lazy="selectin")
    vote_details = relationship(
        "LawProjectVoteDetail",
        secondary="public.law_project_votes",             
        primaryjoin="LawProject.id==LawProjectVote.law_project_id",
        secondaryjoin="LawProjectVote.id==LawProjectVoteDetail.vote_id",
        viewonly=True,
        lazy="selectin",
    )
    authors = relationship("LawProjectAuthor", back_populates="project", lazy="selectin")
    matters = relationship("LawProjectMatter", back_populates="project", lazy="selectin")
    ministries = relationship("LawProjectMinistry", back_populates="project", lazy="selectin")


class LawProjectVote(Base):
    __tablename__ = "law_project_votes"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    law_project_id = Column(Integer, ForeignKey("public.law_projects.id"), nullable=False)
    description = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False) 
   
    total_yes = Column(Integer, nullable=False)
    total_no = Column(Integer, nullable=False)
    total_abstention = Column(Integer, nullable=False)
    total_excused = Column(Integer, nullable=False)
    
    quorum = Column(String, nullable=False)
    result = Column(String, nullable=False)
    vote_type = Column(String, nullable=False)
    constitutional_stage = Column(String, nullable=True)
    
    regulatory_stage = Column(String, nullable=True) 
    article = Column(Text, nullable=True)
    type = Column(String(200), nullable=True)

    project = relationship("LawProject", back_populates="votes")
    details = relationship("LawProjectVoteDetail", back_populates="vote", lazy="selectin")


class LawProjectVoteDetail(Base):
    __tablename__ = "law_project_vote_details"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    vote_id = Column(Integer, ForeignKey("public.law_project_votes.id"), nullable=True)
    
    parliament_member_id = Column(Integer, ForeignKey("public.parliament_member.id"), nullable=True)
    vote_option = Column(String, nullable=False)

    vote = relationship("LawProjectVote", back_populates="details")


class LawProjectMinistry(Base):
    __tablename__ = "law_project_ministries"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    law_project_id = Column(Integer, ForeignKey("public.law_projects.id"), nullable=False)
    ministry_id = Column(Integer, ForeignKey("public.ministries.id"), nullable=False)

    project = relationship("LawProject", back_populates="ministries")


class LawProjectMatter(Base):
    __tablename__ = "law_project_matters"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    law_project_id = Column(Integer, ForeignKey("public.law_projects.id"), nullable=False)
    matter_id = Column(Integer, ForeignKey("public.matters.id"), nullable=False)

    project = relationship("LawProject", back_populates="matters")


class LawProjectAuthor(Base):
    __tablename__ = "law_project_authors"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    law_project_id = Column(Integer, ForeignKey("public.law_projects.id"), nullable=False)
    parliament_member_id = Column(Integer, ForeignKey("public.parliament_member.id"), nullable=False)

    project = relationship("LawProject", back_populates="authors")