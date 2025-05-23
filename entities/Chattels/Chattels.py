from dataclasses import dataclass
from entities.HomeDoc import HomeDoc

@dataclass
class Chattels(HomeDoc):
    __slots__ = ['colors', 'quantity', 'weight']
    colors: str
    quantity: str
    weight: str