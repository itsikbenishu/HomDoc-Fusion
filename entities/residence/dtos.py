from datetime import datetime
from typing import Optional, List, Dict
from pydantic import Field, field_validator
from entities.abstracts.camel_model import CamelModel
from entities.home_doc.models import HomeDoc, HomeDocDimensions
from entities.residence.models import ListingContact, ListingHistory, ResidenceSpecsAttributes, Listing
from entities.common.enums import HomeDocTypeEnum, ListingTypeEnum, ListingStatusEnum, HomeDocCategoriesEnum

class ListingContactResponse(CamelModel):
    id: int
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None


class ListingHistoryResponse(CamelModel):
    id: int
    event: Optional[str] = None
    price: Optional[float] = None
    listing_type: Optional[ListingTypeEnum] = None
    listed_date: Optional[datetime] = None
    removed_date: Optional[datetime] = None
    days_on_market: Optional[int] = None


class HomeDocChildResponse(CamelModel):
    id: int
    interior_entity_key: str
    type: str


class ResidenceResponse(CamelModel):
    id: int
    father_id: Optional[int] = None
    external_id: Optional[str] = None
    interior_entity_key: str
    father_interior_entity_key: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    category: HomeDocCategoriesEnum
    type: HomeDocTypeEnum
    description: Optional[str] = None
    extra_data: Optional[List[Dict[str, str]]] = Field(default_factory=list)

    area: Optional[float] = None
    sub_entities_quantity: Optional[int] = None
    construction_year: Optional[int] = None

    length: Optional[float] = None
    width: Optional[float] = None

    price: Optional[float] = None
    hoa_fee: Optional[float] = None
    bedrooms: Optional[float] = None
    bathrooms: Optional[float] = None
    listing_status: ListingStatusEnum

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
                children_responses.append(HomeDocChildResponse(
                    id=child.id,
                    interior_entity_key=child.interior_entity_key,
                    type=child.type,
                ))

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
                history_responses.append(ListingHistoryResponse(
                    id=history_item.id,
                    event=history_item.event,
                    price=history_item.price,
                    listing_type=history_item.listing_type,
                    listed_date=history_item.listed_date,
                    removed_date=history_item.removed_date,
                    days_on_market=history_item.days_on_market
                ))

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
            price=listing.price if listing else None,
            hoa_fee=listing.hoa_fee if listing else None,
            bedrooms=listing.bedrooms if listing else None,
            bathrooms=listing.bathrooms if listing else None,
            listing_status=listing.listing_status if listing else ListingStatusEnum.inactive,
            listing_agent=agent_response,
            listing_office=office_response,
            listing_history=history_responses,
            children=children_responses
            
        )


class ListingContactCreate(CamelModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None


class ListingHistoryCreate(CamelModel):
    event: Optional[str] = None
    price: Optional[float] = None
    listing_type: Optional[ListingTypeEnum] = None
    listed_date: Optional[datetime] = None
    removed_date: Optional[datetime] = None
    days_on_market: Optional[int] = None


class ResidenceCreate(CamelModel):
    external_id: Optional[str] = None
    interior_entity_key: str
    category: HomeDocCategoriesEnum
    type: HomeDocTypeEnum
    description: Optional[str] = None
    extra_data: Optional[List[Dict[str, str]]] = Field(default_factory=list)

    area: Optional[float] = None
    sub_entities_quantity: Optional[int] = None
    construction_year: Optional[int] = None

    length: Optional[int] = None
    width: Optional[int] = None

    price: Optional[float] = None
    hoa_fee: Optional[float] = None
    bedrooms: Optional[float] = None
    bathrooms: Optional[float] = None
    listing_status: ListingStatusEnum

    listing_agent: Optional[ListingContactCreate] = None
    listing_office: Optional[ListingContactCreate] = None

    listing_history: List[ListingHistoryCreate] = Field(default_factory=list)

    @field_validator('interior_entity_key')
    @classmethod
    def validate_interior_entity_key(cls, v):
        if not v or not v.strip():
            raise ValueError('interior_entity_key cannot be empty')
        return v.strip()

    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        if not v or not v.strip():
            raise ValueError('type cannot be empty')
        if v not in [
            HomeDocTypeEnum.PROPERTY,
            HomeDocTypeEnum.FLOOR,
            HomeDocTypeEnum.APARTMENT,
            HomeDocTypeEnum.ROOM
        ]:
            raise ValueError('type of residence must be one of: PROPERTY, FLOOR, APARTMENT, ROOM')
        return v


class ListingContactUpdate(CamelModel):
    id: int
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None


class ListingHistoryUpdate(CamelModel):
    event: Optional[str] = None
    price: Optional[float] = None
    listing_type: Optional[ListingTypeEnum] = None
    listed_date: Optional[datetime] = None
    removed_date: Optional[datetime] = None
    days_on_market: Optional[int] = None


class ResidenceUpdate(CamelModel):
    external_id: Optional[str] = None
    description: Optional[str] = None
    extra_data: Optional[List[Dict[str, str]]] = Field(default_factory=list)

    area: Optional[float] = None
    sub_entities_quantity: Optional[int] = None
    construction_year: Optional[int] = None

    length: Optional[int] = None
    width: Optional[int] = None

    price: Optional[float] = None
    hoa_fee: Optional[float] = None
    bedrooms: Optional[float] = None
    bathrooms: Optional[float] = None
    listing_status: ListingStatusEnum

    listing_agent: Optional[ListingContactUpdate] = None
    listing_office: Optional[ListingContactUpdate] = None

    listing_history: List[ListingHistoryUpdate] = Field(default_factory=list)

    @field_validator('listing_status')
    @classmethod
    def validate_status(cls, v):
        if not v:
            raise ValueError('listing status cannot be empty')
        return v
