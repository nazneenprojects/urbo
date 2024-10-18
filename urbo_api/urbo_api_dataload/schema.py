"""
 schema.py file contains all the pydantic schema designed to integrate validation of api and DB tables
"""
from typing import List, Any, Optional
from pydantic import BaseModel, Field
import uuid


class UrbanPlanningByPlaceCreate(BaseModel):
    address: str = Field(..., example="New Delhi")
    keywords: List[str] = Field(..., example=["parks"])
    region: Optional[str] = Field("IND", example=["IND"])
    radius: Optional[int] = 1000
    zoom: int = Field(12, example=14)
    size: str = Field("1000x1000", example="1000x1000")


class GeocodeResponseLonLat(BaseModel):
    address: str = Field(..., example="New Delhi")
    latitude: float = Field(..., example=77.2090)
    longitude: float = Field(..., example=28.6139)
    # map_img: bytes


class AggregateResponse(BaseModel):
    address: str = Field(..., example="New Delhi")
    latitude: float = Field(..., example=77.2090)
    longitude: float = Field(..., example=28.6139)
    Nearby_places: Any
    air_quality_index: int
    air_pollution_params: Any
    still_map_image: str


class NearbyPlacesCreate(BaseModel):
    keywords: List[str] = Field(..., example=["parks"])
    ref_location: List[float] = Field(..., example=[28.6139, 77.2090])
    region: Optional[str] = "IND"
    radius: Optional[int] = 1000


class NearbyPlaceResponse(BaseModel):
    id: uuid.UUID
    keywords: List[str] = Field(..., example=["parks"])
    ref_location: List[float] = Field(..., example=[28.6139, 77.2090])
    nearby_places_response: Any

    class Config:
        orm_mode = True


class GeocodeCreate(BaseModel):
    address: str = Field(..., example="New Delhi")


class ReverseGeocodeCreate(BaseModel):
    latitude: float = Field(..., example=28.6139)
    longitude: float = Field(..., example=77.2090)


class GeocodeResponse(BaseModel):
    address: str = Field(..., example="New Delhi")
    latitude: float = Field(..., example=77.2090)
    longitude: float = Field(..., example=28.6139)
    ref_location: str
    geocode_response: dict

    class Config:
        orm_mode = True


class StillMapImageCreate(BaseModel):
    center: List[float] = Field(..., example=[28.6139, 77.2090])
    zoom: int = Field(..., example=14)
    size: str = Field(..., example="1000x1000")


class StillMapImageResponse(BaseModel):
    id: uuid.UUID
    center: List[float] = Field(..., example=[28.6139, 77.2090])
    map_img: bytes

    class Config:
        arbitrary_types_allowed = True


class Coordinates(BaseModel):
    lon: float = Field(..., example=77.2090)
    lat: float = Field(..., example=28.6139)


class AirPollutionComponents(BaseModel):
    co: float = Field(..., example=226.97)
    no: float = Field(..., example=0)
    no2: float = Field(..., example=0.03)
    o3: float = Field(..., example=62.94)
    so2: float = Field(..., example=0.09)
    pm2_5: float = Field(..., example=0.7)
    pm10: float = Field(..., example=1.43)
    nh3: float = Field(..., example=0)


class AirPollutionMain(BaseModel):
    aqi: int = Field(..., example=2)


class AirPollutionList(BaseModel):
    main: AirPollutionMain
    components: AirPollutionComponents
    dt: int = Field(..., example=1728839262)


class AirPollutionResponse(BaseModel):
    center_coordinates: Coordinates
    air_pollution_response: List[AirPollutionList]

    class Config:
        orm_mode = True
