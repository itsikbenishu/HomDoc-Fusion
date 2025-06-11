from typing import List, Dict, Optional
from pydantic import Field, ConfigDict, field_validator
from sqlmodel import SQLModel
from entities.home_doc.models import HomeDocCategoriesEnum, HomeDocTypeEnum

class HomeDocCreate(SQLModel):
    interior_entity_key: str = Field(alias="interiorEntityKey")
    category: HomeDocCategoriesEnum
    type: HomeDocTypeEnum
    description: Optional[str] = Field(default=None)
    extra_data: Optional[List[Dict[str, str]]] = Field(default_factory=list, alias="extraData")

    model_config = ConfigDict(
        str_strip_whitespace=True, 
        use_enum_values=True,
        populate_by_name=True  
    )

    @field_validator('interior_entity_key')
    @classmethod
    def validate_interior_entity_key(cls, v):
        if not v or not v.strip():
            raise ValueError('interior_entity_key cannot be empty')
        return v.strip()
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        if not v:
            raise ValueError('type cannot be empty')
        return v
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        if not v:
            raise ValueError('category cannot be empty')
        return v

class HomeDocUpdate(SQLModel):
    interior_entity_key: Optional[str] = Field(default=None, alias="interiorEntityKey")
    category: Optional[HomeDocCategoriesEnum] = None
    type: Optional[HomeDocTypeEnum] = None
    description: Optional[str] = Field(default=None)
    extra_data: Optional[List[Dict[str, str]]] = Field(default=None, alias="extraData")

    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        populate_by_name=True
    )
