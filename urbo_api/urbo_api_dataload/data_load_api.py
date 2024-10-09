import pprint

from fastapi import APIRouter, Depends, HTTPException
from dotenv import load_dotenv
from geoalchemy2 import WKTElement
from sqlalchemy.orm import Session
from urllib3 import request

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
nearby_places_url = os.getenv('NREABY_PLACES_URL')
models.Base.metadata.create_all(bind=engine)

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'iamdarkseid'
}

router = APIRouter(
    tags=["data-load"],
    responses={404: {"description": "Not Found"}}
)


@router.post("/fetch-nearby-places/", response_model=schema.NearbyPlaceResponse)
def fetch_nearby_places( place_data: schema.NearbyPlacesCreate, db_session: Session = Depends(get_db)
):
    token = utils.get_mapple_token()
    print(token)

    headers = {
        'Authorization': f'Bearer {token}'
    }

    ref_location_str = f"{place_data.ref_location[0]},{place_data.ref_location[1]}"
    params = {
        'keywords': place_data.keywords,
        'refLocation': ref_location_str,
        'radius': place_data.radius,
        'region': place_data.region
    }

    response = requests.get(nearby_places_url, headers=headers, params=params)


    pprint.pprint(response)

    if response.status_code == 200:
        data = response.json()
        pprint.pprint(data)


        ref_location_point = WKTElement(f'POINT({place_data.ref_location[1]} {place_data.ref_location[0]})',
                                        srid=4326)

        print(ref_location_point)

        mapple_place = models.NearbyPlace(
            keywords=place_data.keywords,
            ref_location=ref_location_point,
            nearby_places_response=data
        )
        db_session.add(mapple_place)
        db_session.commit()
        db_session.refresh(mapple_place)


        ref_location_list = [place_data.ref_location[0], place_data.ref_location[1]]

        return {
            "id": mapple_place.id,
            "keywords": mapple_place.keywords,
            "ref_location": ref_location_list,
            "nearby_places_response": mapple_place.nearby_places_response
        }

    else:
        raise HTTPException(status_code=400, detail="Failed to fetch places from Mapple API")
