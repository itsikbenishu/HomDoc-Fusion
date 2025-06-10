import enum

class HomeDocCategoriesEnum(str, enum.Enum):
    ONE_STORY_HOUSE = "ONE_STORY_HOUSE"
    RESIDENTIAL_BUILDING = "RESIDENTIAL_BUILDING"
    MULTI_STORY_HOUSE = "MULTI_STORY_HOUSE"

class HomeDocTypeEnum(str, enum.Enum):
    PROPERTY = "PROPERTY"
    FLOOR = "FLOOR"
    APARTMENT = "APARTMENT"
    ROOM = "ROOM"
    ROOM_FURNITURE = "ROOM_FURNITURE"
    ROOM_STUFF = "ROOM_STUFF"
    ROOM_INSTRUMENT = "ROOM_INSTRUMENT"

class ListingStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class ListingTypeEnum(str, enum.Enum):
    standard = "Standard"
    new_construction = "New Construction"
    foreclosure = "Foreclosure"
    short_sale = "Short Sale"
