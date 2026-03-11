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
class SkillRequestCreate(BaseModel):
    deadlineDate: date
    createdDate: date
    status: int
    requestId: int
    user_1: int  # N:1 Relationship (mandatory)
    skillmatch_2: Optional[int] = None  # N:1 Relationship (optional)


class SkillCreate(BaseModel):
    skillName: str
    skillId: int
    category: str
    skillLevel: str
    description: str
    userskill_1: Optional[List[int]] = None  # 1:N Relationship


class UserSkillCreate(BaseModel):
    skillId: int
    yearsOfExperience: int
    certification: bool
    skillLevel: str
    user: int  # N:1 Relationship (mandatory)
    skill: int  # N:1 Relationship (mandatory)


class UserCreate(BaseModel):
    userName: str
    emailId: str
    userId: int
    skillmatch_3: Optional[List[int]] = None  # 1:N Relationship
    skillrequest: Optional[List[int]] = None  # 1:N Relationship
    userskill: Optional[List[int]] = None  # 1:N Relationship
    skillmatch: Optional[List[int]] = None  # 1:N Relationship


class SessionCreate(BaseModel):
    sessionType: str
    sessionId: int
    duration: int
    sessionDate: date
    review: Optional[int] = None  # 1:1 Relationship (optional)
    skillmatch_1: int  # N:1 Relationship (mandatory)


class ReviewCreate(BaseModel):
    comments: str
    rating: int
    reviewId: int
    session_1: int  # 1:1 Relationship (mandatory)


class SkillMatchCreate(BaseModel):
    status: int
    matchId: int
    startDate: date
    createdDate: date
    skillrequest_1: Optional[List[int]] = None  # 1:N Relationship
    user_3: int  # N:1 Relationship (mandatory)
    user_2: int  # N:1 Relationship (mandatory)
    session: Optional[List[int]] = None  # 1:N Relationship


