from dataclasses import dataclass
from entities.HomeDoc.HomeDoc import HomeDoc

@dataclass(slots=True)
class Chattels(HomeDoc):
    colors: str
    quantity: str
    weight: str

