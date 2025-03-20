from pprint import pprint

import requests
from nicegui import app, ui
from fastapi import FastAPI
import pprint


def init(fastapi_app: FastAPI) -> None:
    @ui.page('/ui')
    def show():
        ui.page_title('URBO')

        ui.html('<h1><strong>URBO - Sustainability Tool for Urban Planning</strong></h1>')
        ui.html('<center>Select the Regional data to get insight on urban area planning </center>')

        ui.html('<strong> Select Country </strong> </>')
        region_dropdown = ui.select(['IN'])

        ui.html('<strong> Select City </strong> </>')
        city_dropdown = ui.select(['Pune', 'Mumbai', 'Chennai', 'Bangalore', 'New Delhi'])

        ui.html('<strong> Select radius area in meters </strong> </>')
        radius_dropdown = ui.select([1000])

        ui.html('<strong> Select keyword by which you want to filter the data </strong> </>')
        keyword_dropdown = ui.select(['Park', 'Clinic', 'School', 'Playground'], clearable=True)

        #ui.run()

        # Function to handle button click and send data to FastAPI endpoint
        def on_button_click():
            city = city_dropdown.value
            region = region_dropdown.value
            keyword = keyword_dropdown.value
            radius = radius_dropdown.value
            zoom = 12
            size = '1000x1000'

            if city and region and keyword and radius:
                # Send data to FastAPI endpoint
                payload = {
                    "address": city,
                    "keywords": [keyword],
                    "region": region,
                    "radius": radius,
                    "zoom": zoom,
                    "size": size
                }

                try:
                    # Send POST request to FastAPI
                    response = requests.post('http://127.0.0.1:8000/aggregate-endpoint', json=payload)

                    # Handle the response
                    if response.status_code == 200:
                        data = response.json()
                        pprint(data)
                        ui.notify(f"Success: {data.get('message', 'Data received!')}")
                    else:
                        ui.notify(f"Error: {response.status_code} - {response.text}")
                except requests.exceptions.RequestException as e:
                    ui.notify(f"Request failed: {str(e)}")
            else:
                ui.notify("Please select all fields before proceeding!")

        # Add button to submit the form
        ui.button("Show Urban Planning Data", on_click=on_button_click)

        # Mount NiceGUI with FastAPI app
        ui.run_with(fastapi_app, mount_path='/gui')

    ui.run_with(fastapi_app, mount_path='/gui')
