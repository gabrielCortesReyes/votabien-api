# ============================
# SCHEMAS 
# ============================

from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import List, Optional
from math import ceil

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
# Esquemas Compuestos: Sesión con Asistencias
# ------------------------------------------------------------
class AttendanceWithMemberSchema(AttendanceSchema):
    member: ParliamentMemberSchema


class SessionWithAttendancesAndMembersSchema(BaseModel):
    session: LegislativeSessionSchema
    attendances: List[AttendanceWithMemberSchema]

# ------------------------------------------------------------
# Resumen de Asistencias por Diputado
# ------------------------------------------------------------
class AttendanceResumeSchema(BaseModel):
    total_sessions: int
    attendance: int
    absence: int
    attendance_percentage: float

# ------------------------------------------------------------
# Esquema Compuesto: Diputado + Resumen + Detalle
# ------------------------------------------------------------
class MemberAttendanceResponseSchema(BaseModel):
    member: ParliamentMemberSchema
    resume: AttendanceResumeSchema
    detail: List[AttendanceSchema]

# ------------------------------------------------------------
# District and Communes
# ------------------------------------------------------------
class DistrictSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    number: int


class CommuneSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class DistrictWithCommunesAndMembersSchema(BaseModel):
    district: "DistrictSchema"
    communes: List["CommuneSchema"]
    members: List["ParliamentMemberSchema"]

# ------------------------------------------------------------
# Law Project
# ------------------------------------------------------------
class LawProjectSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    project_id: int
    bulletin_number: str
    name: str
    entry_date: date
    
    initiative_type: str
    origin_chamber: str
    admissible: bool
    admission_date: Optional[date] = None
    chamber_origin: Optional[str] = None


class LawProjectVoteSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    law_project_id: int
    description: str
    date: datetime
    
    total_yes: int
    total_no: int
    total_abstention: int
    total_excused: int
    
    quorum: str
    result: str
    vote_type: str
    constitutional_stage: Optional[str] = None
    
    regulatory_stage: Optional[str] = None
    article: Optional[str] = None
    type: Optional[str] = None


class LawProjectVoteDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    vote_id: Optional[int] = None
    parliament_member_id: Optional[int] = None
    vote_option: str


class LawProjectAuthorSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    law_project_id: int
    parliament_member_id: int


class LawProjectMatterSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    law_project_id: int
    matter_id: int


class LawProjectMinistrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    law_project_id: int
    ministry_id: int


class PaginatedLawProjectsSchema(BaseModel):
    items: List[LawProjectSchema]
    total: int
    page: int
    size: int
    pages: int

# ------------------------------------------------------------
# Esquema Compuesto: Ley, Votaciones y Detalles
# ------------------------------------------------------------
class LawProjectWithVotesSchema(BaseModel):
    project: LawProjectSchema
    votes: List[LawProjectVoteSchema]


class LawProjectDetailSchema(BaseModel):
    project: LawProjectSchema
    authors: List[LawProjectAuthorSchema]
    matters: List[LawProjectMatterSchema]
    
    ministries: List[LawProjectMinistrySchema]
    votes: List[LawProjectVoteSchema]
    vote_details: List[LawProjectVoteDetailSchema]

# ------------------------------------------------------------
# Ministry + Matter
# ------------------------------------------------------------
class MinistrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class MatterSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: Optional[str] = None

# ------------------------------------------------------------
# Vote Detail
# ------------------------------------------------------------
class VoteDetailHumanSchema(BaseModel):
    id: int
    name: str
    party: Optional[str] = None
    vote: str