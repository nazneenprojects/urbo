"""
geocode_api.py help get lon and lat and vice versa from 3rdy party server (HERE server)
"""

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
import requests
import os
from sqlalchemy.orm import Session
from urbo_api.db_connect.db import get_db
from urbo_api.urbo_api_dataload import models, schema

#load environment variable from .env
load_dotenv()
here_api_key = os.getenv("HERE_API_KEY")
geocode_url = os.getenv("GEOCODE_HERE_API_URL")
reverse_geocode_url = os.getenv("GEOCODE_HERE_REVERSE_API_URL")

router = APIRouter(
    tags=["geocode"],
    responses={404: {"description": "Not Found"}}
)


@router.post("/geocode", response_model=schema.GeocodeResponse)
def get_geocode(geocode_data: schema.GeocodeCreate, db: Session = Depends(get_db)):
    """
    Get the Latitude and Longitude based on address
    :param geocode_data: takes address in string format as user input
    :param db: db_session: DB connection session
    :return:based on given address finds the coordinates  (long and lat)
    """
    if not here_api_key:
        raise HTTPException(status_code=500, detail="HERE API key not found")

    # Call HERE API for geocode
    params = {
        'q': geocode_data.address,
        'apiKey': here_api_key
    }
    response = requests.get(geocode_url, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching geocode")

    data = response.json()

    # Extract lat/long from HERE API response
    if 'items' not in data or len(data['items']) == 0:
        raise HTTPException(status_code=404, detail="Address not found")

    latitude = data['items'][0]['position']['lat']
    longitude = data['items'][0]['position']['lng']
    ref_location_point = f'POINT({longitude} {latitude})'

    # Store in DB
    new_geocode = models.Geocode(
        address=geocode_data.address,
        latitude=latitude,
        longitude=longitude,
        ref_location=ref_location_point,
        geocode_response=data
    )

    db.add(new_geocode)
    db.commit()
    db.refresh(new_geocode)

    return {
        "address": geocode_data.address,
        "latitude": latitude,
        "longitude": longitude,
        "ref_location": ref_location_point,
        "geocode_response": data
    }



@router.post("/reverse-geocode", response_model=schema.GeocodeResponse)
def get_reverse_geocode(reverse_geocode_data: schema.ReverseGeocodeCreate, db: Session = Depends(get_db)):
    """

    :param reverse_geocode_data: it takes coordinates (lon, lat)
    :param db: db_session: DB connection session
    :return: returns the address
    """
    if not here_api_key:
        raise HTTPException(status_code=500, detail="HERE API key not found")


    params = {
        'at': f"{reverse_geocode_data.latitude},{reverse_geocode_data.longitude}",
        'limit': 1,  # limit results to 1
        'apiKey': here_api_key
    }
    response = requests.get(reverse_geocode_url, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching reverse geocode")

    data = response.json()

    # Extract address from HERE API response
    if 'items' not in data or len(data['items']) == 0:
        raise HTTPException(status_code=404, detail="Location not found")

    address = data['items'][0]['address']['label']
    ref_location_point = f'POINT({reverse_geocode_data.longitude} {reverse_geocode_data.latitude})'

    # Store in DB
    new_geocode = models.Geocode(
        address=address,
        latitude=reverse_geocode_data.latitude,
        longitude=reverse_geocode_data.longitude,
        ref_location=ref_location_point,
        geocode_response=data
    )

    db.add(new_geocode)
    db.commit()
    db.refresh(new_geocode)

    return {
        "address": address,
        "latitude": reverse_geocode_data.latitude,
        "longitude": reverse_geocode_data.longitude,
        "ref_location": ref_location_point,
        "geocode_response": data
    }
