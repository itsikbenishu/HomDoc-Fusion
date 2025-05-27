from enum import Enum
from pydantic import BaseModel, EmailStr
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


class Builder(BaseModel):
    name: Optional[str] = None
    development: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    
class PropertyListing(BaseModel):
    id: str
    formattedAddress: str
    addressLine1: Optional[str]
    addressLine2: Optional[str]
    city: Optional[str] = None
    state: str
    zipCode: Optional[str] = None
    county: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    propertyType: PropertyTypeEnum
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    squareFootage: Optional[int] = None
    lotSize: Optional[int] = None
    yearBuilt: Optional[int] = None
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
    builder: Optional[Builder] = None
    history: Optional[Dict[str, HistoryItem]] = None

property_listing_transfom = lambda property_listing: PropertyListing(**property_listing)

