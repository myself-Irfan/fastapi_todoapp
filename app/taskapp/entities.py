from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Text, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database.core import Base


class DocumentCollection(Base):
    __tablename__ = 'document_collection'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    user_id = Column(Integer, ForeignKey('document_users.id', ondelete="SET NULL"), nullable=True)

    owner = relationship('DocumentUser', back_populates='documents')
    files = relationship("DocumentCollectionFile", back_populates="document", passive_deletes=True)

    def __repr__(self):
        return f"<DocumentCollection(id={self.id}, title='{self.title}')>"

class DocumentCollectionFile(Base):
    __tablename__ = "document_files"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    file_path = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    extension = Column(String(10), nullable=False)
    checksum = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    document_id = Column(Integer, ForeignKey("document_collection.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey('document_users.id', ondelete="SET NULL"), nullable=True, index=True)

    owner = relationship('DocumentUser', back_populates='files')
    document = relationship("DocumentCollection", back_populates="files")

    def __repr__(self):
        return f"<DocumentCollectionFile(id={self.id}, is_active={self.is_active}, document_id={self.document_id}, user_id={self.user_id})>"