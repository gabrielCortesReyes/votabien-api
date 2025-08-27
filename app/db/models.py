from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
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
    
class Party(Base):
    __tablename__ = "party"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    abbreviation = Column(String(10), nullable=True)

    img_url = Column(String(200), nullable=True)
    created_at = Column(Date, nullable=False)
    updated_at = Column(Date, nullable=False)

