from sqlalchemy import Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped

from app.database.core import Base


class DocumentCollectionFile(Base):
    __tablename__ = "document_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    extension: Mapped[str] = mapped_column(String(10), nullable=False)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("document_collection.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('document_users.id', ondelete="SET NULL"), nullable=True, index=True)

    owner = relationship('DocumentUser', back_populates='files')
    document = relationship("DocumentCollection", back_populates="files")

    def __repr__(self):
        return f"<DocumentCollectionFile(id={self.id}, is_active={self.is_active}, document_id={self.document_id}, user_id={self.user_id})>"