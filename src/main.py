from __future__ import print_function

import json
import os
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from app.schemas import WeatherResponse
from app.service import (get_weather_forecast_from_tomorrow_io,
                         get_weather_forecast_from_weather_api,
                         get_weather_from_tomorrow_io,
                         get_weather_from_weather_api)

app = FastAPI(title="Weather App")


# app.openapi = app.openapi_schema
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


openapi_schema = get_openapi(
    title="Your API",
    version="1.0.0",
    routes=app.routes,
)

with open("docs/openapi.json", "w") as f:
    f.write(str(openapi_schema))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
