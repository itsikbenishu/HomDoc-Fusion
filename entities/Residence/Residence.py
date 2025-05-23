from dataclasses import dataclass
from entities.HomeDoc import HomeDoc

@dataclass
def Residence(HomeDoc):
    __slots__ = ['area', 'subEntitiesQuantity', 'constructionYear']
    area: str
    subEntitiesQuantity: str
    constructionYear: str
