from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy import Enum, Column, JSON, func
from entities.common.enums import HomeDocCategoriesEnum, HomeDocTypeEnum
from pydantic import ConfigDict 

class HomeDocs(SQLModel, table=True):
    __tablename__ = "home_docs"

    id: int = Field(default=None, primary_key=True)
    father_id: Optional[int] = Field(
        default=None,
        foreign_key="home_docs.id",
        ondelete="CASCADE",
        alias="fatherId",
        sa_column_kwargs={"name": "fatherId"}
    )
    interior_entity_key: str = Field(
        nullable=False,
        alias="interiorEntityKey",
        sa_column_kwargs={"name": "interiorEntityKey"}
    )
    father_interior_entity_key: str = Field(
        nullable=False,
        alias="fatherInteriorEntityKey",
        sa_column_kwargs={"name": "fatherInteriorEntityKey"}
    )
    created_at: Optional[datetime] = Field(
        default=None,
        alias="createdAt",
        sa_column_kwargs={"name": "createdAt", "server_default": func.now()}
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        alias="updatedAt",
        sa_column_kwargs={"name": "updatedAt", "server_default": func.now()}
    )
    category: HomeDocCategoriesEnum = Field(
        sa_column=Enum(HomeDocCategoriesEnum),
    )
    type: HomeDocTypeEnum = Field(
        sa_column=Enum(HomeDocTypeEnum),
    )
    description: Optional[str] = Field(default=None)
    extra_data: Optional[dict] = Field(
        default=None,
        alias="extraData",
        sa_column=Column(JSON, name="extraData")
    )

    father: Optional["HomeDocs"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "HomeDocs.id"}
    )
    children: List["HomeDocs"] = Relationship(back_populates="father")

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True
    )


class HomeDocsRelations(SQLModel, table=True):
    __tablename__ = "home_docs_relations"

    id: Optional[int] = Field(default=None, primary_key=True)
    home_doc_id: int = Field(
        foreign_key="home_docs.id",
        ondelete="CASCADE",
        alias="homeDocId",
        sa_column_kwargs={"name": "homeDocId"}
    )
    sub_home_doc_id: int = Field(
        foreign_key="home_docs.id",
        ondelete="CASCADE",
        alias="subHomeDocId",
        sa_column_kwargs={"name": "subHomeDocId"}
    )

    home_doc: Optional["HomeDocs"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[HomeDocsRelations.home_doc_id]"}
    )

    sub_home_doc: Optional["HomeDocs"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[HomeDocsRelations.sub_home_doc_id]"}
    )

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True
    )


class HomeDocsDimensions(SQLModel, table=True):
    __tablename__ = "home_docs_dimensions"

    id: Optional[int] = Field(default=None, primary_key=True)
    home_doc_id: int = Field(
        foreign_key="home_docs.id",
        ondelete="CASCADE",
        unique=True,
        alias="homeDocId",
        sa_column_kwargs={"name": "homeDocId"}
    )
    length: Optional[str] = Field(default=None)
    width: Optional[str] = Field(default=None)

    home_doc: Optional["HomeDocs"] = Relationship()

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True
    )
