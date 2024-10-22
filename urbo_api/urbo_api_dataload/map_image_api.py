"""
 map_image_api.py contains the api for fetching still map image based on long, lat and other given params
"""
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2 import WKTElement
from sqlalchemy.orm import Session
import requests
from urbo_api.db_connect.db import get_db
from urbo_api.urbo_api_dataload import models, schema

# load environment variable
load_dotenv()
api_key = os.getenv("API_KEY")
url = os.getenv("STILL_MAP_URL")


router = APIRouter(
    tags=["map"],
    responses={404: {"description": "Not Found"}}
)


@router.get("/stillmap", response_model=schema.StillMapImageResponse)
def get_stillmap(lat: float, lon: float, zoom: int = 12, size: str = "1000x1000", db: Session = Depends(get_db)):
    """

    :param lat: latitude in float
    :param lon: longitude in float
    :param zoom: zoom level set to 12
    :param size: constant size 1000x1000
    :param db: DB connection session
    :return: fetches the still map image in .png form based on given inputs
    """
    # Construct the URL to fetch the image
    still_map_url = f"{url}{api_key}/still_image"
    params = {
        "center": f"{lat},{lon}",
        "zoom": zoom,
        "size": size
    }

    response = requests.get(still_map_url, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching image from Mapples")

    center = [lon,lat]
    center_point = WKTElement(f'POINT({center[0]} {center[1]})', srid=4326)
    new_stillmap = models.StillMap(
        center= center_point,
        map_img=response.content
    )

    db.add(new_stillmap)
    db.commit()
    db.refresh(new_stillmap)

    return {
        "id": new_stillmap.id,
        "center": [lon,lat],
        "map_img": new_stillmap.map_img
    }