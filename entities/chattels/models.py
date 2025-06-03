from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Enum, JSON, func
from entities.home_doc.models import HomeDocs
from pydantic import ConfigDict 


class ChattelsSpecsAttributes(SQLModel, table=True):
    __tablename__ = "chattels_specs_attributes"

    id: int = Field(default=None, primary_key=True)
    home_doc_id: int = Field(
        foreign_key="home_docs.id",
        ondelete="CASCADE",
        alias="homeDocId",
        sa_column_kwargs={"name": "homeDocId"}
    )
    colors: Optional[str] = Field(default=None)
    quantity: Optional[str] = Field(default=None)
    weight: Optional[str] = Field(default=None)

    home_doc: Optional["HomeDocs"] = Relationship()

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True
    )
