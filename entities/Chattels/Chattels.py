from dataclasses import dataclass
from entities.HomeDoc import HomeDoc

@dataclass
def Chattels(HomeDoc):
    colors: str
    quantity: str
    weight: str
