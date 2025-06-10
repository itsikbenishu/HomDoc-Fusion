from typing import Optional, List, Dict
from sqlmodel import SQLModel, Field, Relationship, Enum, Column
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


class ListingContactResponse(SQLModel):
    id: int
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None

class ListingHistoryResponse(SQLModel):
    id: int
    event: Optional[str] = None
    price: Optional[float] = None
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
class ListingResponse(SQLModel):
    id: int
    price: Optional[float] = None
    hoa_fee: Optional[float] = None
    bedrooms: Optional[float] = None
    bathrooms: Optional[float] = None
    status: ListingStatusEnum

class HomeDocChildResponse(SQLModel):
    id: int
    interior_entity_key: str
    type: str

class ResidenceResponse(SQLModel):
    id: int
    father_id: Optional[int] = None
    external_id: Optional[str] = None
    interior_entity_key: str
    father_interior_entity_key: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    category: str
    type: str
    description: Optional[str] = None
    extra_data: Optional[List[Dict[str, str]]] = Field(default_factory=list)

    area: Optional[float] = None
    sub_entities_quantity: Optional[int] = None
    construction_year: Optional[int] = None

    length: Optional[int] = None
    width: Optional[int] = None

    listing: Optional[ListingResponse] = None
    
    listing_agent: Optional[ListingContactResponse] = None
    listing_office: Optional[ListingContactResponse] = None
    
    listing_history: List[ListingHistoryResponse] = Field(default_factory=list)

    children: List[HomeDocChildResponse] = Field(default_factory=list)

    @classmethod
    def from_models(
        cls,
        home_doc: HomeDoc,
        specs: Optional[ResidenceSpecsAttributes] = None,
        dimensions: Optional[HomeDocDimensions] = None,
        listing: Optional[Listing] = None,
        listing_agent: Optional[ListingContact] = None,
        listing_office: Optional[ListingContact] = None,
        listing_history: Optional[List[ListingHistory]] = None
    ) -> "ResidenceResponse":
        
        children_responses = []
        if home_doc.children:
            for child in home_doc.children:
                child_response = HomeDocChildResponse(
                    id=child.id,
                    interior_entity_key=child.interior_entity_key,
                    type=child.type,
                )
                children_responses.append(child_response)

        listing_response = None
        if listing:
            listing_response = ListingResponse(
                id=listing.id,
                price=listing.price,
                hoa_fee=listing.hoa_fee,
                bedrooms=listing.bedrooms,
                bathrooms=listing.bathrooms,
                status=listing.status
            )

        agent_response = None
        if listing_agent:
            agent_response = ListingContactResponse(
                id=listing_agent.id,
                name=listing_agent.name,
                phone=listing_agent.phone,
                email=listing_agent.email,
                website=listing_agent.website
            )

        office_response = None
        if listing_office:
            office_response = ListingContactResponse(
                id=listing_office.id,
                name=listing_office.name,
                phone=listing_office.phone,
                email=listing_office.email,
                website=listing_office.website
            )

        history_responses = []
        if listing_history:
            for history_item in listing_history:
                history_response = ListingHistoryResponse(
                    id=history_item.id,
                    event=history_item.event,
                    price=history_item.price,
                    listing_type=history_item.listing_type,
                    listed_date=history_item.listed_date,
                    removed_date=history_item.removed_date,
                    days_on_market=history_item.days_on_market
                )
                history_responses.append(history_response)

        return cls(
            id=home_doc.id,
            father_id=home_doc.father_id,
            external_id=home_doc.external_id,
            interior_entity_key=home_doc.interior_entity_key,
            father_interior_entity_key=home_doc.father_interior_entity_key,
            created_at=home_doc.created_at,
            updated_at=home_doc.updated_at,
            category=home_doc.category,
            type=home_doc.type,
            description=home_doc.description,
            extra_data=home_doc.extra_data or [],
            area=specs.area if specs else None,
            sub_entities_quantity=specs.sub_entities_quantity if specs else None,
            construction_year=specs.construction_year if specs else None,
            length=dimensions.length if dimensions else None,
            width=dimensions.width if dimensions else None,
            listing=listing_response,
            listing_agent=agent_response,
            listing_office=office_response,
            listing_history=history_responses,
            children=children_responses
        )
