from __future__ import print_function

import os
from datetime import datetime

import requests
import swagger_client
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from swagger_client.rest import ApiException

app = FastAPI(title="Weather App")


# class WeatherRequest(BaseModel):
#     country: str = (Query(..., description="Country"),)
#     city: str = Query(..., description="City")
#     when: datetime = (Query(datetime.now(), description="Datetime"),)


class WeatherResponse(BaseModel):
    temp_celsius: str
    is_precipitation: bool



@app.get("/get_now", response_model=WeatherResponse)
def get_now(
    country: str = Query(..., description="Country"),
    city: str = Query(..., description="City"),
    when: datetime = Query(datetime.now(), description="Datetime"),
):
    try:
        weather_data = get_weather_from_tomorrow_io(
            api_key="U4PjQiiqhnmTXjUJ2DJBcnGpHweby2nu",
            country=country,
            city=city,
            when=when,
        )
        weather_data1 = get_weather_from_weather_api(
            api_key="3dbe11fc94a34345887200931230612",
            country=country,
            city=city,
            when=when,
        )
        # print("Tomorrow.io Data:", weather_data)
        # print("WeatherAPI Data:", weather_data1)

        response_data = {"tomorrow_io": weather_data, "weather_api": weather_data1}

        return JSONResponse(content=response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")



@app.get("/get_forecast", response_model=WeatherResponse)
def get_forecast(
    country: str = Query(..., description="Country"),
    city: str = Query(..., description="City"),
    when: datetime = Query(datetime.now(), description="Datetime"),
):
    try:
        forecast_data = get_weather_forecast_from_tomorrow_io(
            api_key="U4PjQiiqhnmTXjUJ2DJBcnGpHweby2nu",
            country=country,
            city=city,
            when=when,
        )

        forecast_data1 = get_weather_forecast_from_weather_api(
            api_key="3dbe11fc94a34345887200931230612",
            country=country,
            city=city,
            when=when,
        )

        print("Tomorrow.io Data:", forecast_data)
        print("WeatherAPI Data:", forecast_data1)

        response_data = {"tomorrow_io": forecast_data, "weather_api": forecast_data1}

        return JSONResponse(content=response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


def get_weather_from_tomorrow_io(api_key: str, country: str, city: str, when: datetime):
    url = f"https://api.tomorrow.io/v4/weather/realtime"

    params = {
        "location": f"{city}/{country}",
        "apikey": api_key,
    }

    headers = {"accept": "application/json"}

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    data = response.json()

    values = data.get("data", {}).get("values", {})
    temperature = values.get("temperature", None)

    precipitation_probability = values.get("precipitationProbability", 0)
    print("precipitation_probability ", precipitation_probability)
    precipitation = precipitation_probability > 0

    if temperature is not None:
        return {"temp_celsius": str(temperature), "is_precipitation": precipitation}
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to get weather data from Tomorrow.io",
        )


def get_weather_forecast_from_tomorrow_io(
    api_key: str, country: str, city: str, when: datetime
):
    url = f"https://api.tomorrow.io/v4/weather/forecast"
    when_s = str(when)[:10]
    params = {
        "location": f"{city}/{country}",
        "apikey": api_key,
    }

    headers = {"accept": "application/json"}

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    data = response.json()
    temperature_avg = None
    precipitation_avg = None
    for daily_data in data.get("timelines", {}).get("daily", []):

        if daily_data.get("time", "")[:10] == when_s:
            temperature_avg = daily_data.get("values", {}).get("temperatureAvg", None)
            precipitation_avg = daily_data.get("values", {}).get(
                "precipitationProbabilityAvg", 0
            )
            precipitation_avg = precipitation_avg > 0
            break

    if temperature_avg is not None:
        return {
            "temp_celsius": str(temperature_avg),
            "is_precipitation": precipitation_avg,
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to get weather data from Tomorrow.io",
        )


def get_weather_from_weather_api(api_key: str, country: str, city: str, when: datetime):
    configuration = swagger_client.Configuration()
    configuration.api_key["key"] = "3dbe11fc94a34345887200931230612"

    api_instance = swagger_client.APIsApi(swagger_client.ApiClient(configuration))
    q = f"{city}/{country}"

    try:
        api_response = api_instance.realtime_weather(q)
    except ApiException as e:
        print("Exception when calling APIsApi->realtime_weather: %s\n" % e)
        raise HTTPException(
            status_code=500, detail="Failed to get weather data from WeatherAPI"
        )

    values = api_response.get("current", {})  # .get("values", {})
    temperature = values.get("temp_c", None)

    precipitation_probability = values.get("precip_mm", 0)
    print("precipitation_probability ", precipitation_probability)
    precipitation = precipitation_probability > 0

    if temperature is not None:
        return {"temp_celsius": str(temperature), "is_precipitation": precipitation}
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to get weather data from WeatherAPI",
        )


def get_weather_forecast_from_weather_api(
    api_key: str, country: str, city: str, when: datetime
):
    configuration = swagger_client.Configuration()
    configuration.api_key["key"] = api_key

    api_instance = swagger_client.APIsApi(swagger_client.ApiClient(configuration))
    q = f"{city}/{country}"

    days = 5

    dt = str(when)[:10]

    try:
        api_response = api_instance.forecast_weather(q, days, dt=dt)
    except ApiException as e:
        print("Exception when calling APIsApi->forecast_weather: %s\n" % e)
        raise HTTPException(
            status_code=500, detail="Failed to get weather data from WeatherAPI"
        )
    temperature_avg = None
    precipitation_avg = None
    for daily_data in api_response.get("forecast", {}).get("forecastday", []):
        if daily_data.get("date", "")[:10] == dt:
            temperature_avg = daily_data.get("day", {}).get("avgtemp_c", None)
            precipitation_avg = daily_data.get("day", {}).get("totalprecip_mm", 0)
            precipitation_avg = precipitation_avg > 0
            break

    if temperature_avg is not None:
        return {
            "temp_celsius": str(temperature_avg),
            "is_precipitation": precipitation_avg,
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to get weather data from WeatherAPI",
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
