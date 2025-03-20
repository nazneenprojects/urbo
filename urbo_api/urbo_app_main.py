"""
starter file to start the fastapi app
how to run?
    uvicorn urbo_app_main:app --reload
    uvicorn urbo_api.urbo_app_main:app --reload

"""

import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pyfiglet import Figlet
from starlette.middleware.trustedhost import TrustedHostMiddleware
import logging

from urbo_api.urbo_api_dataload.air_pollution_api import router as air_pollution
from urbo_api.urbo_api_dataload.data_nearbyplaces_api import router as data_load
from urbo_api.urbo_api_dataload.geocode_api import router as geocode
from urbo_api.urbo_api_dataload.map_image_api import router as map
from urbo_api.urbo_api_fetchdata.fetch_data import router as fetch_urban_planning_data
from urbo_ui.frontend_main import init

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
figlet = Figlet(font='slant')
text_art = figlet.renderText('URBO')



app = FastAPI(
    title="URBO - Sustainability Tool for Urban Planning",
    version="v0.1.0a"
)

# init ui
init(app)

origins = [
    "http://localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "*"])
logging.basicConfig(level=logging.DEBUG)

print("\t \t \t", text_art)

#Add other api endpoints into a common place
app.include_router(data_load)
app.include_router(geocode)
app.include_router(map)
app.include_router(air_pollution)
app.include_router(fetch_urban_planning_data)

logging.getLogger('socketio').setLevel(logging.DEBUG)

# root welcome api
@app.get("/")
def root():
    return "Welcome to URBO"


# if __name__ == '__main__':
#     import uvicorn
#     uvicorn.run("urbo_app_main:app", host="0.0.0.0", port=8000, reload=True)