from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .connection import Base


class PersonDB(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    face_encodings = relationship("FaceEncodingDB", back_populates="person", cascade="all, delete-orphan")


class FaceEncodingDB(Base):
    __tablename__ = "face_encodings"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"))
    encoding = Column(LargeBinary)  # Store numpy array as binary
    image_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    person = relationship("PersonDB", back_populates="face_encodings")