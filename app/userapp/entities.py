from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from app.database.core import Base


class DocumentUser(Base):
    __tablename__ = 'document_users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_pwd = Column(String(250), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    documents = relationship('DocumentCollection', back_populates='owner')
    files = relationship('DocumentCollectionFile', back_populates="owner")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"