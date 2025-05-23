from dataclasses import dataclass
from entities.HomeDoc import HomeDoc

@dataclass
class Chattels(HomeDoc):
    colors: str
    quantity: str
    weight: str