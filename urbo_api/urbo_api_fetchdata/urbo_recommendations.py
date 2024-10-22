"""
 This file contains custom recommendations.
"""

from enum import Enum

class AQILevel(Enum):
    GOOD = {
        "aqi": 1,
        "description": "Air quality is good.",
        "action": "No action needed. Enjoy outdoor activities!"
    }
    FAIR = {
        "aqi": 2,
        "description": "Air quality is fair.",
        "action": "Sensitive individuals should consider limiting prolonged outdoor exertion."
    }
    MODERATE = {
        "aqi": 3,
        "description": "Air quality is moderate.",
        "action": "Everyone should consider limiting prolonged outdoor exertion, especially sensitive groups."
    }
    POOR = {
        "aqi": 4,
        "description": "Air quality is poor.",
        "action": "Limit outdoor activities. Avoid outdoor exertion for sensitive individuals."
    }
    VERY_POOR = {
        "aqi": 5,
        "description": "Air quality is very poor.",
        "action": "Avoid all outdoor exertion. Use masks if necessary."
    }


class PollutantInfo(Enum):
    PM10 = {
        "name": "Particulate Matter (PM10)",
        "description": "Coarse particulates that can penetrate into the lungs and cause health problems.",
        "source": "Vehicle emissions, industrial activities, and dust.",
        "health_effects": "Can cause respiratory issues, especially in sensitive individuals."
    }
    PM2_5 = {
        "name": "Particulate Matter (PM2.5)",
        "description": "Fine particulates that can penetrate deep into the lungs and even enter the bloodstream.",
        "source": "Vehicle emissions, industrial processes, and dust.",
        "health_effects": "Prolonged exposure can lead to serious respiratory and cardiovascular issues."
    }
    NO2 = {
        "name": "Nitrogen Dioxide (NO2)",
        "description": "Forms from burning fossil fuels, especially in vehicles and power plants.",
        "source": "Primarily emitted from vehicle engines and power plants.",
        "health_effects": "Long-term exposure can lead to respiratory diseases such as asthma."
    }
    O3 = {
        "name": "Ozone (O3)",
        "description": "Ground-level ozone forms when pollutants react with sunlight.",
        "source": "Forms from reactions between NOx and VOCs in the presence of sunlight.",
        "health_effects": "Aggravates lung diseases and reduces lung function."
    }
    SO2 = {
        "name": "Sulfur Dioxide (SO2)",
        "description": "A gas produced by the burning of fossil fuels, especially in power plants and industrial facilities.",
        "source": "Burning of fossil fuels, such as coal and oil, and industrial processes.",
        "health_effects": "Can cause respiratory problems and contribute to the formation of acid rain."
    }
    CO = {
        "name": "Carbon Monoxide (CO)",
        "description": "Produced by incomplete combustion of carbon-containing fuels.",
        "source": "Vehicles, industrial processes, and residential heating systems.",
        "health_effects": "Reduces the body’s ability to deliver oxygen to vital organs and tissues."
    }
    NH3 = {
        "name": "Ammonia (NH3)",
        "description": "A colorless gas with a pungent odor, often associated with agricultural activities.",
        "source": "Agriculture, especially livestock waste and fertilizer use.",
        "health_effects": "Can irritate the eyes, nose, and throat; contributes to the formation of fine particulate matter."
    }
    NO = {
        "name": "Nitrogen Monoxide (NO)",
        "description": "A precursor to nitrogen dioxide and ozone formation, associated with combustion processes.",
        "source": "Combustion of fossil fuels, especially in vehicles and power plants.",
        "health_effects": "Can lead to the formation of more harmful pollutants like NO2 and ozone."
    }