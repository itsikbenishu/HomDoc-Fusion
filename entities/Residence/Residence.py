from dataclasses import dataclass
from entities.HomeDoc import HomeDoc

@dataclass(slots=True)
class Residence(HomeDoc):
    area: str
    sub_entities_quantity: str
    construction_year: str
