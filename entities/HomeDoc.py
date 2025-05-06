from dataclasses import dataclass
from typing import List,Dict

@dataclass
class HomeDoc: 
    id: int
    fatherId: int   
    fatherInteriorEntityKey: str
    interiorEntityKey: str
    createdAt: str
    updatedAt: str
    category: str
    type: str
    description: str
    extraData: List[Dict]

