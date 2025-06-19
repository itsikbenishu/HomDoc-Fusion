from typing import List, Dict, Optional
from pydantic import Field, ConfigDict, field_validator
from entities.abstracts.camel_model import CamelModel
from entities.home_doc.models import HomeDocCategoriesEnum, HomeDocTypeEnum

class HomeDocCreate(CamelModel):
    interior_entity_key: str = Field(alias="interiorEntityKey")
    category: HomeDocCategoriesEnum
    type: HomeDocTypeEnum
    description: Optional[str] = Field(default=None)
    extra_data: Optional[List[Dict[str, str]]] = Field(default_factory=list, alias="extraData")

    @field_validator('interior_entity_key')
    @classmethod
    def validate_interior_entity_key(cls, v):
        if not v or not v.strip():
            raise ValueError('interior_entity_key cannot be empty')
        return v.strip()

class HomeDocUpdate(CamelModel):
    description: Optional[str] = Field(default=None)
    extra_data: Optional[List[Dict[str, str]]] = Field(default=None, alias="extraData")

class HomeDocChildCreate(CamelModel):
    interior_entity_key: str
    type: str

    @field_validator('interior_entity_key')
    @classmethod
    def validate_interior_entity_key(cls, v):
        if not v or not v.strip():
            raise ValueError('interior_entity_key cannot be empty')
        return v.strip()

