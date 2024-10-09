from typing import List, Any, Optional
from pydantic import BaseModel, Field
import uuid


class NearbyPlacesCreate(BaseModel):
    keywords: str
    ref_location: List[float] = Field(..., example=[28.6139, 77.2090])
    region: Optional[str] = "IND"
    radius: Optional[int] = 1000  # Default radius to 1000 meter


class NearbyPlaceResponse(BaseModel):
    id: uuid.UUID
    keywords: str
    ref_location: List[float]
    nearby_places_response: Any

    class Config:
        orm_mode = True
