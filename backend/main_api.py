import uvicorn
import os, json
import time as time_module
import logging
from fastapi import Depends, FastAPI, HTTPException, Request, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic_classes import *
from sql_alchemy import *
from matching_service import router as matching_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

############################################
#
#   Initialize the database
#
############################################

def init_db():
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/Class_Diagram.db")
    # Ensure local SQLite directory exists (safe no-op for other DBs)

    if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
        os.makedirs("data", exist_ok=True)
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False},
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=False
        )
    else:
        if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
            SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=False
        )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return SessionLocal

app = FastAPI(
    title="Class_Diagram API",
    description="Auto-generated REST API with full CRUD operations, relationship management, and advanced features",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "System", "description": "System health and statistics"},
        {"name": "Session", "description": "Operations for Session entities"},
        {"name": "Session Relationships", "description": "Manage Session relationships"},
        {"name": "Review", "description": "Operations for Review entities"},
        {"name": "Review Relationships", "description": "Manage Review relationships"},
        {"name": "SkillMatch", "description": "Operations for SkillMatch entities"},
        {"name": "SkillMatch Relationships", "description": "Manage SkillMatch relationships"},
        {"name": "SkillRequest", "description": "Operations for SkillRequest entities"},
        {"name": "SkillRequest Relationships", "description": "Manage SkillRequest relationships"},
        {"name": "Skill", "description": "Operations for Skill entities"},
        {"name": "Skill Relationships", "description": "Manage Skill relationships"},
        {"name": "UserSkill", "description": "Operations for UserSkill entities"},
        {"name": "UserSkill Relationships", "description": "Manage UserSkill relationships"},
        {"name": "User", "description": "Operations for User entities"},
        {"name": "User Relationships", "description": "Manage User relationships"},
    ]
)

app.include_router(matching_router)

# Enable CORS for all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

############################################
#
#   Middleware
#
############################################

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and responses."""
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to all responses."""
    start_time = time_module.time()
    response = await call_next(request)
    process_time = time_module.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

############################################
#
#   Exception Handlers
#
############################################

# Global exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Bad Request",
            "message": str(exc),
            "detail": "Invalid input data provided"
        }
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors."""
    logger.error(f"Database integrity error: {exc}")

    # Extract more detailed error information
    error_detail = str(exc.orig) if hasattr(exc, 'orig') else str(exc)

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "Conflict",
            "message": "Data conflict occurred",
            "detail": error_detail
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """Handle general SQLAlchemy errors."""
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "Database operation failed",
            "detail": "An internal database error occurred"
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else "HTTP Error",
            "message": exc.detail,
            "detail": f"HTTP {exc.status_code} error occurred"
        }
    )

# Initialize database session
SessionLocal = init_db()
# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        logger.error("Database session rollback due to exception")
        raise
    finally:
        db.close()

############################################
#
#   Global API endpoints
#
############################################

@app.get("/", tags=["System"])
def root():
    """Root endpoint - API information"""
    return {
        "name": "Class_Diagram API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint for monitoring"""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected"
    }


@app.get("/statistics", tags=["System"])
def get_statistics(database: DBSession = Depends(get_db)):
    """Get database statistics for all entities"""
    stats = {}
    stats["session_count"] = database.query(Session).count()
    stats["review_count"] = database.query(Review).count()
    stats["skillmatch_count"] = database.query(SkillMatch).count()
    stats["skillrequest_count"] = database.query(SkillRequest).count()
    stats["skill_count"] = database.query(Skill).count()
    stats["userskill_count"] = database.query(UserSkill).count()
    stats["user_count"] = database.query(User).count()
    stats["total_entities"] = sum(stats.values())
    return stats


############################################
#
#   BESSER Action Language standard lib
#
############################################


async def BAL_size(sequence:list) -> int:
    return len(sequence)

async def BAL_is_empty(sequence:list) -> bool:
    return len(sequence) == 0

async def BAL_add(sequence:list, elem) -> None:
    sequence.append(elem)

async def BAL_remove(sequence:list, elem) -> None:
    sequence.remove(elem)

async def BAL_contains(sequence:list, elem) -> bool:
    return elem in sequence

async def BAL_filter(sequence:list, predicate) -> list:
    return [elem for elem in sequence if predicate(elem)]

async def BAL_forall(sequence:list, predicate) -> bool:
    for elem in sequence:
        if not predicate(elem):
            return False
    return True

async def BAL_exists(sequence:list, predicate) -> bool:
    for elem in sequence:
        if predicate(elem):
            return True
    return False

async def BAL_one(sequence:list, predicate) -> bool:
    found = False
    for elem in sequence:
        if predicate(elem):
            if found:
                return False
            found = True
    return found

async def BAL_is_unique(sequence:list, mapping) -> bool:
    mapped = [mapping(elem) for elem in sequence]
    return len(set(mapped)) == len(mapped)

async def BAL_map(sequence:list, mapping) -> list:
    return [mapping(elem) for elem in sequence]

async def BAL_reduce(sequence:list, reduce_fn, aggregator) -> any:
    for elem in sequence:
        aggregator = reduce_fn(aggregator, elem)
    return aggregator


############################################
#
#   Session functions
#
############################################

@app.get("/session/", response_model=None, tags=["Session"])
def get_all_session(detailed: bool = False, database: DBSession = Depends(get_db)) -> list:
    from sqlalchemy.orm import joinedload

    # Use detailed=true to get entities with eagerly loaded relationships (for tables with lookup columns)
    if detailed:
        # Eagerly load all relationships to avoid N+1 queries
        query = database.query(Session)
        query = query.options(joinedload(Session.skillmatch_1))
        query = query.options(joinedload(Session.review))
        session_list = query.all()

        # Serialize with relationships included
        result = []
        for session_item in session_list:
            item_dict = session_item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)

            # Add many-to-one relationships (foreign keys for lookup columns)
            if session_item.skillmatch_1:
                related_obj = session_item.skillmatch_1
                related_dict = related_obj.__dict__.copy()
                related_dict.pop('_sa_instance_state', None)
                item_dict['skillmatch_1'] = related_dict
            else:
                item_dict['skillmatch_1'] = None
            if session_item.review:
                related_obj = session_item.review
                related_dict = related_obj.__dict__.copy()
                related_dict.pop('_sa_instance_state', None)
                item_dict['review'] = related_dict
            else:
                item_dict['review'] = None


            result.append(item_dict)
        return result
    else:
        # Default: return flat entities (faster for charts/widgets without lookup columns)
        return database.query(Session).all()


@app.get("/session/count/", response_model=None, tags=["Session"])
def get_count_session(database: DBSession = Depends(get_db)) -> dict:
    """Get the total count of Session entities"""
    count = database.query(Session).count()
    return {"count": count}


@app.get("/session/paginated/", response_model=None, tags=["Session"])
def get_paginated_session(skip: int = 0, limit: int = 100, detailed: bool = False, database: DBSession = Depends(get_db)) -> dict:
    """Get paginated list of Session entities"""
    total = database.query(Session).count()
    session_list = database.query(Session).offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": session_list
    }


@app.get("/session/search/", response_model=None, tags=["Session"])
def search_session(
    database: DBSession = Depends(get_db)
) -> list:
    """Search Session entities by attributes"""
    query = database.query(Session)


    results = query.all()
    return results


@app.get("/session/{session_id}/", response_model=None, tags=["Session"])
async def get_session(session_id: int, database: DBSession = Depends(get_db)) -> Session:
    db_session = database.query(Session).filter(Session.id == session_id).first()
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    response_data = {
        "session": db_session,
}
    return response_data



@app.post("/session/", response_model=None, tags=["Session"])
async def create_session(session_data: SessionCreate = Body(alias="params", embed=True), database: DBSession = Depends(get_db)) -> Session:

    if session_data.skillmatch_1 is not None:
        db_skillmatch_1 = database.query(SkillMatch).filter(SkillMatch.id == session_data.skillmatch_1).first()
        if not db_skillmatch_1:
            raise HTTPException(status_code=400, detail="SkillMatch not found")
    else:
        raise HTTPException(status_code=400, detail="SkillMatch ID is required")

    db_session = Session(
        duration=session_data.duration,        sessionId=session_data.sessionId,        sessionDate=session_data.sessionDate,        sessionType=session_data.sessionType.value,        skillmatch_1_id=session_data.skillmatch_1        )

    database.add(db_session)
    database.commit()
    database.refresh(db_session)




    return db_session


@app.post("/session/bulk/", response_model=None, tags=["Session"])
async def bulk_create_session(items: list[SessionCreate], database: DBSession = Depends(get_db)) -> dict:
    """Create multiple Session entities at once"""
    created_items = []
    errors = []

    for idx, item_data in enumerate(items):
        try:
            # Basic validation for each item
            if not item_data.skillmatch_1:
                raise ValueError("SkillMatch ID is required")

            db_session = Session(
                duration=item_data.duration,                sessionId=item_data.sessionId,                sessionDate=item_data.sessionDate,                sessionType=item_data.sessionType.value,                skillmatch_1_id=item_data.skillmatch_1            )
            database.add(db_session)
            database.flush()  # Get ID without committing
            created_items.append(db_session.id)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})

    if errors:
        database.rollback()
        raise HTTPException(status_code=400, detail={"message": "Bulk creation failed", "errors": errors})

    database.commit()
    return {
        "created_count": len(created_items),
        "created_ids": created_items,
        "message": f"Successfully created {len(created_items)} Session entities"
    }


@app.delete("/session/bulk/", response_model=None, tags=["Session"])
async def bulk_delete_session(ids: list[int], database: DBSession = Depends(get_db)) -> dict:
    """Delete multiple Session entities at once"""
    deleted_count = 0
    not_found = []

    for item_id in ids:
        db_session = database.query(Session).filter(Session.id == item_id).first()
        if db_session:
            database.delete(db_session)
            deleted_count += 1
        else:
            not_found.append(item_id)

    database.commit()

    return {
        "deleted_count": deleted_count,
        "not_found": not_found,
        "message": f"Successfully deleted {deleted_count} Session entities"
    }

@app.put("/session/{session_id}/", response_model=None, tags=["Session"])
async def update_session(session_id: int, session_data: SessionCreate  = Body(alias="params", embed=True), database: DBSession = Depends(get_db)) -> Session:
    db_session = database.query(Session).filter(Session.id == session_id).first()
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    setattr(db_session, 'duration', session_data.duration)
    setattr(db_session, 'sessionId', session_data.sessionId)
    setattr(db_session, 'sessionDate', session_data.sessionDate)
    setattr(db_session, 'sessionType', session_data.sessionType.value)
    if session_data.skillmatch_1 is not None:
        db_skillmatch_1 = database.query(SkillMatch).filter(SkillMatch.id == session_data.skillmatch_1).first()
        if not db_skillmatch_1:
            raise HTTPException(status_code=400, detail="SkillMatch not found")
        setattr(db_session, 'skillmatch_1_id', session_data.skillmatch_1)
    database.commit()
    database.refresh(db_session)

    return db_session


@app.delete("/session/{session_id}/", response_model=None, tags=["Session"])
async def delete_session(session_id: int, database: DBSession = Depends(get_db)):
    db_session = database.query(Session).filter(Session.id == session_id).first()
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    database.delete(db_session)
    database.commit()
    return db_session





############################################
#
#   Review functions
#
############################################

@app.get("/review/", response_model=None, tags=["Review"])
def get_all_review(detailed: bool = False, database: DBSession = Depends(get_db)) -> list:
    from sqlalchemy.orm import joinedload

    # Use detailed=true to get entities with eagerly loaded relationships (for tables with lookup columns)
    if detailed:
        # Eagerly load all relationships to avoid N+1 queries
        query = database.query(Review)
        query = query.options(joinedload(Review.session_1))
        review_list = query.all()

        # Serialize with relationships included
        result = []
        for review_item in review_list:
            item_dict = review_item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)

            # Add many-to-one relationships (foreign keys for lookup columns)
            if review_item.session_1:
                related_obj = review_item.session_1
                related_dict = related_obj.__dict__.copy()
                related_dict.pop('_sa_instance_state', None)
                item_dict['session_1'] = related_dict
            else:
                item_dict['session_1'] = None


            result.append(item_dict)
        return result
    else:
        # Default: return flat entities (faster for charts/widgets without lookup columns)
        return database.query(Review).all()


@app.get("/review/count/", response_model=None, tags=["Review"])
def get_count_review(database: DBSession = Depends(get_db)) -> dict:
    """Get the total count of Review entities"""
    count = database.query(Review).count()
    return {"count": count}


@app.get("/review/paginated/", response_model=None, tags=["Review"])
def get_paginated_review(skip: int = 0, limit: int = 100, detailed: bool = False, database: DBSession = Depends(get_db)) -> dict:
    """Get paginated list of Review entities"""
    total = database.query(Review).count()
    review_list = database.query(Review).offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": review_list
    }


@app.get("/review/search/", response_model=None, tags=["Review"])
def search_review(
    database: DBSession = Depends(get_db)
) -> list:
    """Search Review entities by attributes"""
    query = database.query(Review)


    results = query.all()
    return results


@app.get("/review/{review_id}/", response_model=None, tags=["Review"])
async def get_review(review_id: int, database: DBSession = Depends(get_db)) -> Review:
    db_review = database.query(Review).filter(Review.id == review_id).first()
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")

    response_data = {
        "review": db_review,
}
    return response_data



@app.post("/review/", response_model=None, tags=["Review"])
async def create_review(review_data: ReviewCreate = Body(alias="params", embed=True), database: DBSession = Depends(get_db)) -> Review:

    if review_data.session_1 is not None:
        db_session_1 = database.query(Session).filter(Session.id == review_data.session_1).first()
        if not db_session_1:
            raise HTTPException(status_code=400, detail="Session not found")
    else:
        raise HTTPException(status_code=400, detail="Session ID is required")

    db_review = Review(
        rating=review_data.rating,        comments=review_data.comments,        session_1_id=review_data.session_1        )

    database.add(db_review)
    database.commit()
    database.refresh(db_review)




    return db_review


@app.post("/review/bulk/", response_model=None, tags=["Review"])
async def bulk_create_review(items: list[ReviewCreate], database: DBSession = Depends(get_db)) -> dict:
    """Create multiple Review entities at once"""
    created_items = []
    errors = []

    for idx, item_data in enumerate(items):
        try:
            # Basic validation for each item
            if not item_data.session_1:
                raise ValueError("Session ID is required")

            db_review = Review(
                rating=item_data.rating,                comments=item_data.comments,                session_1_id=item_data.session_1            )
            database.add(db_review)
            database.flush()  # Get ID without committing
            created_items.append(db_review.id)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})

    if errors:
        database.rollback()
        raise HTTPException(status_code=400, detail={"message": "Bulk creation failed", "errors": errors})

    database.commit()
    return {
        "created_count": len(created_items),
        "created_ids": created_items,
        "message": f"Successfully created {len(created_items)} Review entities"
    }


@app.delete("/review/bulk/", response_model=None, tags=["Review"])
async def bulk_delete_review(ids: list[int], database: DBSession = Depends(get_db)) -> dict:
    """Delete multiple Review entities at once"""
    deleted_count = 0
    not_found = []

    for item_id in ids:
        db_review = database.query(Review).filter(Review.id == item_id).first()
        if db_review:
            database.delete(db_review)
            deleted_count += 1
        else:
            not_found.append(item_id)

    database.commit()

    return {
        "deleted_count": deleted_count,
        "not_found": not_found,
        "message": f"Successfully deleted {deleted_count} Review entities"
    }

@app.put("/review/{review_id}/", response_model=None, tags=["Review"])
async def update_review(review_id: int, review_data: ReviewCreate  = Body(alias="params", embed=True), database: DBSession = Depends(get_db)) -> Review:
    db_review = database.query(Review).filter(Review.id == review_id).first()
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")

    setattr(db_review, 'rating', review_data.rating)
    setattr(db_review, 'comments', review_data.comments)
    if review_data.session_1 is not None:
        db_session_1 = database.query(Session).filter(Session.id == review_data.session_1).first()
        if not db_session_1:
            raise HTTPException(status_code=400, detail="Session not found")
        setattr(db_review, 'session_1_id', review_data.session_1)
    database.commit()
    database.refresh(db_review)

    return db_review


@app.delete("/review/{review_id}/", response_model=None, tags=["Review"])
async def delete_review(review_id: int, database: DBSession = Depends(get_db)):
    db_review = database.query(Review).filter(Review.id == review_id).first()
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    database.delete(db_review)
    database.commit()
    return db_review





############################################
#
#   SkillMatch functions
#
############################################

@app.get("/skillmatch/", response_model=None, tags=["SkillMatch"])
def get_all_skillmatch(detailed: bool = False, database: DBSession = Depends(get_db)) -> list:
    from sqlalchemy.orm import joinedload

    # Use detailed=true to get entities with eagerly loaded relationships (for tables with lookup columns)
    if detailed:
        # Eagerly load all relationships to avoid N+1 queries
        query = database.query(SkillMatch)
        query = query.options(joinedload(SkillMatch.user_2))
        query = query.options(joinedload(SkillMatch.user_3))
        skillmatch_list = query.all()

        # Serialize with relationships included
        result = []
        for skillmatch_item in skillmatch_list:
            item_dict = skillmatch_item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)

            # Add many-to-one relationships (foreign keys for lookup columns)
            if skillmatch_item.user_2:
                related_obj = skillmatch_item.user_2
                related_dict = related_obj.__dict__.copy()
                related_dict.pop('_sa_instance_state', None)
                item_dict['user_2'] = related_dict
            else:
                item_dict['user_2'] = None
            if skillmatch_item.user_3:
                related_obj = skillmatch_item.user_3
                related_dict = related_obj.__dict__.copy()
                related_dict.pop('_sa_instance_state', None)
                item_dict['user_3'] = related_dict
            else:
                item_dict['user_3'] = None

            # Add many-to-many and one-to-many relationship objects (full details)
            session_list = database.query(Session).filter(Session.skillmatch_1_id == skillmatch_item.id).all()
            item_dict['session'] = []
            for session_obj in session_list:
                session_dict = session_obj.__dict__.copy()
                session_dict.pop('_sa_instance_state', None)
                item_dict['session'].append(session_dict)
            skillrequest_list = database.query(SkillRequest).filter(SkillRequest.skillmatch_2_id == skillmatch_item.id).all()
            item_dict['skillrequest_1'] = []
            for skillrequest_obj in skillrequest_list:
                skillrequest_dict = skillrequest_obj.__dict__.copy()
                skillrequest_dict.pop('_sa_instance_state', None)
                item_dict['skillrequest_1'].append(skillrequest_dict)

            result.append(item_dict)
        return result
    else:
        # Default: return flat entities (faster for charts/widgets without lookup columns)
        return database.query(SkillMatch).all()


@app.get("/skillmatch/count/", response_model=None, tags=["SkillMatch"])
def get_count_skillmatch(database: DBSession = Depends(get_db)) -> dict:
    """Get the total count of SkillMatch entities"""
    count = database.query(SkillMatch).count()
    return {"count": count}


@app.get("/skillmatch/paginated/", response_model=None, tags=["SkillMatch"])
def get_paginated_skillmatch(skip: int = 0, limit: int = 100, detailed: bool = False, database: DBSession = Depends(get_db)) -> dict:
    """Get paginated list of SkillMatch entities"""
    total = database.query(SkillMatch).count()
    skillmatch_list = database.query(SkillMatch).offset(skip).limit(limit).all()
    # By default, return flat entities (for charts/widgets)
    # Use detailed=true to get entities with relationships
    if not detailed:
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": skillmatch_list
        }

    result = []
    for skillmatch_item in skillmatch_list:
        session_ids = database.query(Session.id).filter(Session.skillmatch_1_id == skillmatch_item.id).all()
        skillrequest_1_ids = database.query(SkillRequest.id).filter(SkillRequest.skillmatch_2_id == skillmatch_item.id).all()
        item_data = {
            "skillmatch": skillmatch_item,
            "session_ids": [x[0] for x in session_ids],            "skillrequest_1_ids": [x[0] for x in skillrequest_1_ids]        }
        result.append(item_data)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": result
    }


@app.get("/skillmatch/search/", response_model=None, tags=["SkillMatch"])
def search_skillmatch(
    database: DBSession = Depends(get_db)
) -> list:
    """Search SkillMatch entities by attributes"""
    query = database.query(SkillMatch)


    results = query.all()
    return results


@app.get("/skillmatch/{skillmatch_id}/", response_model=None, tags=["SkillMatch"])
async def get_skillmatch(skillmatch_id: int, database: DBSession = Depends(get_db)) -> SkillMatch:
    db_skillmatch = database.query(SkillMatch).filter(SkillMatch.id == skillmatch_id).first()
    if db_skillmatch is None:
        raise HTTPException(status_code=404, detail="SkillMatch not found")

    session_ids = database.query(Session.id).filter(Session.skillmatch_1_id == db_skillmatch.id).all()
    skillrequest_1_ids = database.query(SkillRequest.id).filter(SkillRequest.skillmatch_2_id == db_skillmatch.id).all()
    response_data = {
        "skillmatch": db_skillmatch,
        "session_ids": [x[0] for x in session_ids],        "skillrequest_1_ids": [x[0] for x in skillrequest_1_ids]}
    return response_data



@app.post("/skillmatch/", response_model=None, tags=["SkillMatch"])
async def create_skillmatch(skillmatch_data: SkillMatchCreate = Body(alias="params", embed=True), database: DBSession = Depends(get_db)) -> SkillMatch:

    if skillmatch_data.user_2 is not None:
        db_user_2 = database.query(User).filter(User.id == skillmatch_data.user_2).first()
        if not db_user_2:
            raise HTTPException(status_code=400, detail="User not found")
    else:
        raise HTTPException(status_code=400, detail="User ID is required")
    if skillmatch_data.user_3 is not None:
        db_user_3 = database.query(User).filter(User.id == skillmatch_data.user_3).first()
        if not db_user_3:
            raise HTTPException(status_code=400, detail="User not found")
    else:
        raise HTTPException(status_code=400, detail="User ID is required")

    db_skillmatch = SkillMatch(
        startDate=skillmatch_data.startDate,        createdDate=skillmatch_data.createdDate,        status=skillmatch_data.status.value,        user_2_id=skillmatch_data.user_2,        user_3_id=skillmatch_data.user_3        )

    database.add(db_skillmatch)
    database.commit()
    database.refresh(db_skillmatch)

    if skillmatch_data.session:
        # Validate that all Session IDs exist
        for session_id in skillmatch_data.session:
            db_session = database.query(Session).filter(Session.id == session_id).first()
            if not db_session:
                raise HTTPException(status_code=400, detail=f"Session with id {session_id} not found")

        # Update the related entities with the new foreign key
        database.query(Session).filter(Session.id.in_(skillmatch_data.session)).update(
            {Session.skillmatch_1_id: db_skillmatch.id}, synchronize_session=False
        )
        database.commit()
    if skillmatch_data.skillrequest_1:
        # Validate that all SkillRequest IDs exist
        for skillrequest_id in skillmatch_data.skillrequest_1:
            db_skillrequest = database.query(SkillRequest).filter(SkillRequest.id == skillrequest_id).first()
            if not db_skillrequest:
                raise HTTPException(status_code=400, detail=f"SkillRequest with id {skillrequest_id} not found")

        # Update the related entities with the new foreign key
        database.query(SkillRequest).filter(SkillRequest.id.in_(skillmatch_data.skillrequest_1)).update(
            {SkillRequest.skillmatch_2_id: db_skillmatch.id}, synchronize_session=False
        )
        database.commit()



    session_ids = database.query(Session.id).filter(Session.skillmatch_1_id == db_skillmatch.id).all()
    skillrequest_1_ids = database.query(SkillRequest.id).filter(SkillRequest.skillmatch_2_id == db_skillmatch.id).all()
    response_data = {
        "skillmatch": db_skillmatch,
        "session_ids": [x[0] for x in session_ids],        "skillrequest_1_ids": [x[0] for x in skillrequest_1_ids]    }
    return response_data


@app.post("/skillmatch/bulk/", response_model=None, tags=["SkillMatch"])
async def bulk_create_skillmatch(items: list[SkillMatchCreate], database: DBSession = Depends(get_db)) -> dict:
    """Create multiple SkillMatch entities at once"""
    created_items = []
    errors = []

    for idx, item_data in enumerate(items):
        try:
            # Basic validation for each item
            if not item_data.user_2:
                raise ValueError("User ID is required")
            if not item_data.user_3:
                raise ValueError("User ID is required")

            db_skillmatch = SkillMatch(
                startDate=item_data.startDate,                createdDate=item_data.createdDate,                status=item_data.status.value,                user_2_id=item_data.user_2,                user_3_id=item_data.user_3            )
            database.add(db_skillmatch)
            database.flush()  # Get ID without committing
            created_items.append(db_skillmatch.id)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})

    if errors:
        database.rollback()
        raise HTTPException(status_code=400, detail={"message": "Bulk creation failed", "errors": errors})

    database.commit()
    return {
        "created_count": len(created_items),
        "created_ids": created_items,
        "message": f"Successfully created {len(created_items)} SkillMatch entities"
    }


@app.delete("/skillmatch/bulk/", response_model=None, tags=["SkillMatch"])
async def bulk_delete_skillmatch(ids: list[int], database: DBSession = Depends(get_db)) -> dict:
    """Delete multiple SkillMatch entities at once"""
    deleted_count = 0
    not_found = []

    for item_id in ids:
        db_skillmatch = database.query(SkillMatch).filter(SkillMatch.id == item_id).first()
        if db_skillmatch:
            database.delete(db_skillmatch)
            deleted_count += 1
        else:
            not_found.append(item_id)

    database.commit()

    return {
        "deleted_count": deleted_count,
        "not_found": not_found,
        "message": f"Successfully deleted {deleted_count} SkillMatch entities"
    }

@app.put("/skillmatch/{skillmatch_id}/", response_model=None, tags=["SkillMatch"])
async def update_skillmatch(skillmatch_id: int, skillmatch_data: SkillMatchCreate  = Body(alias="params", embed=True), database: DBSession = Depends(get_db)) -> SkillMatch:
    db_skillmatch = database.query(SkillMatch).filter(SkillMatch.id == skillmatch_id).first()
    if db_skillmatch is None:
        raise HTTPException(status_code=404, detail="SkillMatch not found")

    setattr(db_skillmatch, 'startDate', skillmatch_data.startDate)
    setattr(db_skillmatch, 'createdDate', skillmatch_data.createdDate)
    setattr(db_skillmatch, 'status', skillmatch_data.status.value)
    if skillmatch_data.user_2 is not None:
        db_user_2 = database.query(User).filter(User.id == skillmatch_data.user_2).first()
        if not db_user_2:
            raise HTTPException(status_code=400, detail="User not found")
        setattr(db_skillmatch, 'user_2_id', skillmatch_data.user_2)
    if skillmatch_data.user_3 is not None:
        db_user_3 = database.query(User).filter(User.id == skillmatch_data.user_3).first()
        if not db_user_3:
            raise HTTPException(status_code=400, detail="User not found")
        setattr(db_skillmatch, 'user_3_id', skillmatch_data.user_3)
    if skillmatch_data.session is not None:
        # Clear all existing relationships (set foreign key to NULL)
        database.query(Session).filter(Session.skillmatch_1_id == db_skillmatch.id).update(
            {Session.skillmatch_1_id: None}, synchronize_session=False
        )

        # Set new relationships if list is not empty
        if skillmatch_data.session:
            # Validate that all IDs exist
            for session_id in skillmatch_data.session:
                db_session = database.query(Session).filter(Session.id == session_id).first()
                if not db_session:
                    raise HTTPException(status_code=400, detail=f"Session with id {session_id} not found")

            # Update the related entities with the new foreign key
            database.query(Session).filter(Session.id.in_(skillmatch_data.session)).update(
                {Session.skillmatch_1_id: db_skillmatch.id}, synchronize_session=False
            )
    if skillmatch_data.skillrequest_1 is not None:
        # Clear all existing relationships (set foreign key to NULL)
        database.query(SkillRequest).filter(SkillRequest.skillmatch_2_id == db_skillmatch.id).update(
            {SkillRequest.skillmatch_2_id: None}, synchronize_session=False
        )

        # Set new relationships if list is not empty
        if skillmatch_data.skillrequest_1:
            # Validate that all IDs exist
            for skillrequest_id in skillmatch_data.skillrequest_1:
                db_skillrequest = database.query(SkillRequest).filter(SkillRequest.id == skillrequest_id).first()
                if not db_skillrequest:
                    raise HTTPException(status_code=400, detail=f"SkillRequest with id {skillrequest_id} not found")

            # Update the related entities with the new foreign key
            database.query(SkillRequest).filter(SkillRequest.id.in_(skillmatch_data.skillrequest_1)).update(
                {SkillRequest.skillmatch_2_id: db_skillmatch.id}, synchronize_session=False
            )
    database.commit()
    database.refresh(db_skillmatch)

    session_ids = database.query(Session.id).filter(Session.skillmatch_1_id == db_skillmatch.id).all()
    skillrequest_1_ids = database.query(SkillRequest.id).filter(SkillRequest.skillmatch_2_id == db_skillmatch.id).all()
    response_data = {
        "skillmatch": db_skillmatch,
        "session_ids": [x[0] for x in session_ids],        "skillrequest_1_ids": [x[0] for x in skillrequest_1_ids]    }
    return response_data


@app.delete("/skillmatch/{skillmatch_id}/", response_model=None, tags=["SkillMatch"])
async def delete_skillmatch(skillmatch_id: int, database: DBSession = Depends(get_db)):
    db_skillmatch = database.query(SkillMatch).filter(SkillMatch.id == skillmatch_id).first()
    if db_skillmatch is None:
        raise HTTPException(status_code=404, detail="SkillMatch not found")
    database.delete(db_skillmatch)
    database.commit()
    return db_skillmatch





############################################
#
#   SkillRequest functions
#
############################################

@app.get("/skillrequest/", response_model=None, tags=["SkillRequest"])
def get_all_skillrequest(detailed: bool = False, database: DBSession = Depends(get_db)) -> list:
    from sqlalchemy.orm import joinedload

    # Use detailed=true to get entities with eagerly loaded relationships (for tables with lookup columns)
    if detailed:
        # Eagerly load all relationships to avoid N+1 queries
        query = database.query(SkillRequest)
        query = query.options(joinedload(SkillRequest.skillmatch_2))
        query = query.options(joinedload(SkillRequest.skill_1))
        query = query.options(joinedload(SkillRequest.user_1))
        skillrequest_list = query.all()

        # Serialize with relationships included
        result = []
        for skillrequest_item in skillrequest_list:
            item_dict = skillrequest_item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)

            # Add many-to-one relationships (foreign keys for lookup columns)
            if skillrequest_item.skillmatch_2:
                related_obj = skillrequest_item.skillmatch_2
                related_dict = related_obj.__dict__.copy()
                related_dict.pop('_sa_instance_state', None)
                item_dict['skillmatch_2'] = related_dict
            else:
                item_dict['skillmatch_2'] = None
            if skillrequest_item.skill_1:
                related_obj = skillrequest_item.skill_1
                related_dict = related_obj.__dict__.copy()
                related_dict.pop('_sa_instance_state', None)
                item_dict['skill_1'] = related_dict
            else:
                item_dict['skill_1'] = None
            if skillrequest_item.user_1:
                related_obj = skillrequest_item.user_1
                related_dict = related_obj.__dict__.copy()
                related_dict.pop('_sa_instance_state', None)
                item_dict['user_1'] = related_dict
            else:
                item_dict['user_1'] = None


            result.append(item_dict)
        return result
    else:
        # Default: return flat entities (faster for charts/widgets without lookup columns)
        return database.query(SkillRequest).all()


@app.get("/skillrequest/count/", response_model=None, tags=["SkillRequest"])
def get_count_skillrequest(database: DBSession = Depends(get_db)) -> dict:
    """Get the total count of SkillRequest entities"""
    count = database.query(SkillRequest).count()
    return {"count": count}


@app.get("/skillrequest/paginated/", response_model=None, tags=["SkillRequest"])
def get_paginated_skillrequest(skip: int = 0, limit: int = 100, detailed: bool = False, database: DBSession = Depends(get_db)) -> dict:
    """Get paginated list of SkillRequest entities"""
    total = database.query(SkillRequest).count()
    skillrequest_list = database.query(SkillRequest).offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": skillrequest_list
    }


@app.get("/skillrequest/search/", response_model=None, tags=["SkillRequest"])
def search_skillrequest(
    database: DBSession = Depends(get_db)
) -> list:
    """Search SkillRequest entities by attributes"""
    query = database.query(SkillRequest)


    results = query.all()
    return results


@app.get("/skillrequest/{skillrequest_id}/", response_model=None, tags=["SkillRequest"])
async def get_skillrequest(skillrequest_id: int, database: DBSession = Depends(get_db)) -> SkillRequest:
    db_skillrequest = database.query(SkillRequest).filter(SkillRequest.id == skillrequest_id).first()
    if db_skillrequest is None:
        raise HTTPException(status_code=404, detail="SkillRequest not found")

    response_data = {
        "skillrequest": db_skillrequest,
}
    return response_data



@app.post("/skillrequest/", response_model=None, tags=["SkillRequest"])
async def create_skillrequest(skillrequest_data: SkillRequestCreate = Body(alias="params", embed=True), database: DBSession = Depends(get_db)) -> SkillRequest:

    if skillrequest_data.skillmatch_2 :
        db_skillmatch_2 = database.query(SkillMatch).filter(SkillMatch.id == skillrequest_data.skillmatch_2).first()
        if not db_skillmatch_2:
            raise HTTPException(status_code=400, detail="SkillMatch not found")
    if skillrequest_data.skill_1 is not None:
        db_skill_1 = database.query(Skill).filter(Skill.id == skillrequest_data.skill_1).first()
        if not db_skill_1:
            raise HTTPException(status_code=400, detail="Skill not found")
    else:
        raise HTTPException(status_code=400, detail="Skill ID is required")
    if skillrequest_data.user_1 is not None:
        db_user_1 = database.query(User).filter(User.id == skillrequest_data.user_1).first()
        if not db_user_1:
            raise HTTPException(status_code=400, detail="User not found")
    else:
        raise HTTPException(status_code=400, detail="User ID is required")

    db_skillrequest = SkillRequest(
        deadlineDate=skillrequest_data.deadlineDate,        status=skillrequest_data.status.value,        createdDate=skillrequest_data.createdDate,        skillmatch_2_id=skillrequest_data.skillmatch_2,        skill_1_id=skillrequest_data.skill_1,        user_1_id=skillrequest_data.user_1        )

    database.add(db_skillrequest)
    database.commit()
    database.refresh(db_skillrequest)




    return db_skillrequest


@app.post("/skillrequest/bulk/", response_model=None, tags=["SkillRequest"])
async def bulk_create_skillrequest(items: list[SkillRequestCreate], database: DBSession = Depends(get_db)) -> dict:
    """Create multiple SkillRequest entities at once"""
    created_items = []
    errors = []

    for idx, item_data in enumerate(items):
        try:
            # Basic validation for each item
            if not item_data.skill_1:
                raise ValueError("Skill ID is required")
            if not item_data.user_1:
                raise ValueError("User ID is required")

            db_skillrequest = SkillRequest(
                deadlineDate=item_data.deadlineDate,                status=item_data.status.value,                createdDate=item_data.createdDate,                skillmatch_2_id=item_data.skillmatch_2,                skill_1_id=item_data.skill_1,                user_1_id=item_data.user_1            )
            database.add(db_skillrequest)
            database.flush()  # Get ID without committing
            created_items.append(db_skillrequest.id)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})

    if errors:
        database.rollback()
        raise HTTPException(status_code=400, detail={"message": "Bulk creation failed", "errors": errors})

    database.commit()
    return {
        "created_count": len(created_items),
        "created_ids": created_items,
        "message": f"Successfully created {len(created_items)} SkillRequest entities"
    }


@app.delete("/skillrequest/bulk/", response_model=None, tags=["SkillRequest"])
async def bulk_delete_skillrequest(ids: list[int], database: DBSession = Depends(get_db)) -> dict:
    """Delete multiple SkillRequest entities at once"""
    deleted_count = 0
    not_found = []

    for item_id in ids:
        db_skillrequest = database.query(SkillRequest).filter(SkillRequest.id == item_id).first()
        if db_skillrequest:
            database.delete(db_skillrequest)
            deleted_count += 1
        else:
            not_found.append(item_id)

    database.commit()

    return {
        "deleted_count": deleted_count,
        "not_found": not_found,
        "message": f"Successfully deleted {deleted_count} SkillRequest entities"
    }

@app.put("/skillrequest/{skillrequest_id}/", response_model=None, tags=["SkillRequest"])
async def update_skillrequest(skillrequest_id: int, skillrequest_data: SkillRequestCreate  = Body(alias="params", embed=True), database: DBSession = Depends(get_db)) -> SkillRequest:
    db_skillrequest = database.query(SkillRequest).filter(SkillRequest.id == skillrequest_id).first()
    if db_skillrequest is None:
        raise HTTPException(status_code=404, detail="SkillRequest not found")

    setattr(db_skillrequest, 'deadlineDate', skillrequest_data.deadlineDate)
    setattr(db_skillrequest, 'status', skillrequest_data.status.value)
    setattr(db_skillrequest, 'createdDate', skillrequest_data.createdDate)
    if skillrequest_data.skillmatch_2 is not None:
        db_skillmatch_2 = database.query(SkillMatch).filter(SkillMatch.id == skillrequest_data.skillmatch_2).first()
        if not db_skillmatch_2:
            raise HTTPException(status_code=400, detail="SkillMatch not found")
        setattr(db_skillrequest, 'skillmatch_2_id', skillrequest_data.skillmatch_2)
    else:
        setattr(db_skillrequest, 'skillmatch_2_id', None)
    if skillrequest_data.skill_1 is not None:
        db_skill_1 = database.query(Skill).filter(Skill.id == skillrequest_data.skill_1).first()
        if not db_skill_1:
            raise HTTPException(status_code=400, detail="Skill not found")
        setattr(db_skillrequest, 'skill_1_id', skillrequest_data.skill_1)
    if skillrequest_data.user_1 is not None:
        db_user_1 = database.query(User).filter(User.id == skillrequest_data.user_1).first()
        if not db_user_1:
            raise HTTPException(status_code=400, detail="User not found")
        setattr(db_skillrequest, 'user_1_id', skillrequest_data.user_1)
    database.commit()
    database.refresh(db_skillrequest)

    return db_skillrequest


@app.delete("/skillrequest/{skillrequest_id}/", response_model=None, tags=["SkillRequest"])
async def delete_skillrequest(skillrequest_id: int, database: DBSession = Depends(get_db)):
    db_skillrequest = database.query(SkillRequest).filter(SkillRequest.id == skillrequest_id).first()
    if db_skillrequest is None:
        raise HTTPException(status_code=404, detail="SkillRequest not found")
    database.delete(db_skillrequest)
    database.commit()
    return db_skillrequest





############################################
#
#   Skill functions
#
############################################

@app.get("/skill/", response_model=None, tags=["Skill"])
def get_all_skill(detailed: bool = False, database: DBSession = Depends(get_db)) -> list:
    from sqlalchemy.orm import joinedload

    # Use detailed=true to get entities with eagerly loaded relationships (for tables with lookup columns)
    if detailed:
        # Eagerly load all relationships to avoid N+1 queries
        query = database.query(Skill)
        skill_list = query.all()

        # Serialize with relationships included
        result = []
        for skill_item in skill_list:
            item_dict = skill_item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)

            # Add many-to-one relationships (foreign keys for lookup columns)

            # Add many-to-many and one-to-many relationship objects (full details)
            skillrequest_list = database.query(SkillRequest).filter(SkillRequest.skill_1_id == skill_item.id).all()
            item_dict['skillrequest_2'] = []
            for skillrequest_obj in skillrequest_list:
                skillrequest_dict = skillrequest_obj.__dict__.copy()
                skillrequest_dict.pop('_sa_instance_state', None)
                item_dict['skillrequest_2'].append(skillrequest_dict)
            userskill_list = database.query(UserSkill).filter(UserSkill.skill_id == skill_item.id).all()
            item_dict['userskill_1'] = []
            for userskill_obj in userskill_list:
                userskill_dict = userskill_obj.__dict__.copy()
                userskill_dict.pop('_sa_instance_state', None)
                item_dict['userskill_1'].append(userskill_dict)

            result.append(item_dict)
        return result
    else:
        # Default: return flat entities (faster for charts/widgets without lookup columns)
        return database.query(Skill).all()


@app.get("/skill/count/", response_model=None, tags=["Skill"])
def get_count_skill(database: DBSession = Depends(get_db)) -> dict:
    """Get the total count of Skill entities"""
    count = database.query(Skill).count()
    return {"count": count}


@app.get("/skill/paginated/", response_model=None, tags=["Skill"])
def get_paginated_skill(skip: int = 0, limit: int = 100, detailed: bool = False, database: DBSession = Depends(get_db)) -> dict:
    """Get paginated list of Skill entities"""
    total = database.query(Skill).count()
    skill_list = database.query(Skill).offset(skip).limit(limit).all()
    # By default, return flat entities (for charts/widgets)
    # Use detailed=true to get entities with relationships
    if not detailed:
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": skill_list
        }

    result = []
    for skill_item in skill_list:
        skillrequest_2_ids = database.query(SkillRequest.id).filter(SkillRequest.skill_1_id == skill_item.id).all()
        userskill_1_ids = database.query(UserSkill.id).filter(UserSkill.skill_id == skill_item.id).all()
        item_data = {
            "skill": skill_item,
            "skillrequest_2_ids": [x[0] for x in skillrequest_2_ids],            "userskill_1_ids": [x[0] for x in userskill_1_ids]        }
        result.append(item_data)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": result
    }


@app.get("/skill/search/", response_model=None, tags=["Skill"])
def search_skill(
    database: DBSession = Depends(get_db)
) -> list:
    """Search Skill entities by attributes"""
    query = database.query(Skill)


    results = query.all()
    return results


@app.get("/skill/{skill_id}/", response_model=None, tags=["Skill"])
async def get_skill(skill_id: int, database: DBSession = Depends(get_db)) -> Skill:
    db_skill = database.query(Skill).filter(Skill.id == skill_id).first()
    if db_skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")

    skillrequest_2_ids = database.query(SkillRequest.id).filter(SkillRequest.skill_1_id == db_skill.id).all()
    userskill_1_ids = database.query(UserSkill.id).filter(UserSkill.skill_id == db_skill.id).all()
    response_data = {
        "skill": db_skill,
        "skillrequest_2_ids": [x[0] for x in skillrequest_2_ids],        "userskill_1_ids": [x[0] for x in userskill_1_ids]}
    return response_data



@app.post("/skill/", response_model=None, tags=["Skill"])
async def create_skill(skill_data: SkillCreate = Body(alias="params", embed=True), database: DBSession = Depends(get_db)) -> Skill:


    db_skill = Skill(
        skillLevel=skill_data.skillLevel.value,        estimatedDuration=skill_data.estimatedDuration,        category=skill_data.category,        skillName=skill_data.skillName,        description=skill_data.description,        skillId=skill_data.skillId        )

    database.add(db_skill)
    database.commit()
    database.refresh(db_skill)

    if skill_data.skillrequest_2:
        # Validate that all SkillRequest IDs exist
        for skillrequest_id in skill_data.skillrequest_2:
            db_skillrequest = database.query(SkillRequest).filter(SkillRequest.id == skillrequest_id).first()
            if not db_skillrequest:
                raise HTTPException(status_code=400, detail=f"SkillRequest with id {skillrequest_id} not found")

        # Update the related entities with the new foreign key
        database.query(SkillRequest).filter(SkillRequest.id.in_(skill_data.skillrequest_2)).update(
            {SkillRequest.skill_1_id: db_skill.id}, synchronize_session=False
        )
        database.commit()
    if skill_data.userskill_1:
        # Validate that all UserSkill IDs exist
        for userskill_id in skill_data.userskill_1:
            db_userskill = database.query(UserSkill).filter(UserSkill.id == userskill_id).first()
            if not db_userskill:
                raise HTTPException(status_code=400, detail=f"UserSkill with id {userskill_id} not found")

        # Update the related entities with the new foreign key
        database.query(UserSkill).filter(UserSkill.id.in_(skill_data.userskill_1)).update(
            {UserSkill.skill_id: db_skill.id}, synchronize_session=False
        )
        database.commit()



    skillrequest_2_ids = database.query(SkillRequest.id).filter(SkillRequest.skill_1_id == db_skill.id).all()
    userskill_1_ids = database.query(UserSkill.id).filter(UserSkill.skill_id == db_skill.id).all()
    response_data = {
        "skill": db_skill,
        "skillrequest_2_ids": [x[0] for x in skillrequest_2_ids],        "userskill_1_ids": [x[0] for x in userskill_1_ids]    }
    return response_data


@app.post("/skill/bulk/", response_model=None, tags=["Skill"])
async def bulk_create_skill(items: list[SkillCreate], database: DBSession = Depends(get_db)) -> dict:
    """Create multiple Skill entities at once"""
    created_items = []
    errors = []

    for idx, item_data in enumerate(items):
        try:
            # Basic validation for each item

            db_skill = Skill(
                skillLevel=item_data.skillLevel.value,                estimatedDuration=item_data.estimatedDuration,                category=item_data.category,                skillName=item_data.skillName,                description=item_data.description,                skillId=item_data.skillId            )
            database.add(db_skill)
            database.flush()  # Get ID without committing
            created_items.append(db_skill.id)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})

    if errors:
        database.rollback()
        raise HTTPException(status_code=400, detail={"message": "Bulk creation failed", "errors": errors})

    database.commit()
    return {
        "created_count": len(created_items),
        "created_ids": created_items,
        "message": f"Successfully created {len(created_items)} Skill entities"
    }


@app.delete("/skill/bulk/", response_model=None, tags=["Skill"])
async def bulk_delete_skill(ids: list[int], database: DBSession = Depends(get_db)) -> dict:
    """Delete multiple Skill entities at once"""
    deleted_count = 0
    not_found = []

    for item_id in ids:
        db_skill = database.query(Skill).filter(Skill.id == item_id).first()
        if db_skill:
            database.delete(db_skill)
            deleted_count += 1
        else:
            not_found.append(item_id)

    database.commit()

    return {
        "deleted_count": deleted_count,
        "not_found": not_found,
        "message": f"Successfully deleted {deleted_count} Skill entities"
    }

@app.put("/skill/{skill_id}/", response_model=None, tags=["Skill"])
async def update_skill(skill_id: int, skill_data: SkillCreate  = Body(alias="params", embed=True), database: DBSession = Depends(get_db)) -> Skill:
    db_skill = database.query(Skill).filter(Skill.id == skill_id).first()
    if db_skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")

    setattr(db_skill, 'skillLevel', skill_data.skillLevel.value)
    setattr(db_skill, 'estimatedDuration', skill_data.estimatedDuration)
    setattr(db_skill, 'category', skill_data.category)
    setattr(db_skill, 'skillName', skill_data.skillName)
    setattr(db_skill, 'description', skill_data.description)
    setattr(db_skill, 'skillId', skill_data.skillId)
    if skill_data.skillrequest_2 is not None:
        # Clear all existing relationships (set foreign key to NULL)
        database.query(SkillRequest).filter(SkillRequest.skill_1_id == db_skill.id).update(
            {SkillRequest.skill_1_id: None}, synchronize_session=False
        )

        # Set new relationships if list is not empty
        if skill_data.skillrequest_2:
            # Validate that all IDs exist
            for skillrequest_id in skill_data.skillrequest_2:
                db_skillrequest = database.query(SkillRequest).filter(SkillRequest.id == skillrequest_id).first()
                if not db_skillrequest:
                    raise HTTPException(status_code=400, detail=f"SkillRequest with id {skillrequest_id} not found")

            # Update the related entities with the new foreign key
            database.query(SkillRequest).filter(SkillRequest.id.in_(skill_data.skillrequest_2)).update(
                {SkillRequest.skill_1_id: db_skill.id}, synchronize_session=False
            )
    if skill_data.userskill_1 is not None:
        # Clear all existing relationships (set foreign key to NULL)
        database.query(UserSkill).filter(UserSkill.skill_id == db_skill.id).update(
            {UserSkill.skill_id: None}, synchronize_session=False
        )

        # Set new relationships if list is not empty
        if skill_data.userskill_1:
            # Validate that all IDs exist
            for userskill_id in skill_data.userskill_1:
                db_userskill = database.query(UserSkill).filter(UserSkill.id == userskill_id).first()
                if not db_userskill:
                    raise HTTPException(status_code=400, detail=f"UserSkill with id {userskill_id} not found")

            # Update the related entities with the new foreign key
            database.query(UserSkill).filter(UserSkill.id.in_(skill_data.userskill_1)).update(
                {UserSkill.skill_id: db_skill.id}, synchronize_session=False
            )
    database.commit()
    database.refresh(db_skill)

    skillrequest_2_ids = database.query(SkillRequest.id).filter(SkillRequest.skill_1_id == db_skill.id).all()
    userskill_1_ids = database.query(UserSkill.id).filter(UserSkill.skill_id == db_skill.id).all()
    response_data = {
        "skill": db_skill,
        "skillrequest_2_ids": [x[0] for x in skillrequest_2_ids],        "userskill_1_ids": [x[0] for x in userskill_1_ids]    }
    return response_data


@app.delete("/skill/{skill_id}/", response_model=None, tags=["Skill"])
async def delete_skill(skill_id: int, database: DBSession = Depends(get_db)):
    db_skill = database.query(Skill).filter(Skill.id == skill_id).first()
    if db_skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    database.delete(db_skill)
    database.commit()
    return db_skill





############################################
#
#   UserSkill functions
#
############################################

@app.get("/userskill/", response_model=None, tags=["UserSkill"])
def get_all_userskill(detailed: bool = False, database: DBSession = Depends(get_db)) -> list:
    from sqlalchemy.orm import joinedload

    # Use detailed=true to get entities with eagerly loaded relationships (for tables with lookup columns)
    if detailed:
        # Eagerly load all relationships to avoid N+1 queries
        query = database.query(UserSkill)
        query = query.options(joinedload(UserSkill.skill))
        query = query.options(joinedload(UserSkill.user))
        userskill_list = query.all()

        # Serialize with relationships included
        result = []
        for userskill_item in userskill_list:
            item_dict = userskill_item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)

            # Add many-to-one relationships (foreign keys for lookup columns)
            if userskill_item.skill:
                related_obj = userskill_item.skill
                related_dict = related_obj.__dict__.copy()
                related_dict.pop('_sa_instance_state', None)
                item_dict['skill'] = related_dict
            else:
                item_dict['skill'] = None
            if userskill_item.user:
                related_obj = userskill_item.user
                related_dict = related_obj.__dict__.copy()
                related_dict.pop('_sa_instance_state', None)
                item_dict['user'] = related_dict
            else:
                item_dict['user'] = None


            result.append(item_dict)
        return result
    else:
        # Default: return flat entities (faster for charts/widgets without lookup columns)
        return database.query(UserSkill).all()


@app.get("/userskill/count/", response_model=None, tags=["UserSkill"])
def get_count_userskill(database: DBSession = Depends(get_db)) -> dict:
    """Get the total count of UserSkill entities"""
    count = database.query(UserSkill).count()
    return {"count": count}


@app.get("/userskill/paginated/", response_model=None, tags=["UserSkill"])
def get_paginated_userskill(skip: int = 0, limit: int = 100, detailed: bool = False, database: DBSession = Depends(get_db)) -> dict:
    """Get paginated list of UserSkill entities"""
    total = database.query(UserSkill).count()
    userskill_list = database.query(UserSkill).offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": userskill_list
    }


@app.get("/userskill/search/", response_model=None, tags=["UserSkill"])
def search_userskill(
    database: DBSession = Depends(get_db)
) -> list:
    """Search UserSkill entities by attributes"""
    query = database.query(UserSkill)


    results = query.all()
    return results


@app.get("/userskill/{userskill_id}/", response_model=None, tags=["UserSkill"])
async def get_userskill(userskill_id: int, database: DBSession = Depends(get_db)) -> UserSkill:
    db_userskill = database.query(UserSkill).filter(UserSkill.id == userskill_id).first()
    if db_userskill is None:
        raise HTTPException(status_code=404, detail="UserSkill not found")

    response_data = {
        "userskill": db_userskill,
}
    return response_data



@app.post("/userskill/", response_model=None, tags=["UserSkill"])
async def create_userskill(userskill_data: UserSkillCreate = Body(alias="params", embed=True), database: DBSession = Depends(get_db)) -> UserSkill:

    if userskill_data.skill is not None:
        db_skill = database.query(Skill).filter(Skill.id == userskill_data.skill).first()
        if not db_skill:
            raise HTTPException(status_code=400, detail="Skill not found")
    else:
        raise HTTPException(status_code=400, detail="Skill ID is required")
    if userskill_data.user is not None:
        db_user = database.query(User).filter(User.id == userskill_data.user).first()
        if not db_user:
            raise HTTPException(status_code=400, detail="User not found")
    else:
        raise HTTPException(status_code=400, detail="User ID is required")

    db_userskill = UserSkill(
        certification=userskill_data.certification,        yearsOfExperience=userskill_data.yearsOfExperience,        skillLevel=userskill_data.skillLevel.value,        skill_id=userskill_data.skill,        user_id=userskill_data.user        )

    database.add(db_userskill)
    database.commit()
    database.refresh(db_userskill)




    return db_userskill


@app.post("/userskill/bulk/", response_model=None, tags=["UserSkill"])
async def bulk_create_userskill(items: list[UserSkillCreate], database: DBSession = Depends(get_db)) -> dict:
    """Create multiple UserSkill entities at once"""
    created_items = []
    errors = []

    for idx, item_data in enumerate(items):
        try:
            # Basic validation for each item
            if not item_data.skill:
                raise ValueError("Skill ID is required")
            if not item_data.user:
                raise ValueError("User ID is required")

            db_userskill = UserSkill(
                certification=item_data.certification,                yearsOfExperience=item_data.yearsOfExperience,                skillLevel=item_data.skillLevel.value,                skill_id=item_data.skill,                user_id=item_data.user            )
            database.add(db_userskill)
            database.flush()  # Get ID without committing
            created_items.append(db_userskill.id)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})

    if errors:
        database.rollback()
        raise HTTPException(status_code=400, detail={"message": "Bulk creation failed", "errors": errors})

    database.commit()
    return {
        "created_count": len(created_items),
        "created_ids": created_items,
        "message": f"Successfully created {len(created_items)} UserSkill entities"
    }


@app.delete("/userskill/bulk/", response_model=None, tags=["UserSkill"])
async def bulk_delete_userskill(ids: list[int], database: DBSession = Depends(get_db)) -> dict:
    """Delete multiple UserSkill entities at once"""
    deleted_count = 0
    not_found = []

    for item_id in ids:
        db_userskill = database.query(UserSkill).filter(UserSkill.id == item_id).first()
        if db_userskill:
            database.delete(db_userskill)
            deleted_count += 1
        else:
            not_found.append(item_id)

    database.commit()

    return {
        "deleted_count": deleted_count,
        "not_found": not_found,
        "message": f"Successfully deleted {deleted_count} UserSkill entities"
    }

@app.put("/userskill/{userskill_id}/", response_model=None, tags=["UserSkill"])
async def update_userskill(userskill_id: int, userskill_data: UserSkillCreate  = Body(alias="params", embed=True), database: DBSession = Depends(get_db)) -> UserSkill:
    db_userskill = database.query(UserSkill).filter(UserSkill.id == userskill_id).first()
    if db_userskill is None:
        raise HTTPException(status_code=404, detail="UserSkill not found")

    setattr(db_userskill, 'certification', userskill_data.certification)
    setattr(db_userskill, 'yearsOfExperience', userskill_data.yearsOfExperience)
    setattr(db_userskill, 'skillLevel', userskill_data.skillLevel.value)
    if userskill_data.skill is not None:
        db_skill = database.query(Skill).filter(Skill.id == userskill_data.skill).first()
        if not db_skill:
            raise HTTPException(status_code=400, detail="Skill not found")
        setattr(db_userskill, 'skill_id', userskill_data.skill)
    if userskill_data.user is not None:
        db_user = database.query(User).filter(User.id == userskill_data.user).first()
        if not db_user:
            raise HTTPException(status_code=400, detail="User not found")
        setattr(db_userskill, 'user_id', userskill_data.user)
    database.commit()
    database.refresh(db_userskill)

    return db_userskill


@app.delete("/userskill/{userskill_id}/", response_model=None, tags=["UserSkill"])
async def delete_userskill(userskill_id: int, database: DBSession = Depends(get_db)):
    db_userskill = database.query(UserSkill).filter(UserSkill.id == userskill_id).first()
    if db_userskill is None:
        raise HTTPException(status_code=404, detail="UserSkill not found")
    database.delete(db_userskill)
    database.commit()
    return db_userskill





############################################
#
#   User functions
#
############################################

@app.get("/user/", response_model=None, tags=["User"])
def get_all_user(detailed: bool = False, database: DBSession = Depends(get_db)) -> list:
    from sqlalchemy.orm import joinedload

    # Use detailed=true to get entities with eagerly loaded relationships (for tables with lookup columns)
    if detailed:
        # Eagerly load all relationships to avoid N+1 queries
        query = database.query(User)
        user_list = query.all()

        # Serialize with relationships included
        result = []
        for user_item in user_list:
            item_dict = user_item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)

            # Add many-to-one relationships (foreign keys for lookup columns)

            # Add many-to-many and one-to-many relationship objects (full details)
            skillmatch_list = database.query(SkillMatch).filter(SkillMatch.user_2_id == user_item.id).all()
            item_dict['skillmatch'] = []
            for skillmatch_obj in skillmatch_list:
                skillmatch_dict = skillmatch_obj.__dict__.copy()
                skillmatch_dict.pop('_sa_instance_state', None)
                item_dict['skillmatch'].append(skillmatch_dict)
            userskill_list = database.query(UserSkill).filter(UserSkill.user_id == user_item.id).all()
            item_dict['userskill'] = []
            for userskill_obj in userskill_list:
                userskill_dict = userskill_obj.__dict__.copy()
                userskill_dict.pop('_sa_instance_state', None)
                item_dict['userskill'].append(userskill_dict)
            skillrequest_list = database.query(SkillRequest).filter(SkillRequest.user_1_id == user_item.id).all()
            item_dict['skillrequest'] = []
            for skillrequest_obj in skillrequest_list:
                skillrequest_dict = skillrequest_obj.__dict__.copy()
                skillrequest_dict.pop('_sa_instance_state', None)
                item_dict['skillrequest'].append(skillrequest_dict)
            skillmatch_list = database.query(SkillMatch).filter(SkillMatch.user_3_id == user_item.id).all()
            item_dict['skillmatch_3'] = []
            for skillmatch_obj in skillmatch_list:
                skillmatch_dict = skillmatch_obj.__dict__.copy()
                skillmatch_dict.pop('_sa_instance_state', None)
                item_dict['skillmatch_3'].append(skillmatch_dict)

            result.append(item_dict)
        return result
    else:
        # Default: return flat entities (faster for charts/widgets without lookup columns)
        return database.query(User).all()


@app.get("/user/count/", response_model=None, tags=["User"])
def get_count_user(database: DBSession = Depends(get_db)) -> dict:
    """Get the total count of User entities"""
    count = database.query(User).count()
    return {"count": count}


@app.get("/user/paginated/", response_model=None, tags=["User"])
def get_paginated_user(skip: int = 0, limit: int = 100, detailed: bool = False, database: DBSession = Depends(get_db)) -> dict:
    """Get paginated list of User entities"""
    total = database.query(User).count()
    user_list = database.query(User).offset(skip).limit(limit).all()
    # By default, return flat entities (for charts/widgets)
    # Use detailed=true to get entities with relationships
    if not detailed:
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": user_list
        }

    result = []
    for user_item in user_list:
        skillmatch_ids = database.query(SkillMatch.id).filter(SkillMatch.user_2_id == user_item.id).all()
        userskill_ids = database.query(UserSkill.id).filter(UserSkill.user_id == user_item.id).all()
        skillrequest_ids = database.query(SkillRequest.id).filter(SkillRequest.user_1_id == user_item.id).all()
        skillmatch_3_ids = database.query(SkillMatch.id).filter(SkillMatch.user_3_id == user_item.id).all()
        item_data = {
            "user": user_item,
            "skillmatch_ids": [x[0] for x in skillmatch_ids],            "userskill_ids": [x[0] for x in userskill_ids],            "skillrequest_ids": [x[0] for x in skillrequest_ids],            "skillmatch_3_ids": [x[0] for x in skillmatch_3_ids]        }
        result.append(item_data)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": result
    }


@app.get("/user/search/", response_model=None, tags=["User"])
def search_user(
    database: DBSession = Depends(get_db)
) -> list:
    """Search User entities by attributes"""
    query = database.query(User)


    results = query.all()
    return results


@app.get("/user/{user_id}/", response_model=None, tags=["User"])
async def get_user(user_id: int, database: DBSession = Depends(get_db)) -> User:
    db_user = database.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    skillmatch_ids = database.query(SkillMatch.id).filter(SkillMatch.user_2_id == db_user.id).all()
    userskill_ids = database.query(UserSkill.id).filter(UserSkill.user_id == db_user.id).all()
    skillrequest_ids = database.query(SkillRequest.id).filter(SkillRequest.user_1_id == db_user.id).all()
    skillmatch_3_ids = database.query(SkillMatch.id).filter(SkillMatch.user_3_id == db_user.id).all()
    response_data = {
        "user": db_user,
        "skillmatch_ids": [x[0] for x in skillmatch_ids],        "userskill_ids": [x[0] for x in userskill_ids],        "skillrequest_ids": [x[0] for x in skillrequest_ids],        "skillmatch_3_ids": [x[0] for x in skillmatch_3_ids]}
    return response_data



@app.post("/user/", response_model=None, tags=["User"])
async def create_user(user_data: UserCreate = Body(alias="params", embed=True), database: DBSession = Depends(get_db)) -> User:


    db_user = User(
        userId=user_data.userId,        emailId=user_data.emailId,        userName=user_data.userName        )

    database.add(db_user)
    database.commit()
    database.refresh(db_user)

    if user_data.skillmatch:
        # Validate that all SkillMatch IDs exist
        for skillmatch_id in user_data.skillmatch:
            db_skillmatch = database.query(SkillMatch).filter(SkillMatch.id == skillmatch_id).first()
            if not db_skillmatch:
                raise HTTPException(status_code=400, detail=f"SkillMatch with id {skillmatch_id} not found")

        # Update the related entities with the new foreign key
        database.query(SkillMatch).filter(SkillMatch.id.in_(user_data.skillmatch)).update(
            {SkillMatch.user_2_id: db_user.id}, synchronize_session=False
        )
        database.commit()
    if user_data.userskill:
        # Validate that all UserSkill IDs exist
        for userskill_id in user_data.userskill:
            db_userskill = database.query(UserSkill).filter(UserSkill.id == userskill_id).first()
            if not db_userskill:
                raise HTTPException(status_code=400, detail=f"UserSkill with id {userskill_id} not found")

        # Update the related entities with the new foreign key
        database.query(UserSkill).filter(UserSkill.id.in_(user_data.userskill)).update(
            {UserSkill.user_id: db_user.id}, synchronize_session=False
        )
        database.commit()
    if user_data.skillrequest:
        # Validate that all SkillRequest IDs exist
        for skillrequest_id in user_data.skillrequest:
            db_skillrequest = database.query(SkillRequest).filter(SkillRequest.id == skillrequest_id).first()
            if not db_skillrequest:
                raise HTTPException(status_code=400, detail=f"SkillRequest with id {skillrequest_id} not found")

        # Update the related entities with the new foreign key
        database.query(SkillRequest).filter(SkillRequest.id.in_(user_data.skillrequest)).update(
            {SkillRequest.user_1_id: db_user.id}, synchronize_session=False
        )
        database.commit()
    if user_data.skillmatch_3:
        # Validate that all SkillMatch IDs exist
        for skillmatch_id in user_data.skillmatch_3:
            db_skillmatch = database.query(SkillMatch).filter(SkillMatch.id == skillmatch_id).first()
            if not db_skillmatch:
                raise HTTPException(status_code=400, detail=f"SkillMatch with id {skillmatch_id} not found")

        # Update the related entities with the new foreign key
        database.query(SkillMatch).filter(SkillMatch.id.in_(user_data.skillmatch_3)).update(
            {SkillMatch.user_3_id: db_user.id}, synchronize_session=False
        )
        database.commit()



    skillmatch_ids = database.query(SkillMatch.id).filter(SkillMatch.user_2_id == db_user.id).all()
    userskill_ids = database.query(UserSkill.id).filter(UserSkill.user_id == db_user.id).all()
    skillrequest_ids = database.query(SkillRequest.id).filter(SkillRequest.user_1_id == db_user.id).all()
    skillmatch_3_ids = database.query(SkillMatch.id).filter(SkillMatch.user_3_id == db_user.id).all()
    response_data = {
        "user": db_user,
        "skillmatch_ids": [x[0] for x in skillmatch_ids],        "userskill_ids": [x[0] for x in userskill_ids],        "skillrequest_ids": [x[0] for x in skillrequest_ids],        "skillmatch_3_ids": [x[0] for x in skillmatch_3_ids]    }
    return response_data


@app.post("/user/bulk/", response_model=None, tags=["User"])
async def bulk_create_user(items: list[UserCreate], database: DBSession = Depends(get_db)) -> dict:
    """Create multiple User entities at once"""
    created_items = []
    errors = []

    for idx, item_data in enumerate(items):
        try:
            # Basic validation for each item

            db_user = User(
                userId=item_data.userId,                emailId=item_data.emailId,                userName=item_data.userName            )
            database.add(db_user)
            database.flush()  # Get ID without committing
            created_items.append(db_user.id)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})

    if errors:
        database.rollback()
        raise HTTPException(status_code=400, detail={"message": "Bulk creation failed", "errors": errors})

    database.commit()
    return {
        "created_count": len(created_items),
        "created_ids": created_items,
        "message": f"Successfully created {len(created_items)} User entities"
    }


@app.delete("/user/bulk/", response_model=None, tags=["User"])
async def bulk_delete_user(ids: list[int], database: DBSession = Depends(get_db)) -> dict:
    """Delete multiple User entities at once"""
    deleted_count = 0
    not_found = []

    for item_id in ids:
        db_user = database.query(User).filter(User.id == item_id).first()
        if db_user:
            database.delete(db_user)
            deleted_count += 1
        else:
            not_found.append(item_id)

    database.commit()

    return {
        "deleted_count": deleted_count,
        "not_found": not_found,
        "message": f"Successfully deleted {deleted_count} User entities"
    }

@app.put("/user/{user_id}/", response_model=None, tags=["User"])
async def update_user(user_id: int, user_data: UserCreate  = Body(alias="params", embed=True), database: DBSession = Depends(get_db)) -> User:
    db_user = database.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    setattr(db_user, 'userId', user_data.userId)
    setattr(db_user, 'emailId', user_data.emailId)
    setattr(db_user, 'userName', user_data.userName)
    if user_data.skillmatch is not None:
        # Clear all existing relationships (set foreign key to NULL)
        database.query(SkillMatch).filter(SkillMatch.user_2_id == db_user.id).update(
            {SkillMatch.user_2_id: None}, synchronize_session=False
        )

        # Set new relationships if list is not empty
        if user_data.skillmatch:
            # Validate that all IDs exist
            for skillmatch_id in user_data.skillmatch:
                db_skillmatch = database.query(SkillMatch).filter(SkillMatch.id == skillmatch_id).first()
                if not db_skillmatch:
                    raise HTTPException(status_code=400, detail=f"SkillMatch with id {skillmatch_id} not found")

            # Update the related entities with the new foreign key
            database.query(SkillMatch).filter(SkillMatch.id.in_(user_data.skillmatch)).update(
                {SkillMatch.user_2_id: db_user.id}, synchronize_session=False
            )
    if user_data.userskill is not None:
        # Clear all existing relationships (set foreign key to NULL)
        database.query(UserSkill).filter(UserSkill.user_id == db_user.id).update(
            {UserSkill.user_id: None}, synchronize_session=False
        )

        # Set new relationships if list is not empty
        if user_data.userskill:
            # Validate that all IDs exist
            for userskill_id in user_data.userskill:
                db_userskill = database.query(UserSkill).filter(UserSkill.id == userskill_id).first()
                if not db_userskill:
                    raise HTTPException(status_code=400, detail=f"UserSkill with id {userskill_id} not found")

            # Update the related entities with the new foreign key
            database.query(UserSkill).filter(UserSkill.id.in_(user_data.userskill)).update(
                {UserSkill.user_id: db_user.id}, synchronize_session=False
            )
    if user_data.skillrequest is not None:
        # Clear all existing relationships (set foreign key to NULL)
        database.query(SkillRequest).filter(SkillRequest.user_1_id == db_user.id).update(
            {SkillRequest.user_1_id: None}, synchronize_session=False
        )

        # Set new relationships if list is not empty
        if user_data.skillrequest:
            # Validate that all IDs exist
            for skillrequest_id in user_data.skillrequest:
                db_skillrequest = database.query(SkillRequest).filter(SkillRequest.id == skillrequest_id).first()
                if not db_skillrequest:
                    raise HTTPException(status_code=400, detail=f"SkillRequest with id {skillrequest_id} not found")

            # Update the related entities with the new foreign key
            database.query(SkillRequest).filter(SkillRequest.id.in_(user_data.skillrequest)).update(
                {SkillRequest.user_1_id: db_user.id}, synchronize_session=False
            )
    if user_data.skillmatch_3 is not None:
        # Clear all existing relationships (set foreign key to NULL)
        database.query(SkillMatch).filter(SkillMatch.user_3_id == db_user.id).update(
            {SkillMatch.user_3_id: None}, synchronize_session=False
        )

        # Set new relationships if list is not empty
        if user_data.skillmatch_3:
            # Validate that all IDs exist
            for skillmatch_id in user_data.skillmatch_3:
                db_skillmatch = database.query(SkillMatch).filter(SkillMatch.id == skillmatch_id).first()
                if not db_skillmatch:
                    raise HTTPException(status_code=400, detail=f"SkillMatch with id {skillmatch_id} not found")

            # Update the related entities with the new foreign key
            database.query(SkillMatch).filter(SkillMatch.id.in_(user_data.skillmatch_3)).update(
                {SkillMatch.user_3_id: db_user.id}, synchronize_session=False
            )
    database.commit()
    database.refresh(db_user)

    skillmatch_ids = database.query(SkillMatch.id).filter(SkillMatch.user_2_id == db_user.id).all()
    userskill_ids = database.query(UserSkill.id).filter(UserSkill.user_id == db_user.id).all()
    skillrequest_ids = database.query(SkillRequest.id).filter(SkillRequest.user_1_id == db_user.id).all()
    skillmatch_3_ids = database.query(SkillMatch.id).filter(SkillMatch.user_3_id == db_user.id).all()
    response_data = {
        "user": db_user,
        "skillmatch_ids": [x[0] for x in skillmatch_ids],        "userskill_ids": [x[0] for x in userskill_ids],        "skillrequest_ids": [x[0] for x in skillrequest_ids],        "skillmatch_3_ids": [x[0] for x in skillmatch_3_ids]    }
    return response_data


@app.delete("/user/{user_id}/", response_model=None, tags=["User"])
async def delete_user(user_id: int, database: DBSession = Depends(get_db)):
    db_user = database.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    database.delete(db_user)
    database.commit()
    return db_user







############################################
# Maintaining the server
############################################
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



