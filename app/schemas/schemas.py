# ============================
# SCHEMAS 
# ============================

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import List, Optional

app = FastAPI()

# ------------------------------------------------------------
# Parliament Member
# ------------------------------------------------------------
class ParliamentMemberSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    parlid: int
    role: str

    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    second_last_name: Optional[str] = None

    birth_date: Optional[date] = None 
    gender: str
    region: Optional[str] = None
    constituency: Optional[str] = None

    party_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    curriculum: Optional[str] = None

# ------------------------------------------------------------
# Party
# ------------------------------------------------------------
class PartySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    abbreviation: Optional[str] = None

    img_url: Optional[str] = None
    created_at: datetime  
    updated_at: datetime

# ------------------------------------------------------------
# Party Membership
# ------------------------------------------------------------
class PartyMembershipSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    parliament_member_id: int
    party_id: int

    start_date: datetime
    end_date: Optional[datetime] = None

# ------------------------------------------------------------
# Auxiliar (Membership info)
# ------------------------------------------------------------
class MembershipSchema(BaseModel):
    start_date: datetime
    end_date: Optional[datetime] = None

# ------------------------------------------------------------
# Esquemas Compuestos
# ------------------------------------------------------------
class PartyWithMembershipSchema(PartySchema):
    membership: Optional[MembershipSchema] = None

class MemberWithMembershipSchema(ParliamentMemberSchema):
    membership: Optional[MembershipSchema] = None

class MemberWithCurrentPartySchema(BaseModel):
    member: ParliamentMemberSchema
    party: Optional[PartyWithMembershipSchema] = None

class MemberWithAllPartiesSchema(BaseModel):
    member: ParliamentMemberSchema
    parties: List[PartyWithMembershipSchema]

class PartyWithMembersSchema(PartySchema):
    members: List[MemberWithMembershipSchema]

# ------------------------------------------------------------
# Attendance
# ------------------------------------------------------------
class AttendanceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: int
    parliament_member_id: int

    attendance_type: str
    justification: Optional[str] = None

    reduces_attendance: Optional[bool] = None
    reduces_quorum: Optional[bool] = None

# ------------------------------------------------------------
# Legislative Session
# ------------------------------------------------------------
class LegislativeSessionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_number: int
    start_date: datetime
    end_date: Optional[datetime] = None
    session_type: str
    session_status: str

# ------------------------------------------------------------
# Esquemas Compuestos: Sesión con asistencias
# ------------------------------------------------------------
class AttendanceWithMemberSchema(AttendanceSchema):
    member: ParliamentMemberSchema

class SessionWithAttendancesSchema(BaseModel):
    session: LegislativeSessionSchema
    attendances: List[AttendanceSchema]

class SessionWithAttendancesAndMembersSchema(BaseModel):
    session: LegislativeSessionSchema
    attendances: List[AttendanceWithMemberSchema]