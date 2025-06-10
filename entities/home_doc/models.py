from typing import Optional, List, Dict
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy import Enum, Column, JSON, func
from entities.common.enums import HomeDocCategoriesEnum, HomeDocTypeEnum
from pydantic import ConfigDict 

class HomeDoc(SQLModel, table=True):
    __tablename__ = "home_docs"

    id: int = Field(default=None, primary_key=True)
    father_id: Optional[int] = Field(
        default=None,
        foreign_key="home_docs.id",
        ondelete="CASCADE",
        alias="fatherId",
        sa_column_kwargs={"name": "fatherId"}
    )
    external_id: Optional[str] = Field(
        default=None,
        alias="externalId",
        sa_column_kwargs={"name": "externalId"}
    )
    interior_entity_key: str = Field(
        nullable=False,
        alias="interiorEntityKey",
        sa_column_kwargs={"name": "interiorEntityKey"}
    )
    father_interior_entity_key: Optional[str] = Field(
        default=None,
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
    extra_data: Optional[List[Dict[str, str]]] = Field(
        default=[],
        alias="extraData",
        sa_column=Column(JSON, name="extraData")
    )    
    listing_agent_id: Optional[int] = Field(default=None, foreign_key="listing_contact.id", ondelete="SET NULL")    
    listing_office_id: Optional[int] = Field(default=None, foreign_key="listing_contact.id", ondelete="SET NULL")
    
    father: Optional["HomeDoc"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "HomeDoc.id"}
    )
    
    children: List["HomeDoc"] = Relationship(back_populates="father")

    specs: Optional["ResidenceSpecsAttributes"] = Relationship(
        back_populates="home_doc",
        sa_relationship_kwargs={"uselist": False}
    )
    listing: Optional["Listing"] = Relationship(
        back_populates="home_doc"
    )
    listing_agent: Optional["ListingContact"] = Relationship(
        back_populates="agent_for_home_docs",
        sa_relationship_kwargs={"foreign_keys": "[HomeDoc.listing_agent_id]"}
    )
    listing_office: Optional["ListingContact"] = Relationship(
        back_populates="office_for_home_docs",
        sa_relationship_kwargs={"foreign_keys": "[HomeDoc.listing_office_id]"}
    )
    listing_history: List["ListingHistory"] = Relationship(
        back_populates="residence"
    )

    dimensions: Optional["HomeDocDimensions"] = Relationship(
        back_populates="home_doc",
        sa_relationship_kwargs={"uselist": False}
    )

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True
    )


class HomeDocRelations(SQLModel, table=True):
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

    home_doc: Optional["HomeDoc"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[HomeDocRelations.home_doc_id]"}
    )

    sub_home_doc: Optional["HomeDoc"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[HomeDocRelations.sub_home_doc_id]"}
    )

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True
    )


class HomeDocDimensions(SQLModel, table=True):
    __tablename__ = "home_docs_dimensions"

    id: Optional[int] = Field(default=None, primary_key=True)
    home_doc_id: int = Field(
        foreign_key="home_docs.id",
        ondelete="CASCADE",
        unique=True,
        alias="homeDocId",
        sa_column_kwargs={"name": "homeDocId"}
    )
    
    length: Optional[int] = Field(default=None)
    width: Optional[int] = Field(default=None)

    home_doc: Optional["HomeDoc"] = Relationship(back_populates="dimensions")

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True
    )

from entities.residence.models import ResidenceSpecsAttributes, ListingContact, ListingHistory, Listing

HomeDoc.model_rebuild()
