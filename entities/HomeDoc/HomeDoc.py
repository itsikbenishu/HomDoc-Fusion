from dataclasses import dataclass
from typing import List,Dict

@dataclass
class HomeDoc: 
    id: int
    fatherId: int   
    interiorEntityKey: str
    fatherInteriorEntityKey: str
    createdAt: str
    updatedAt: str
    category: str
    type: str
    description: str
    extraData: List[Dict]
    length: str
    width: str

