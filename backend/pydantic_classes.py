from datetime import datetime, date, time
from typing import Any, List, Optional, Union, Set
from enum import Enum
from pydantic import BaseModel, field_validator


############################################
# Enumerations are defined here
############################################

class UserSkillLevel(Enum):
    PROFICIENT = "PROFICIENT"
    NOVICE = "NOVICE"
    AUTHORITY = "AUTHORITY"
    COMPETENT = "COMPETENT"
    EXPERT = "EXPERT"

class SkillMatchStatus(Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"

class SessionType(Enum):
    OFFLINE = "OFFLINE"
    HYBRID = "HYBRID"
    ONLINE = "ONLINE"

class TechSkillLevel(Enum):
    INTERMEDIATE = "INTERMEDIATE"
    EXPERT = "EXPERT"
    MASTERCLASS = "MASTERCLASS"
    BEGINNER = "BEGINNER"
    ADVANCED = "ADVANCED"

class SkillRequestStatus(Enum):
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    OPEN = "OPEN"
    MATCHED = "MATCHED"

############################################
# Classes are defined here
############################################
class SessionCreate(BaseModel):
    duration: int
    sessionId: int
    sessionDate: date
    sessionType: SessionType
    skillmatch_1: int  # N:1 Relationship (mandatory)
    review: Optional[int] = None  # 1:1 Relationship (optional)


class ReviewCreate(BaseModel):
    reviewId: int
    rating: int
    comments: str
    session_1: int  # 1:1 Relationship (mandatory)


class SkillMatchCreate(BaseModel):
    startDate: date
    createdDate: date
    status: SkillMatchStatus
    matchId: int
    user_2: int  # N:1 Relationship (mandatory)
    session: Optional[List[int]] = None  # 1:N Relationship
    skillrequest_1: Optional[List[int]] = None  # 1:N Relationship
    user_3: int  # N:1 Relationship (mandatory)


class SkillRequestCreate(BaseModel):
    deadlineDate: date
    status: SkillRequestStatus
    requestId: int
    createdDate: date
    skillmatch_2: Optional[int] = None  # N:1 Relationship (optional)
    skill_1: int  # N:1 Relationship (mandatory)
    user_1: int  # N:1 Relationship (mandatory)


class SkillCreate(BaseModel):
    skillLevel: TechSkillLevel
    estimatedDuration: int
    category: str
    skillName: str
    description: str
    skillId: int
    skillrequest_2: Optional[List[int]] = None  # 1:N Relationship
    userskill_1: Optional[List[int]] = None  # 1:N Relationship


class UserSkillCreate(BaseModel):
    certification: bool
    yearsOfExperience: int
    skillLevel: UserSkillLevel
    skill: int  # N:1 Relationship (mandatory)
    user: int  # N:1 Relationship (mandatory)


class UserCreate(BaseModel):
    userId: int
    emailId: str
    userName: str
    skillmatch: Optional[List[int]] = None  # 1:N Relationship
    userskill: Optional[List[int]] = None  # 1:N Relationship
    skillrequest: Optional[List[int]] = None  # 1:N Relationship
    skillmatch_3: Optional[List[int]] = None  # 1:N Relationship


