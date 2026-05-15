"""
PostgreSQL database layer for job persistence.

Used in production (Railway) when DATABASE_URL is set.
Falls back to JSON file persistence when DATABASE_URL is not set (local dev).
"""

import os
import json
import logging
from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Boolean,
    DateTime,
    Integer,
    ForeignKey,
    Text,
    text,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

logger = logging.getLogger(__name__)

Base = declarative_base()
_engine = None
_SessionLocal = None


# ── Table definitions ──────────────────────────────────────────────


class JobRow(Base):
    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True)
    status = Column(String, nullable=False, default="created")
    created_at = Column(DateTime, nullable=False)
    timestamp = Column(String, nullable=False)
    candidate_file = Column(String)
    columns = Column(Text)          # JSON list
    is_allocated = Column(Boolean, default=False)
    allocated_path = Column(String)
    template_id = Column(String)
    pdf_folder = Column(String)
    log_path = Column(String)
    cancelled = Column(Boolean, default=False)
    paused = Column(Text)           # JSON dict
    tasks = Column(Text)            # JSON dict


class CandidateRow(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False, index=True)
    data = Column(Text, nullable=False)  # JSON dict – one candidate row


# ── Init ───────────────────────────────────────────────────────────


def get_database_url() -> str | None:
    """Return DATABASE_URL if set, else None."""
    return os.getenv("DATABASE_URL")


def init_db():
    """Create engine, session factory, and tables if DATABASE_URL is set."""
    global _engine, _SessionLocal

    url = get_database_url()
    if not url:
        logger.info("DATABASE_URL not set – using JSON file persistence")
        return

    # Railway sometimes gives postgres:// but SQLAlchemy needs postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    _engine = create_engine(url, pool_pre_ping=True)
    _SessionLocal = sessionmaker(bind=_engine)

    Base.metadata.create_all(_engine)
    logger.info("Database tables created / verified")


def _get_session() -> Session | None:
    """Return a new DB session, or None if DB is not configured."""
    if _SessionLocal is None:
        return None
    return _SessionLocal()


def db_available() -> bool:
    """True when a DATABASE_URL is configured and the engine is ready."""
    return _engine is not None


# ── CRUD helpers ───────────────────────────────────────────────────


def save_job_to_db(job_dict: dict, candidates_data: list[dict] | None = None):
    """
    Upsert a job row and optionally replace its candidate rows.

    Parameters
    ----------
    job_dict : dict
        Output of Job.to_dict().
    candidates_data : list[dict] | None
        List of row-dicts (one per candidate).  If provided the existing
        candidate rows for this job are replaced.
    """
    session = _get_session()
    if session is None:
        return

    try:
        existing = session.get(JobRow, job_dict["job_id"])

        row_data = {
            "job_id": job_dict["job_id"],
            "status": job_dict["status"],
            "created_at": datetime.fromisoformat(job_dict["created_at"]),
            "timestamp": job_dict["timestamp"],
            "candidate_file": job_dict.get("candidate_file"),
            "columns": json.dumps(job_dict.get("columns", [])),
            "is_allocated": job_dict.get("is_allocated", False),
            "allocated_path": job_dict.get("allocated_path"),
            "template_id": job_dict.get("template_id"),
            "pdf_folder": job_dict.get("pdf_folder"),
            "log_path": job_dict.get("log_path"),
            "cancelled": job_dict.get("cancelled", False),
            "paused": json.dumps(job_dict.get("paused", {})),
            "tasks": json.dumps(job_dict.get("tasks", {})),
        }

        if existing:
            for key, value in row_data.items():
                setattr(existing, key, value)
        else:
            session.add(JobRow(**row_data))

        # Replace candidate rows when data is provided
        if candidates_data is not None:
            session.execute(
                text("DELETE FROM candidates WHERE job_id = :jid"),
                {"jid": job_dict["job_id"]},
            )
            for row in candidates_data:
                session.add(CandidateRow(
                    job_id=job_dict["job_id"],
                    data=json.dumps(row, default=str),
                ))

        session.commit()
    except Exception:
        session.rollback()
        logger.exception("Failed to save job %s to DB", job_dict["job_id"])
        raise
    finally:
        session.close()


def load_job_from_db(job_id: str) -> dict | None:
    """
    Load a single job + its candidates from the DB.

    Returns a dict with keys matching Job.to_dict() plus an extra
    ``"candidates"`` key containing a list[dict].
    """
    session = _get_session()
    if session is None:
        return None

    try:
        row = session.get(JobRow, job_id)
        if row is None:
            return None

        job_dict = _row_to_dict(row)

        candidates = (
            session.query(CandidateRow)
            .filter(CandidateRow.job_id == job_id)
            .order_by(CandidateRow.id)
            .all()
        )
        job_dict["candidates"] = [json.loads(c.data) for c in candidates]
        return job_dict
    finally:
        session.close()


def load_all_jobs_from_db() -> list[dict]:
    """
    Load every job (with candidates) from the DB.

    Returns a list of dicts, each shaped like load_job_from_db output.
    """
    session = _get_session()
    if session is None:
        return []

    try:
        rows = session.query(JobRow).all()
        results = []
        for row in rows:
            job_dict = _row_to_dict(row)

            candidates = (
                session.query(CandidateRow)
                .filter(CandidateRow.job_id == row.job_id)
                .order_by(CandidateRow.id)
                .all()
            )
            job_dict["candidates"] = [json.loads(c.data) for c in candidates]
            results.append(job_dict)

        return results
    finally:
        session.close()


def delete_job_from_db(job_id: str):
    """Delete a job and its candidates from the DB."""
    session = _get_session()
    if session is None:
        return

    try:
        # Candidates are CASCADE-deleted via FK, but be explicit
        session.execute(
            text("DELETE FROM candidates WHERE job_id = :jid"),
            {"jid": job_id},
        )
        session.execute(
            text("DELETE FROM jobs WHERE job_id = :jid"),
            {"jid": job_id},
        )
        session.commit()
    except Exception:
        session.rollback()
        logger.exception("Failed to delete job %s from DB", job_id)
        raise
    finally:
        session.close()


# ── Internal helpers ───────────────────────────────────────────────


def _row_to_dict(row: JobRow) -> dict:
    """Convert a JobRow ORM instance to a plain dict."""
    return {
        "job_id": row.job_id,
        "status": row.status,
        "created_at": row.created_at.isoformat(),
        "timestamp": row.timestamp,
        "candidate_file": row.candidate_file,
        "columns": json.loads(row.columns) if row.columns else [],
        "is_allocated": row.is_allocated,
        "allocated_path": row.allocated_path,
        "template_id": row.template_id,
        "pdf_folder": row.pdf_folder,
        "log_path": row.log_path,
        "cancelled": row.cancelled,
        "paused": json.loads(row.paused) if row.paused else {},
        "tasks": json.loads(row.tasks) if row.tasks else {},
    }
