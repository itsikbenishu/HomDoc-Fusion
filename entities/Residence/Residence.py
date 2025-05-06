from dataclasses import dataclass
from entities.HomeDoc import HomeDoc

@dataclass
def Residence(HomeDoc):
    area: str
    subEntitiesQuantity: str
    constructionYear: str
