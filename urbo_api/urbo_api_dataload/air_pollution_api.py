import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
import requests
from geoalchemy2 import WKTElement
from sqlalchemy.orm import Session
from urbo_api.db_connect.db import get_db
from urbo_api.urbo_api_dataload import models, schema

#load environment variable
load_dotenv()
api_key = os.getenv("API_KEY_OW")
base_url = os.getenv("AIR_POLLUTION_URL")

router = APIRouter(
    tags=["air-pollution"],
    responses={404: {"description": "Not Found"}}
)


@router.get("/fetch-air-pollution-data/", response_model=schema.AirPollutionResponse)
def get_air_pollution(latitude: float, longitude: float, db: Session = Depends(get_db)):
    """

    :param latitude: user input latitude
    :param longitude: user input longitude
    :param db:DB connection session
    :return: returns the coordinate(lon, lat) and the air pollution data of that specific coordinates
    """
    params = {
        'lon': longitude,
        'lat': latitude,
        'appid': api_key
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        lon = data['coord']['lon']
        lat = data['coord']['lat']
        center_coordinates = WKTElement(f'POINT({lon} {lat})', srid=4326)

        pollution_record = models.AirPollution(
            center_coordinates=center_coordinates,
            air_pollution_response=data['list']
        )

        db.add(pollution_record)
        db.commit()
        db.refresh(pollution_record)

        # response_model = schema.AirPollutionResponse(
        #     center_coordinates={"lon": lon, "lat": lat},
        #     air_pollution_response=data['list']
        # )
        #
        # return response_model
        center_coordinates = {"lon": lon, "lat": lat}
        air_pollution_response = data['list']

        return {
            "center_coordinates":center_coordinates,
            "air_pollution_response":air_pollution_response
        }

    else:
        raise HTTPException(status_code=response.status_code, detail="Error in fetching air polluting data")
