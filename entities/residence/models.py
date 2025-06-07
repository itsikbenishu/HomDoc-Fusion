from typing import Optional, List, Dict
from sqlmodel import SQLModel, Field, Relationship
from entities.home_doc.models import HomeDocs, HomeDocsDimensions
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
    area: Optional[float] = None
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

    home_doc: Optional["HomeDocs"] = Relationship(back_populates="specs")

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True
    )

ResidenceSpecsAttributes.model_rebuild()

class ResidenceResponse(SQLModel):
    id: int
    interior_entity_key: str
    father_interior_entity_key: Optional[str] = None
    category: str
    type: str
    description: Optional[str] = None
    extra_data: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    
    area: Optional[float] = Field(default=None)
    sub_entities_quantity: Optional[int] = Field(default=None)
    construction_year: Optional[int] = Field(default=None)
    
    length: Optional[int] = Field(default=None)
    width: Optional[int] = Field(default=None)
    
    children: List[HomeDocs] = Field(default=list)

    home_doc: Optional["HomeDocs"] = Relationship(
        back_populates="specs"
    )


    @classmethod
    def from_models(cls, 
                   home_doc: HomeDocs, 
                   specs: ResidenceSpecsAttributes, 
                   dimensions: Optional[HomeDocsDimensions] = None) -> "ResidenceResponse":

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
