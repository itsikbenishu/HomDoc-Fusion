from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from entities.common.base import Base
from entities.home_doc.models import HomeDocs

class ResidenceSpecsAttributes(Base):
    __tablename__ = "residence_specs_attributes"

    id: Mapped[int] = mapped_column(primary_key=True)
    home_doc_id: Mapped[int] = mapped_column(ForeignKey("home_docs.id", ondelete="CASCADE"), unique=True)
    area: Mapped[Optional[str]] = mapped_column(String)
    sub_Entities_quantity: Mapped[Optional[str]] = mapped_column(String)
    construction_year: Mapped[Optional[str]] = mapped_column(String)

    home_doc: Mapped["HomeDocs"] = relationship()
