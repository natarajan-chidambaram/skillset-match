from datetime import datetime, date, time
from typing import Any, List, Optional, Union, Set
from enum import Enum
from pydantic import BaseModel, field_validator


############################################
# Enumerations are defined here
############################################

class SkillRequestStatus(Enum):
    MATCHED = "MATCHED"
    OPEN = "OPEN"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class SessionType(Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    HYBRID = "HYBRID"

class UserSkillLevel(Enum):
    AUTHORITY = "AUTHORITY"
    COMPETENT = "COMPETENT"
    NOVICE = "NOVICE"
    EXPERT = "EXPERT"
    PROFICIENT = "PROFICIENT"

class TechSkillLevel(Enum):
    BEGINNER = "BEGINNER"
    ADVANCED = "ADVANCED"
    INTERMEDIATE = "INTERMEDIATE"
    EXPERT = "EXPERT"
    MASTERCLASS = "MASTERCLASS"

class SkillMatchStatus(Enum):
    COMPLETED = "COMPLETED"
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    REJECTED = "REJECTED"

############################################
# Classes are defined here
############################################
class SessionCreate(BaseModel):
    sessionType: SessionType
    duration: int
    sessionDate: date
    sessionId: int
    review: Optional[int] = None  # 1:1 Relationship (optional)
    skillmatch_1: int  # N:1 Relationship (mandatory)


class ReviewCreate(BaseModel):
    comments: str
    reviewId: int
    rating: int
    session_1: int  # 1:1 Relationship (mandatory)


class SkillMatchCreate(BaseModel):
    status: SkillMatchStatus
    matchId: int
    createdDate: date
    startDate: date
    skillrequest_1: Optional[List[int]] = None  # 1:N Relationship
    user_2: int  # N:1 Relationship (mandatory)
    session: Optional[List[int]] = None  # 1:N Relationship
    user_3: int  # N:1 Relationship (mandatory)


class SkillRequestCreate(BaseModel):
    requestId: int
    status: SkillRequestStatus
    createdDate: date
    deadlineDate: date
    skillmatch_2: Optional[int] = None  # N:1 Relationship (optional)
    skill_1: int  # N:1 Relationship (mandatory)
    user_1: int  # N:1 Relationship (mandatory)


class SkillCreate(BaseModel):
    skillName: str
    skillId: int
    description: str
    skillLevel: TechSkillLevel
    category: str
    userskill_1: Optional[List[int]] = None  # 1:N Relationship
    skillrequest_2: Optional[List[int]] = None  # 1:N Relationship


class UserSkillCreate(BaseModel):
    skillLevel: UserSkillLevel
    certification: bool
    yearsOfExperience: int
    skillId: int
    skill: int  # N:1 Relationship (mandatory)
    user: int  # N:1 Relationship (mandatory)


class UserCreate(BaseModel):
    userId: int
    userName: str
    emailId: str
    skillmatch: Optional[List[int]] = None  # 1:N Relationship
    skillrequest: Optional[List[int]] = None  # 1:N Relationship
    skillmatch_3: Optional[List[int]] = None  # 1:N Relationship
    userskill: Optional[List[int]] = None  # 1:N Relationship


