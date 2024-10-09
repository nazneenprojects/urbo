# app/models.py
from sqlalchemy import Column, Integer, String, Float
from urbo_api.database.db_connect import Base


class NearbyPlace(Base):
    __tablename__ = "nearby_places"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    region = Column(String)
