# ============================
# MODELS
# ============================

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, DateTime, Boolean
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
    created_at = Column(Date, nullable=False)
    updated_at = Column(Date, nullable=False)

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
    session_id = Column(Integer, ForeignKey("legislative_session.id", ondelete="NO ACTION"), nullable=False)
    parliament_member_id = Column(Integer, ForeignKey("parliament_member.id", ondelete="NO ACTION"), nullable=False)

    attendance_type = Column(String(50), nullable=False)
    justification = Column(String(255), nullable=True)

    reduces_attendance = Column(Boolean, nullable=True)
    reduces_quorum = Column(Boolean, nullable=True)

    member = relationship("ParliamentMember", backref="attendances")
    session = relationship("LegislativeSession", backref="attendances")


class LegislativeSession(Base):
    __tablename__ = "legislative_session"

    id = Column(Integer, primary_key=True, index=True)
    session_number = Column(Integer, nullable=False)

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)

    session_type = Column(String(50), nullable=False)   
    session_status = Column(String(50), nullable=False)