from datetime import datetime, date, time
from typing import Any, List, Optional, Union, Set
from enum import Enum
from pydantic import BaseModel, field_validator


############################################
# Enumerations are defined here
############################################

############################################
# Classes are defined here
############################################
class SessionCreate(BaseModel):
    duration: int
    sessionId: int
    sessionDate: date
    sessionType: str
    skillmatch_1: int  # N:1 Relationship (mandatory)
    review: Optional[int] = None  # 1:1 Relationship (optional)


class ReviewCreate(BaseModel):
    reviewId: int
    comments: str
    rating: int
    session_1: int  # 1:1 Relationship (mandatory)


class SkillMatchCreate(BaseModel):
    status: int
    startDate: date
    createdDate: date
    matchId: int
    session: Optional[List[int]] = None  # 1:N Relationship
    user_3: int  # N:1 Relationship (mandatory)
    skillrequest_1: Optional[List[int]] = None  # 1:N Relationship
    user_2: int  # N:1 Relationship (mandatory)


class SkillRequestCreate(BaseModel):
    requestId: int
    status: int
    deadlineDate: date
    createdDate: date
    user_1: int  # N:1 Relationship (mandatory)
    skillmatch_2: int  # N:1 Relationship (mandatory)


class SkillCreate(BaseModel):
    category: str
    description: str
    skillName: str
    skillLevel: str
    skillId: int
    userskill_1: Optional[List[int]] = None  # 1:N Relationship


class UserSkillCreate(BaseModel):
    certification: bool
    yearsOfExperience: int
    skillId: int
    skillLevel: str
    skill: int  # N:1 Relationship (mandatory)
    user: int  # N:1 Relationship (mandatory)


class UserCreate(BaseModel):
    emailId: str
    userName: str
    userId: int
    skillrequest: Optional[List[int]] = None  # 1:N Relationship
    userskill: Optional[List[int]] = None  # 1:N Relationship
    skillmatch_3: Optional[List[int]] = None  # 1:N Relationship
    skillmatch: Optional[List[int]] = None  # 1:N Relationship


