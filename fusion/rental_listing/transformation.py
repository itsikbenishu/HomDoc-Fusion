from enum import Enum
from pydantic import BaseModel, Field, EmailStr, field_serializer
from typing import Optional, Dict
from datetime import datetime

class PropertyTypeEnum(str, Enum):
    single_family = "Single Family"
    Condo = "Condo"
    townhouse = "Townhouse" 
    manufactured = "Manufactured"	
    multi_family = "Multi-Family"
    apartment = "Apartment"
    land = "Land"

class ListingStatusEnum(str, Enum):
    active = "Active"
    inactive = "Inactive"

class ListingTypeEnum(str, Enum):
    standard = "Standard"
    new_construction = "New Construction"
    foreclosure = "Foreclosure"
    short_sale = "Short Sale"

class Contact(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None

class HOA(BaseModel):
    fee: Optional[float] = None

class HistoryItem(BaseModel):
    event: Optional[str] = None
    price: Optional[float] = None
    listingType: Optional[ListingTypeEnum] = None
    listedDate: Optional[datetime] = None
    removedDate: Optional[datetime] = None
    daysOnMarket: Optional[int] = None
    
class PropertyListing(BaseModel):
    rentcastId: str = Field(alias="id")
    interiorEntityKey: str = Field(alias="formattedAddress")
    county: Optional[str] = None
    propertyType: PropertyTypeEnum
    bedrooms: Optional[float] = None
    bathrooms: Optional[float] = None
    area: Optional[float] = Field(alias="squareFootage")
    lotSize: Optional[float] = None
    construction_Year: Optional[int] = Field(alias="yearBuilt")
    hoa: Optional[HOA] = None
    status: Optional[ListingStatusEnum] = None
    price: Optional[float] = None
    listingType: Optional[str] = None
    listedDate: Optional[datetime] = None
    removedDate: Optional[datetime] = None
    createdDate: Optional[datetime] = None
    lastSeenDate: Optional[datetime] = None
    daysOnMarket: Optional[int] = None
    mlsName: Optional[str] = None
    mlsNumber: Optional[str] = None
    listingAgent: Optional[Contact] = None
    listingOffice: Optional[Contact] = None
    history: Optional[Dict[str, HistoryItem]] = None

    @field_serializer("area")
    def serialize_square_footage(self, value):
        if value is None:
            return value
        return round(value * 0.092903, 2)

    @field_serializer("lotSize")
    def serialize_lot_size(self, value):
        if value is None:
            return value
        return round(value * 0.092903, 2)




def filter_fields(property_listing):
    exclude_fields = { "addressLine1", "addressLine2", "city", "state", "zipCode",  "builder", "latitude", "longitude" }

    filtered_fields = {
        field: value for field, value in property_listing.items() if field not in exclude_fields
    }

    return filtered_fields


property_listing_transform = lambda property_listing: PropertyListing(**filter_fields(property_listing))

