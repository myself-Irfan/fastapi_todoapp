from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Text, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database.core import Base


class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    has_input = Column(Boolean, default=False)
    has_output = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="SET NULL"), nullable=True)

    owner = relationship('User', back_populates='documents')
    files = relationship("DocumentFile", back_populates="document", passive_deletes=True)

    @property
    def active_file(self):
        return next((f for f in self.files if f.is_active), None)

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', has_input={self.has_input}, has_output={self.has_output})>"

class DocumentFile(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    input_file_path = Column(String(500), nullable=False)
    input_file_size = Column(Integer, nullable=False)
    output_file_path = Column(String(500), nullable=True)
    output_file_size = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="SET NULL"), nullable=True)

    owner = relationship('User', back_populates='files')
    document = relationship("Document", back_populates="files")

    def __repr__(self):
        return f"<DocumentFile(id={self.id}, is_active={self.is_active}, document_id={self.document_id}, user_id={self.user_id})>"