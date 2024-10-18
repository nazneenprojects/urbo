"""
 fetch_data.py contain the endpoint which acts on top of other apis
 if data not found in current dn then this api request the data to third party api service
"""
import base64

from fastapi import APIRouter, Depends
from geoalchemy2 import WKTElement
from sqlalchemy.orm import Session

from urbo_api.db_connect.db import get_db
from urbo_api.urbo_api_dataload import models, schema
from urbo_api.urbo_api_dataload.air_pollution_api import get_air_pollution
from urbo_api.urbo_api_dataload.data_nearbyplaces_api import fetch_nearby_places
from urbo_api.urbo_api_dataload.geocode_api import get_geocode
from urbo_api.urbo_api_dataload.map_image_api import get_stillmap
from urbo_api.urbo_api_dataload.schema import NearbyPlacesCreate, GeocodeCreate

router = APIRouter(
    tags=["get-urban-planning-data"],
    responses={404: {"description": "Not Found"}}
)


@router.post("/aggreegate-endpoint", response_model=schema.AggregateResponse)
def get_urban_planning_data(user_input: schema.UrbanPlanningByPlaceCreate, db: Session = Depends(get_db)):
    """
    this function acts on top of other api endpoints.
    this check if requested data is present in the database if not then it request from 3rd party api
    :param user_input: takes input from user - address, keywords, region, radius, zoom, size
    :param db: db_session: DB connection session
    :return: returns combined data from different endpoints and also display some recommendations
    """
    geocode_result = None
    map_img_base64 = None
    air_pollution_output = None
    nearby_places_result = None

    # Fetch Longitude and Latitude
    if user_input:
        geocode_result = db.query(models.Geocode).filter(models.Geocode.address == user_input.address).first()

        if geocode_result is None:
            geocode_create_date = GeocodeCreate(
                address=user_input.address
            )
            geocode_result = get_geocode(geocode_create_date, db)

    # Fetch Nearby Places based on Latitude and Longitude
    if geocode_result and user_input:
        ref_location = WKTElement(f'POINT({geocode_result.longitude} {geocode_result.latitude})', srid=4326)
        nearby_places_result = (db.query(models.NearbyPlace).
                                filter(models.NearbyPlace.keywords.in_(user_input.keywords),
                                       models.NearbyPlace.ref_location == ref_location
                                       ).first())

        if nearby_places_result is None:
            nearby_places_data = NearbyPlacesCreate(
                keywords=user_input.keywords,
                ref_location=[geocode_result.latitude, geocode_result.longitude],
                region=user_input.region,
                radius=user_input.radius
            )

            nearby_places_result = fetch_nearby_places(nearby_places_data, db)

    # Fetch Air pollution results based on Latitude and Longitude
    if geocode_result:

        center_coordinates = WKTElement(f'POINT({geocode_result.longitude} {geocode_result.latitude})', srid=4326)
        air_pollution_result = db.query(models.AirPollution).filter(
            models.AirPollution.center_coordinates == center_coordinates).first()

        if air_pollution_result is None:
            air_pollution_result = get_air_pollution(geocode_result.latitude, geocode_result.longitude, db)
            air_pollution_output = air_pollution_result['air_pollution_response'][0]

    # Fetch still Map image (Byte format) based on Latitude and Longitude and other constant params
    if geocode_result:
        center_input = WKTElement(f'POINT({geocode_result.longitude} {geocode_result.latitude})', srid=4326)
        get_still_map_results = db.query(models.StillMap).filter(models.StillMap.center == center_input).first()

        if get_still_map_results is None:
            get_still_map_results = get_stillmap(geocode_result.latitude, geocode_result.longitude, user_input.zoom,
                                                 user_input.size, db)

            map_img_bytes = get_still_map_results["map_img"]
            map_img_base64 = base64.b64encode(map_img_bytes).decode('utf-8')

    return {
        "address": geocode_result.address,
        "latitude": geocode_result.latitude,
        "longitude": geocode_result.longitude,
        "Nearby_places": nearby_places_result.nearby_places_response,
        "air_quality_index": air_pollution_output['main']['aqi'],
        "air_pollution_params": air_pollution_output['components'],
        "still_map_image": f"data:image/png;base64,{map_img_base64}"
    }
