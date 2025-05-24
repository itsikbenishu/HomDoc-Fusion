from dataclasses import dataclass
from typing import List,Dict

@dataclass(slots=True)
class HomeDoc: 
    id: int
    father_id: int   
    interior_entity_key: str
    father_interior_entity_key: str
    created_at: str
    updated_at: str
    category: str
    type: str
    description: str
    extra_data: List[Dict]
    length: str
    width: str

