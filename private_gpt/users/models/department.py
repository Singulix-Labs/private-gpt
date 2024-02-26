from sqlalchemy import ForeignKey, event
from sqlalchemy.orm import relationship, Session
from sqlalchemy import Column, Integer, String

from private_gpt.users.db.base_class import Base

class Department(Base):
    """Models a Department table."""

    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)

    company_id = Column(Integer, ForeignKey('companies.id'))
    company = relationship("Company", back_populates="departments")

    users = relationship("User", back_populates="department")
    documents = relationship("Document", back_populates="department")

    total_users = Column(Integer, default=0)
    total_documents = Column(Integer, default=0)
