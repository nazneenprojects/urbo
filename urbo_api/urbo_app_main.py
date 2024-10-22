"""
starter file to start the fastapi app
how to run?
    uvicorn urbo_app_main:app --reload
    uvicorn urbo_api.urbo_app_main:app --reload

"""

from fastapi import FastAPI
from fastapi.middleware.cors import  CORSMiddleware
from urbo_api.urbo_api_dataload.data_nearbyplaces_api import router as data_load
from urbo_api.urbo_api_dataload.geocode_api import router as geocode
from urbo_api.urbo_api_dataload.map_image_api import router as map
from urbo_api.urbo_api_dataload.air_pollution_api import router as air_pollution
from urbo_api.urbo_api_fetchdata.fetch_data import router as fetch_urban_planning_data
import sys
import os
from pyfiglet import  Figlet


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
figlet = Figlet(font='slant')
text_art = figlet.renderText('URBO')

app = FastAPI(
    title="URBO - Sustainability Tool for Urban Planning",
    version="v0.1.0a"
)

origins = [
    "http://localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("\t \t \t", text_art)

#Add other api endpoints into a common place
app.include_router(data_load)
app.include_router(geocode)
app.include_router(map)
app.include_router(air_pollution)
app.include_router(fetch_urban_planning_data)

# root welcome api
@app.get("/")
def root():
    return "Welcome to URBO"