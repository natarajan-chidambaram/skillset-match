import enum
import os # for reading .env variable
from typing import List, Optional
from sqlalchemy import (
    create_engine, Column, ForeignKey, Table, Text, Boolean, String, Date, 
    Time, DateTime, Float, Integer, Enum
)
from sqlalchemy.orm import (
    column_property, DeclarativeBase, Mapped, mapped_column, relationship
)
from datetime import datetime as dt_datetime, time as dt_time, date as dt_date

class Base(DeclarativeBase):
    pass

# Definitions of Enumerations
class UserSkillLevel(enum.Enum):
    PROFICIENT = "PROFICIENT"
    NOVICE = "NOVICE"
    AUTHORITY = "AUTHORITY"
    COMPETENT = "COMPETENT"
    EXPERT = "EXPERT"

class SkillMatchStatus(enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"

class SessionType(enum.Enum):
    OFFLINE = "OFFLINE"
    HYBRID = "HYBRID"
    ONLINE = "ONLINE"

class TechSkillLevel(enum.Enum):
    INTERMEDIATE = "INTERMEDIATE"
    EXPERT = "EXPERT"
    MASTERCLASS = "MASTERCLASS"
    BEGINNER = "BEGINNER"
    ADVANCED = "ADVANCED"

class SkillRequestStatus(enum.Enum):
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    OPEN = "OPEN"
    MATCHED = "MATCHED"


# Tables definition for many-to-many relationships

# Tables definition
class Session(Base):
    __tablename__ = "session"
    id: Mapped[int] = mapped_column(primary_key=True)
    sessionId: Mapped[int] = mapped_column(Integer)
    sessionDate: Mapped[dt_date] = mapped_column(Date)
    duration: Mapped[int] = mapped_column(Integer)
    sessionType: Mapped[SessionType] = mapped_column(Enum(SessionType))
    skillmatch_1_id: Mapped[int] = mapped_column(ForeignKey("skillmatch.id"))

class Review(Base):
    __tablename__ = "review"
    id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(Integer)
    comments: Mapped[str] = mapped_column(String(100))
    session_1_id: Mapped[int] = mapped_column(ForeignKey("session.id"), unique=True)

class SkillMatch(Base):
    __tablename__ = "skillmatch"
    id: Mapped[int] = mapped_column(primary_key=True)
    createdDate: Mapped[dt_date] = mapped_column(Date)
    startDate: Mapped[dt_date] = mapped_column(Date)
    status: Mapped[SkillMatchStatus] = mapped_column(Enum(SkillMatchStatus))
    user_3_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user_2_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

class SkillRequest(Base):
    __tablename__ = "skillrequest"
    id: Mapped[int] = mapped_column(primary_key=True)
    createdDate: Mapped[dt_date] = mapped_column(Date)
    status: Mapped[SkillRequestStatus] = mapped_column(Enum(SkillRequestStatus))
    deadlineDate: Mapped[dt_date] = mapped_column(Date)
    user_1_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    skillmatch_2_id: Mapped[int] = mapped_column(ForeignKey("skillmatch.id"), nullable=True)
    skill_1_id: Mapped[int] = mapped_column(ForeignKey("skill.id"))

class Skill(Base):
    __tablename__ = "skill"
    id: Mapped[int] = mapped_column(primary_key=True)
    skillLevel: Mapped[TechSkillLevel] = mapped_column(Enum(TechSkillLevel))
    estimatedDuration: Mapped[int] = mapped_column(Integer)
    skillId: Mapped[int] = mapped_column(Integer)
    skillName: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(100))

class UserSkill(Base):
    __tablename__ = "userskill"
    id: Mapped[int] = mapped_column(primary_key=True)
    skillLevel: Mapped[UserSkillLevel] = mapped_column(Enum(UserSkillLevel))
    yearsOfExperience: Mapped[int] = mapped_column(Integer)
    certification: Mapped[bool] = mapped_column(Boolean)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skill.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column(Integer)
    userName: Mapped[str] = mapped_column(String(100))
    emailId: Mapped[str] = mapped_column(String(100))


#--- Relationships of the session table
Session.skillmatch_1: Mapped["SkillMatch"] = relationship("SkillMatch", back_populates="session", foreign_keys=[Session.skillmatch_1_id])
Session.review: Mapped["Review"] = relationship("Review", back_populates="session_1", foreign_keys=[Review.session_1_id])

#--- Relationships of the review table
Review.session_1: Mapped["Session"] = relationship("Session", back_populates="review", foreign_keys=[Review.session_1_id])

#--- Relationships of the skillmatch table
SkillMatch.user_3: Mapped["User"] = relationship("User", back_populates="skillmatch_3", foreign_keys=[SkillMatch.user_3_id])
SkillMatch.user_2: Mapped["User"] = relationship("User", back_populates="skillmatch", foreign_keys=[SkillMatch.user_2_id])
SkillMatch.skillrequest_1: Mapped[List["SkillRequest"]] = relationship("SkillRequest", back_populates="skillmatch_2", foreign_keys=[SkillRequest.skillmatch_2_id])
SkillMatch.session: Mapped[List["Session"]] = relationship("Session", back_populates="skillmatch_1", foreign_keys=[Session.skillmatch_1_id])

#--- Relationships of the skillrequest table
SkillRequest.user_1: Mapped["User"] = relationship("User", back_populates="skillrequest", foreign_keys=[SkillRequest.user_1_id])
SkillRequest.skillmatch_2: Mapped["SkillMatch"] = relationship("SkillMatch", back_populates="skillrequest_1", foreign_keys=[SkillRequest.skillmatch_2_id])
SkillRequest.skill_1: Mapped["Skill"] = relationship("Skill", back_populates="skillrequest_2", foreign_keys=[SkillRequest.skill_1_id])

#--- Relationships of the skill table
Skill.skillrequest_2: Mapped[List["SkillRequest"]] = relationship("SkillRequest", back_populates="skill_1", foreign_keys=[SkillRequest.skill_1_id])
Skill.userskill_1: Mapped[List["UserSkill"]] = relationship("UserSkill", back_populates="skill", foreign_keys=[UserSkill.skill_id])

#--- Relationships of the userskill table
UserSkill.skill: Mapped["Skill"] = relationship("Skill", back_populates="userskill_1", foreign_keys=[UserSkill.skill_id])
UserSkill.user: Mapped["User"] = relationship("User", back_populates="userskill", foreign_keys=[UserSkill.user_id])

#--- Relationships of the user table
User.skillmatch: Mapped[List["SkillMatch"]] = relationship("SkillMatch", back_populates="user_2", foreign_keys=[SkillMatch.user_2_id])
User.userskill: Mapped[List["UserSkill"]] = relationship("UserSkill", back_populates="user", foreign_keys=[UserSkill.user_id])
User.skillrequest: Mapped[List["SkillRequest"]] = relationship("SkillRequest", back_populates="user_1", foreign_keys=[SkillRequest.user_1_id])
User.skillmatch_3: Mapped[List["SkillMatch"]] = relationship("SkillMatch", back_populates="user_3", foreign_keys=[SkillMatch.user_3_id])

# Database connection
DATABASE_URL = "sqlite:///Class_Diagram.db"  # SQLite connection
engine = create_engine(os.getenv("DATABASE_URL"))

# Create tables in the database
Base.metadata.create_all(engine, checkfirst=True)