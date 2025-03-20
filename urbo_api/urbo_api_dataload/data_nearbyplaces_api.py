"""
 data_nearbyplaces_api.py contains endpoint to find nearby places based on keyword and lon and lat
"""

from fastapi import APIRouter, Depends, HTTPException
from dotenv import load_dotenv
from geoalchemy2 import WKTElement
from sqlalchemy.orm import Session
from urbo_api.db_connect.db import engine
from urbo_api.db_connect.db import get_db
from urbo_api.urbo_api_dataload import utils
from urbo_api.urbo_api_dataload import models, schema
import requests
import os

bearer_token = None
load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
token_url = os.getenv('TOKEN_URL')
nearby_places_url = os.getenv('NEARBY_PLACES_URL')

# binds the metadata to a specific database engine to create table in DB
models.Base.metadata.create_all(bind=engine)

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'iamdarkseid'
}

router = APIRouter(
    tags=["nearby-places"],
    responses={404: {"description": "Not Found"}}
)


@router.post("/fetch-nearby-places/", response_model=schema.NearbyPlaceResponse)
def fetch_nearby_places(place_data: schema.NearbyPlacesCreate, db_session: Session = Depends(get_db)):
    """
    This helps to fetch nearby places based on
    :param place_data: inputs such as keyword, longitude, latitude, radius and region
    :param db_session: DB connection session
    :return: returns the nearby places based on given inputs
    """
    token = utils.get_mapple_token()
    if not token:
        raise HTTPException(status_code=500, detail="Token not found")

    headers = {
        'Authorization': f'Bearer {token}'
    }

    ref_location_str = f"{place_data.ref_location[0]},{place_data.ref_location[1]}"
    params = {
        'keywords': keywords_to_string(place_data.keywords),
        'refLocation': ref_location_str,
        'radius': place_data.radius,
        'region': place_data.region
    }

    response = requests.get(nearby_places_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()

        ref_location_point = WKTElement(f'POINT({place_data.ref_location[1]} {place_data.ref_location[0]})',
                                        srid=4326)

        nearby_place = models.NearbyPlace(
            keywords=keywords_to_string(place_data.keywords),
            ref_location=ref_location_point,
            nearby_places_response=data
        )
        db_session.add(nearby_place)
        db_session.commit()
        db_session.refresh(nearby_place)

        ref_location_list = [place_data.ref_location[0], place_data.ref_location[1]]

        return {
            "id": nearby_place.id,
            "keywords": string_to_keywords(nearby_place.keywords),
            "ref_location": ref_location_list,
            "nearby_places_response": nearby_place.nearby_places_response
        }

    else:
        raise HTTPException(status_code=400, detail="Failed to fetch places from Mapple API")



def keywords_to_string(keywords):
    """Convert a list of keywords to a comma-separated string."""
    if isinstance(keywords, list):
        return ','.join(keywords)
    return keywords

def string_to_keywords(keywords_str):
    """Convert a comma-separated string of keywords back into a list."""
    if isinstance(keywords_str, str):
        return keywords_str.split(',')
    return keywords_str