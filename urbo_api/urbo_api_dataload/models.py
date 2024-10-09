# app/models.py
from sqlalchemy import Column, JSON, String, Float
from urbo_api.db_connect.db import Base
from geoalchemy2 import Geography
import uuid
from sqlalchemy.dialects.postgresql import UUID


class NearbyPlace(Base):
    __tablename__ = "nearby_places"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    keywords = Column(String, index=True)
    ref_location = Column(Geography(geometry_type='POINT', srid=4326))
    nearby_places_response = Column(JSON)

