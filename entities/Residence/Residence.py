from dataclasses import dataclass
from entities.HomeDoc import HomeDoc

@dataclass(slots=True)
class Residence(HomeDoc):
    area: str
    subEntitiesQuantity: str
    constructionYear: str
