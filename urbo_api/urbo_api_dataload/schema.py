
from pydantic import BaseModel

class NearbyPlaceCreate(BaseModel):
    name: str
    category: str
    latitude: float
    longitude: float
    region: str

class PlaceResponse(NearbyPlaceCreate):
    id: int

    class Config:
        orm_mode = True
