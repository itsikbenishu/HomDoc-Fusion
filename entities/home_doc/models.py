from typing import Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from entities.common.enums_T import HomeDocCategoriesEnum, HomeDocTypeEnum
from entities.common.base_T import Base

class HomeDocs(Base):
    __tablename__ = "home_docs"

    id: Mapped[int] = mapped_column(primary_key=True)
    father_id: Mapped[Optional[int]] = mapped_column(ForeignKey("home_docs.id", ondelete="CASCADE"))
    interior_entity_key: Mapped[str] = mapped_column(String)
    father_interior_entity_key: Mapped[str] = mapped_column(String)
    created_at: Mapped[Optional[DateTime]] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(server_default=func.now())
    category: Mapped[HomeDocCategoriesEnum] = mapped_column(Enum(HomeDocCategoriesEnum))
    type: Mapped[HomeDocTypeEnum] = mapped_column(Enum(HomeDocTypeEnum))
    description: Mapped[Optional[str]] = mapped_column(String)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)

    father: Mapped[Optional["HomeDocs"]] = relationship("HomeDocs", remote_side=[id], backref="children")

class HomeDocsRelations(Base):
    __tablename__ = "home_docs_relations"

    id: Mapped[int] = mapped_column(primary_key=True)
    home_doc_id: Mapped[int] = mapped_column(ForeignKey("home_docs.id", ondelete="CASCADE"))
    sub_home_doc_id: Mapped[int] = mapped_column(ForeignKey("home_docs.id", ondelete="CASCADE"))

    home_doc: Mapped["HomeDocs"] = relationship(foreign_keys=[home_doc_id])
    sub_home_doc: Mapped["HomeDocs"] = relationship(foreign_keys=[sub_home_doc_id])

class HomeDocsDimensions(Base):
    __tablename__ = "home_docs_dimensions"

    id: Mapped[int] = mapped_column(primary_key=True)
    home_doc_id: Mapped[int] = mapped_column(ForeignKey("home_docs.id", ondelete="CASCADE"), unique=True)
    length: Mapped[Optional[str]] = mapped_column(String)
    width: Mapped[Optional[str]] = mapped_column(String)

    home_doc: Mapped["HomeDocs"] = relationship()

