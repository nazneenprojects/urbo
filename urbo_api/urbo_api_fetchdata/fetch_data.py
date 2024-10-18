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
from urbo_api.urbo_api_dataload.schema import NearbyPlacesCreate, GeocodeCreate, PollutantSchema
from urbo_api.urbo_api_fetchdata.urbo_recommendations import AQILevel, PollutantInfo

# Global variables
aqi_dict = {
    1: "Good",
    2: "Fair",
    3: "Moderate",
    4: "Poor",
    5: "Very Poor"
}

router = APIRouter(
    tags=["get-urban-planning-data"],
    responses={404: {"description": "Not Found"}}
)


@router.post("/aggregate-endpoint", response_model=schema.AggregateResponse)
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
    aqi_recommendation = None
    nearby_places_recommendation = None

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

    # Recommendation Logic based on quantitative data received from different 3rd party api services
    # For Air Quality Index
    if air_pollution_output['main']['aqi']:

        match air_pollution_output['main']['aqi']:
            case 1:
                aqi_recommendation = AQILevel.GOOD
            case 2:
                aqi_recommendation = AQILevel.FAIR
            case 3:
                aqi_recommendation = AQILevel.MODERATE
            case 4:
                aqi_recommendation = AQILevel.POOR
            case 5:
                aqi_recommendation = AQILevel.VERY_POOR
            case _:
                aqi_recommendation = "Invalid AQI value received"

    # For Air Pollution data
    pollutants = []
    for pollutant in PollutantInfo:
        pollutant_data = PollutantSchema(
            pollutant_name=pollutant.value["name"],
            description=pollutant.value["description"],
            source=pollutant.value["source"],
            health_effects=pollutant.value["health_effects"]
        )

        pollutants.append(pollutant_data)

    pollutants_info = pollutants

    # For Nearby found places
    nearby_places_count = len(nearby_places_result.nearby_places_response["suggestedLocations"])

    if nearby_places_count < 5 and user_input.radius >= 1000:
        nearby_places_recommendation = f"You have very less {user_input.keywords} in the radius of {user_input.radius} meters "
    elif nearby_places_count > 5 and user_input.radius <= 1000:
        nearby_places_recommendation = f"You have good enough {user_input.keywords} in the radius of {user_input.radius} meters "

    response_data = {
        "address": geocode_result.address,
        "latitude": geocode_result.latitude,
        "longitude": geocode_result.longitude,
        "Nearby_places": nearby_places_result.nearby_places_response,
        "nearby_places_recommendation": nearby_places_recommendation,
        "air_quality_index": air_pollution_output['main']['aqi'],
        "aqi_recommendation": aqi_recommendation,
        "air_pollution_params": air_pollution_output['components'],
        "pollutants_info": pollutants_info,
        "still_map_image": f"data:image/png;base64,{map_img_base64}"
    }

    return response_data
