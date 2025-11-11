from sqlalchemy import Integer, String, DateTime, func, Text, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped

from app.database.core import Base


class DocumentCollection(Base):
    __tablename__ = 'document_collection'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('document_users.id', ondelete="SET NULL"), nullable=True)

    owner = relationship('DocumentUser', back_populates='documents')
    files = relationship("DocumentCollectionFile", back_populates="document", passive_deletes=True)

    def __repr__(self):
        return f"<DocumentCollection(id={self.id}, title='{self.title}')>"