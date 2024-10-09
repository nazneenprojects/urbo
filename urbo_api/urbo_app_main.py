"""
starter file to start the fastapi app
how to run?
    uvicorn urbo_app_main:app --reload

"""

from fastapi import FastAPI
from fastapi.middleware.cors import  CORSMiddleware
from urbo_api.urbo_api_dataload.data_load_api import router as dataload
import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

app.include_router(dataload)

@app.get("/")
async def root():
    return "Welcome to URBO"