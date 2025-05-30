from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Enum, JSON, func
from entities.home_doc.models import HomeDocs
from pydantic import ConfigDict 

class ResidenceSpecsAttributes(SQLModel, table=True):
    __tablename__ = "residence_specs_attributes"

    id: int = Field(default=None, primary_key=True)
    home_doc_id: int = Field(
        foreign_key="home_docs.id",
        ondelete="CASCADE",
        alias="homeDocId"
    )
    area: Optional[str] = Field(default=None)
    sub_Entities_quantity: Optional[str] = Field(default=None)
    construction_year: Optional[str] = Field(default=None)

    home_doc: Optional["HomeDocs"] = Relationship()

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True
    )
