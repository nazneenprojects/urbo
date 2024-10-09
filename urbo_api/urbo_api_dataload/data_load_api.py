from fastapi import APIRouter, Depends, HTTPException
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from urbo_api.db_connect.db import engine
from urbo_api.db_connect.dependenceis import get_db
from urbo_api.urbo_api_dataload import utils
from urbo_api.urbo_api_dataload import models
import requests

import os
bearer_token = None
load_dotenv()


client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
token_url = os.getenv('TOKEN_URL')
nearby_places_url = os.getenv('NEARBY_PLACES_URL')
models.Base.metadata.create_all(bind=engine)

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'iamdarkseid'
}

router = APIRouter(
    tags=["data-load"],
    responses={404: {"description": "Not Found"}},
    dependencies=[Depends(get_db)],
)

@router.post("/fetch-nearby-places")
def fetch_nearby_places( keywords: str, ref_location: str, radius: int, region: str, db: Session = Depends(get_db)
):
    token = utils.get_mapple_token()
    headers = {
        'Authorization': f'Bearer {token}'
    }

    params = {
        'keywords': keywords,
        'refLocation': ref_location,
        'radius': radius,
        'region': region,
        'page': 1
    }

    response = requests.get(nearby_places_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        places = []
        for place in data['suggestedLocations']:
            place_obj = models.NearbyPlace(
                name=place['placeName'],
                category=place.get('category', 'N/A'),
                latitude=place['latitude'],
                longitude=place['longitude'],
                region=region
            )
            db.add(place_obj)
            places.append(place_obj)

        db.commit()
        db.refresh(place_obj)
        return places

    else:
        raise HTTPException(status_code=400, detail="Failed to fetch places from Mapple API")
