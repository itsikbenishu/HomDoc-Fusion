from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from entities.common.base import Base
from entities.home_doc.models import HomeDocs

class ChattelsSpecsAttributes(Base):
    __tablename__ = "chattels_specs_attributes"

    id: Mapped[int] = mapped_column(primary_key=True)
    home_doc_id: Mapped[int] = mapped_column(ForeignKey("home_docs.id", ondelete="CASCADE"), unique=True)
    colors: Mapped[Optional[str]] = mapped_column(String)
    quantity: Mapped[Optional[str]] = mapped_column(String)
    weight: Mapped[Optional[str]] = mapped_column(String)

    home_doc: Mapped["HomeDocs"] = relationship()
