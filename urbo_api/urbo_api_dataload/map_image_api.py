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
import base64
from fastapi.responses import JSONResponse

# load environment variable
load_dotenv()
api_key = os.getenv("API_KEY")
url = os.getenv("STILL_MAP_URL")


router = APIRouter(tags=["map"], responses={404: {"description": "Not Found"}})


@router.post("/stillmap", response_model=schema.StillMapImageResponse)
def get_stillmap(
    lat: float,
    lon: float,
    zoom: int = 12,
    size: str = "1000x1000",
    ssf: int = 0,  # 0 for non-retina, 1 for retina
    markers: str = None,  # Optional marker coordinates (e.g., "28.5959394,77.2255611")
    markers_icon: str = None,  # Optional custom marker URL
    db: Session = Depends(get_db),
):
    """
    Fetch a static still map image from Mappls API using a POST request.

    :param lat: Latitude of the map center
    :param lon: Longitude of the map center
    :param zoom: Zoom level (default: 12)
    :param size: Image size (default: "1000x1000")
    :param ssf: Scale factor (0 = non-retina, 1 = retina)
    :param markers: Optional marker coordinates (lat,lon)
    :param markers_icon: Optional custom marker URL
    :param db: Database session for storing results
    :return: JSON with map image details
    """

    if not api_key:
        print("❌ Error: API Key is missing! Check your .env file.")
        raise HTTPException(status_code=500, detail="API Key is missing")

    # Construct the API URL
    still_map_url = f"https://apis.mappls.com/advancedmaps/v1/{api_key}/still_image"

    # Construct API parameters
    params = {
        "center": f"{lat},{lon}",
        "zoom": zoom,
        "size": size,
        "ssf": ssf,
    }

    # Add optional parameters if provided
    if markers:
        params["markers"] = markers
    if markers_icon:
        params["markers_icon"] = markers_icon

    headers = {"Content-Type": "application/json"}

    print(f"🔎 Fetching still map from: {still_map_url}")
    print(f"📌 Parameters: {params}")

    try:
        response = requests.post(still_map_url, params=params, headers=headers)

        if response.status_code != 200:
            print(
                f"❌ Error fetching image: {response.status_code}, Response: {response.text}"
            )
            raise HTTPException(
                status_code=response.status_code,
                detail="Error fetching image from Mappls",
            )

        if not response.content or len(response.content) < 100:
            print("❌ Invalid image received. API response might contain an error.")
            raise HTTPException(
                status_code=500, detail="Invalid image received from API"
            )

    except requests.exceptions.RequestException as e:
        print(f"❌ Network request failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to Mappls API")

    # ✅ Convert binary image to Base64 for JSON response
    map_img_base64 = base64.b64encode(response.content).decode()

    # Store image in database
    center_point = WKTElement(f"POINT({lon} {lat})", srid=4326)

    try:
        new_stillmap = models.StillMap(
            center=center_point, map_img=response.content  # Store binary image in DB
        )
        db.add(new_stillmap)
        db.commit()
        db.refresh(new_stillmap)
    except Exception as e:
        db.rollback()
        print(f"❌ Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error while saving image")

    print(f"✅ Successfully saved image for {lat}, {lon}")

    # ✅ Return JSON response with Base64 encoded image
    return JSONResponse(
        content={
            "id": str(new_stillmap.id),
            "center": [lon, lat],
            "map_img": f"data:image/png;base64,{map_img_base64}",
        }
    )
