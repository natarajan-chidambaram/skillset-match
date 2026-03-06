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
    sessionType: str
    sessionDate: date
    duration: int
    sessionId: int
    review: Optional[int] = None  # 1:1 Relationship (optional)
    skillmatch_1: int  # N:1 Relationship (mandatory)


class ReviewCreate(BaseModel):
    reviewId: int
    rating: int
    comments: str
    session_1: int  # 1:1 Relationship (mandatory)


class SkillMatchCreate(BaseModel):
    createdDate: date
    startDate: date
    matchId: int
    status: int
    user_3: int  # N:1 Relationship (mandatory)
    session: Optional[List[int]] = None  # 1:N Relationship


class SkillRequestCreate(BaseModel):
    requestId: int
    deadlineDate: date
    createdDate: date
    status: int
    user_2: int  # N:1 Relationship (mandatory)


class SkillCreate(BaseModel):
    category: str
    skillLevel: str
    skillId: int
    description: str
    skillName: str
    userskill_2: Optional[List[int]] = None  # 1:N Relationship


class UserSkillCreate(BaseModel):
    skillId: int
    skillLevel: str
    yearsOfExperience: int
    certification: bool
    user: int  # N:1 Relationship (mandatory)
    user_1: int  # N:1 Relationship (mandatory)
    skill: int  # N:1 Relationship (mandatory)


class UserCreate(BaseModel):
    userId: int
    emailId: str
    userName: str
    userskill: Optional[List[int]] = None  # 1:N Relationship
    skillrequest: Optional[List[int]] = None  # 1:N Relationship
    skillmatch: Optional[List[int]] = None  # 1:N Relationship
    userskill_1: Optional[List[int]] = None  # 1:N Relationship


