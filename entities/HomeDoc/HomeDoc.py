from dataclasses import dataclass
from typing import List,Dict

@dataclass
class HomeDoc: 
    __slots__ = ['id', 'fatherId', 'interiorEntityKey','fatherInteriorEntityKey', 
                 'createdAt', 'updatedAt', 'category', 'type','description', 
                 'extraData' , 'length', 'length', 'width']
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

