"""
 utils.py helps to generate bearer token from 3rd party api service (Mapple service)
"""
import requests
import os
from dotenv import load_dotenv

# loads data from .env file
load_dotenv()
MAPPLE_TOKEN_URL = os.getenv('TOKEN_URL')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')


def get_mapple_token():
    """
    Based on provided client id, client secret it generates the bearer token
    :return: access_token
    """
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'iamdarkseid',
    }
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    response = requests.post(MAPPLE_TOKEN_URL, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception('Failed to fetch token')
