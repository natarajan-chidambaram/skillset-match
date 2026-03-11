from datetime import datetime, date, time
from typing import Any, List, Optional, Union, Set
from enum import Enum
from pydantic import BaseModel, field_validator


############################################
# Enumerations are defined here
############################################

class SkillMatchStatus(Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"

class SessionType(Enum):
    HYBRID = "HYBRID"
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"

class TechSkillLevel(Enum):
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"
    BEGINNER = "BEGINNER"
    MASTERCLASS = "MASTERCLASS"

class SkillRequestStatus(Enum):
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    OPEN = "OPEN"
    MATCHED = "MATCHED"

class UserSkillLevel(Enum):
    NOVICE = "NOVICE"
    COMPETENT = "COMPETENT"
    EXPERT = "EXPERT"
    AUTHORITY = "AUTHORITY"
    PROFICIENT = "PROFICIENT"

############################################
# Classes are defined here
############################################
class SessionCreate(BaseModel):
    duration: int
    sessionDate: date
    sessionId: int
    sessionType: SessionType
    skillmatch_1: int  # N:1 Relationship (mandatory)
    review: Optional[int] = None  # 1:1 Relationship (optional)


class ReviewCreate(BaseModel):
    reviewId: int
    rating: int
    comments: str
    session_1: int  # 1:1 Relationship (mandatory)


class SkillMatchCreate(BaseModel):
    createdDate: date
    status: SkillMatchStatus
    matchId: int
    startDate: date
    session: Optional[List[int]] = None  # 1:N Relationship
    skillrequest_1: Optional[List[int]] = None  # 1:N Relationship
    user_2: int  # N:1 Relationship (mandatory)
    user_3: int  # N:1 Relationship (mandatory)


class SkillRequestCreate(BaseModel):
    status: SkillRequestStatus
    requestId: int
    createdDate: date
    deadlineDate: date
    user_1: int  # N:1 Relationship (mandatory)
    skill_1: int  # N:1 Relationship (mandatory)
    skillmatch_2: Optional[int] = None  # N:1 Relationship (optional)


class SkillCreate(BaseModel):
    category: str
    skillId: int
    skillLevel: TechSkillLevel
    skillName: str
    description: str
    skillrequest_2: Optional[List[int]] = None  # 1:N Relationship
    userskill_1: Optional[List[int]] = None  # 1:N Relationship


class UserSkillCreate(BaseModel):
    certification: bool
    skillId: int
    skillLevel: UserSkillLevel
    yearsOfExperience: int
    user: int  # N:1 Relationship (mandatory)
    skill: int  # N:1 Relationship (mandatory)


class UserCreate(BaseModel):
    userName: str
    userId: int
    emailId: str
    skillrequest: Optional[List[int]] = None  # 1:N Relationship
    skillmatch: Optional[List[int]] = None  # 1:N Relationship
    userskill: Optional[List[int]] = None  # 1:N Relationship
    skillmatch_3: Optional[List[int]] = None  # 1:N Relationship


