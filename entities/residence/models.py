from typing import Optional, List, Dict
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from entities.home_doc.models import HomeDoc, HomeDocDimensions
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
        alias="homeDocId",
        sa_column_kwargs={"name": "homeDocId"}
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
        alias="listingStatus",
        sa_column_kwargs={"name": "status"}
    )

    home_doc: Optional["HomeDoc"] = Relationship(back_populates="listing") 
    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True
    )

Listing.model_rebuild()

class ListingContact(SQLModel, table=True):
    __tablename__ = "listing_contact"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    phone: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    website: Optional[str] = Field(default=None)

    agent_for_home_docs: List["HomeDoc"] = Relationship(back_populates="listing_agent")
    office_for_home_docs: List["HomeDoc"] = Relationship(back_populates="listing_office")

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
        sa_column_kwargs={"name": "listingType"}
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
        ondelete="CASCADE"
    )
    residence: "HomeDoc" = Relationship(back_populates="listing_history")

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True
    )


ListingHistory.model_rebuild()


class ResidenceResponse(SQLModel):
    id: int
    interior_entity_key: str
    father_interior_entity_key: Optional[str] = None
    category: str
    type: str
    description: Optional[str] = None
    extra_data: Optional[List[Dict[str, str]]] = Field(default_factory=list)

    area: Optional[float] = None
    sub_entities_quantity: Optional[int] = None
    construction_year: Optional[int] = None

    length: Optional[int] = None
    width: Optional[int] = None

    children: List[HomeDoc] = Field(default=list)

    @classmethod
    def from_models(
        cls,
        home_doc: HomeDoc,
        specs: ResidenceSpecsAttributes,
        dimensions: Optional[HomeDocDimensions] = None
    ) -> "ResidenceResponse":
        return cls(
            id=home_doc.id,
            interior_entity_key=home_doc.interior_entity_key,
            father_interior_entity_key=home_doc.father_interior_entity_key,
            category=home_doc.category,
            type=home_doc.type,
            description=home_doc.description,
            extra_data=home_doc.extra_data,
            area=specs.area if specs else None,
            sub_entities_quantity=specs.sub_entities_quantity if specs else None,
            construction_year=specs.construction_year if specs else None,
            length=dimensions.length if dimensions else None,
            width=dimensions.width if dimensions else None,
            children=home_doc.children
        )
