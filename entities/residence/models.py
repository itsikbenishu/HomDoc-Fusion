from typing import Optional, List, Dict
from sqlmodel import SQLModel, Field, Relationship, Enum, Column
from datetime import datetime
from entities.home_doc.models import HomeDoc
from entities.common.enums import ListingStatusEnum, ListingTypeEnum
from pydantic import ConfigDict

class ResidenceSpecsAttributes(SQLModel, table=True):
    __tablename__ = "residence_specs_attributes"

    id: int = Field(default=None, primary_key=True)
    home_doc_id: int = Field(
        foreign_key="home_docs.id",
        ondelete="CASCADE",
        alias="homeDocId",
        sa_column_kwargs={"name": "homeDocId"}
    )
    area: Optional[float] = Field(default=None)
    sub_entities_quantity: Optional[int] = Field(
        default=None,
        alias="subEntitiesQuantity",
        sa_column_kwargs={"name": "subEntitiesQuantity"}
    )
    construction_year: Optional[int] = Field(
        default=None,
        alias="constructionYear",
        sa_column_kwargs={"name": "constructionYear"}
    )

    home_doc: Optional["HomeDoc"] = Relationship(back_populates="specs")

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True
    )

class Listing(SQLModel, table=True):
    __tablename__ = "listings"

    id: int = Field(default=None, primary_key=True)
    residence_id: int = Field(
        foreign_key="home_docs.id",
        ondelete="CASCADE",
        alias="residenceId",
        sa_column_kwargs={"name": "residenceId"}
    )
    price: Optional[float] = Field(default=None)
    hoa_fee: Optional[float] = Field(
        default=None,
        alias="hoaFee",
        sa_column_kwargs={"name": "hoaFee"}
    )
    bedrooms: Optional[float] = Field(default=None)
    bathrooms: Optional[float] = Field(default=None)
    status: ListingStatusEnum = Field(
        default=ListingStatusEnum.inactive,
        sa_column=Enum(ListingStatusEnum, name='listing_status_enum'),
        alias="listingStatus"
    )
    home_doc: Optional["HomeDoc"] = Relationship(back_populates="listing") 
    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True
    )

Listing.model_rebuild()

class ListingContact(SQLModel, table=True):
    __tablename__ = "listing_contact"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    phone: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    website: Optional[str] = Field(default=None)

    agent_for_home_docs: List["HomeDoc"] = Relationship(
        back_populates="listing_agent",
        sa_relationship_kwargs={"foreign_keys": "[HomeDoc.listing_agent_id]"}
    )

    office_for_home_docs: List["HomeDoc"] = Relationship(
        back_populates="listing_office",
        sa_relationship_kwargs={"foreign_keys": "[HomeDoc.listing_office_id]"}
    )


    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True
    )

ListingContact.model_rebuild()

class ListingHistory(SQLModel, table=True):
    __tablename__ = "listing_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    event: Optional[str] = Field(default=None)
    price: Optional[float] = Field(default=None)
    listing_type: Optional[ListingTypeEnum] = Field(
        default=None,
        alias="listingType",
        sa_column=Column("listingType", Enum(ListingTypeEnum, name="listing_type_enum", values_callable=lambda obj: [e.value for e in obj]))
    )
    listed_date: Optional[datetime] = Field(
        default=None,
        alias="listedDate",
        sa_column_kwargs={"name": "listedDate"}
    )
    removed_date: Optional[datetime] = Field(
        default=None,
        alias="removedDate",
        sa_column_kwargs={"name": "removedDate"}
    )
    days_on_market: Optional[int] = Field(
        default=None,
        alias="daysOnMarket",
        sa_column_kwargs={"name": "daysOnMarket"}
    )

    residence_id: int = Field(
        foreign_key="home_docs.id",
        ondelete="CASCADE",
        alias="residenceId",
        sa_column_kwargs={"name": "residenceId"}
    )
    residence: "HomeDoc" = Relationship(back_populates="listing_history")

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True
    )


ListingHistory.model_rebuild()
