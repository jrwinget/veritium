from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Boolean
from sqlalchemy.sql import func
from app.db.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    authors = Column(JSON)
    abstract = Column(Text)
    content = Column(Text)
    doi = Column(String, unique=True, index=True, nullable=True)
    url = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    file_type = Column(String)  # pdf, docx, url

    # Extracted claims and conclusions
    extracted_claims = Column(JSON)
    confidence_score = Column(Float, default=0.0)
    method_quality_score = Column(Float, default=0.0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, index=True)
    user_claim = Column(Text)

    # Similarity and stance
    similarity_score = Column(Float, default=0.0)
    stance = Column(String)  # supports, contradicts, neutral
    entailment_score = Column(Float, default=0.0)

    # Component scores
    method_quality_score = Column(Float, default=0.0)
    evidence_strength_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)

    # Explanations and evidence
    explanation = Column(Text)
    evidence_snippets = Column(JSON)
    citations = Column(JSON)

    # Sharing and feedback
    share_id = Column(String, unique=True, index=True, nullable=True)
    feedback_score = Column(Integer, nullable=True)  # thumbs up/down
    feedback_comment = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
