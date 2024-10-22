"""
models.py file maintains the table structure with table name
"""
from sqlalchemy import Column, JSON, String, Float, LargeBinary
from urbo_api.db_connect.db import Base
from geoalchemy2 import Geography, Geometry
import uuid
from sqlalchemy.dialects.postgresql import UUID


class NearbyPlace(Base):
    __tablename__ = "nearby_places"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    keywords = Column(String, index=True)
    ref_location = Column(Geography(geometry_type='POINT', srid=4326))
    nearby_places_response = Column(JSON)


class Geocode(Base):
    __tablename__ = "geocode"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    address = Column(String, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    ref_location = Column(Geometry(geometry_type='POINT', srid=4326))
    geocode_response = Column(JSON)


class StillMap(Base):
    __tablename__ = "stillmap"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    center = Column(Geometry(geometry_type='POINT', srid=4326))
    map_img = Column(LargeBinary, nullable=False)


class AirPollution(Base):
    __tablename__ = "airpollution"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    center_coordinates = Column(Geometry(geometry_type='POINT', srid=4326))
    air_pollution_response = Column(JSON)

