from __future__ import print_function
from datetime import datetime
import requests
import swagger_client
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from swagger_client.rest import ApiException

app = FastAPI(
    title="Weather App"
)


# Модели данных для запросов и ответов
class WeatherRequest(BaseModel):
    country: str
    city: str
    when: datetime


class WeatherResponse(BaseModel):
    temp_celsius: str
    is_precipitation: bool


# Роут для текущей погоды
@app.post("/get_now", response_model=WeatherResponse)
def get_now(weather_request: WeatherRequest):
    try:
        # Используйте функцию запроса к внешнему сервису Tomorrow.io
        weather_data = get_weather_from_tomorrow_io(api_key="U4PjQiiqhnmTXjUJ2DJBcnGpHweby2nu",
                                                    country=weather_request.country,
                                                    city=weather_request.city,
                                                    when=weather_request.when)
        # Обработайте данные, если необходимо
        # ...

        weather_data1 = get_weather_from_weather_api(api_key="3dbe11fc94a34345887200931230612",
                                                    country=weather_request.country,
                                                    city=weather_request.city,
                                                    when=weather_request.when)
        print("Tomorrow.io Data:", weather_data)
        print("WeatherAPI Data:", weather_data1)

        response_data = {"tomorrow_io": weather_data, "weather_api": weather_data1}

        return JSONResponse(content=response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Роут для прогноза погоды
@app.post("/get_forecast", response_model=WeatherResponse)
def get_forecast(weather_request: WeatherRequest):
    try:
        # Используйте функцию запроса к внешнему сервису Tomorrow.io
        forecast_data = get_weather_forecast_from_tomorrow_io(api_key="U4PjQiiqhnmTXjUJ2DJBcnGpHweby2nu",
                                                              country=weather_request.country,
                                                              city=weather_request.city,
                                                              when=weather_request.when)

        forecast_data1 = get_weather_forecast_from_weather_api(api_key="3dbe11fc94a34345887200931230612",
                                                              country=weather_request.country,
                                                              city=weather_request.city,
                                                              when=weather_request.when)

        print("Tomorrow.io Data:", forecast_data)
        print("WeatherAPI Data:", forecast_data1)

        response_data = {"tomorrow_io": forecast_data, "weather_api": forecast_data1}

        return JSONResponse(content=response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

def get_weather_from_tomorrow_io(api_key: str, country: str, city: str, when: datetime):
    url = f"https://api.tomorrow.io/v4/weather/realtime"

    # Примерно так должен выглядеть ваш запрос
    params = {
        "location": f"{city}/{country}",
        "apikey": api_key,
    }

    headers = {"accept": "application/json"}

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    data = response.json()

    # Парсинг данных из ответа
    values = data.get("data", {}).get("values", {})
    temperature = values.get("temperature", None)

    # Проверка, есть ли осадки
    precipitation_probability = values.get("precipitationProbability", 0)
    print('precipitation_probability ', precipitation_probability)
    precipitation = precipitation_probability > 0

    if temperature is not None:
        return {"temp_celsius": str(temperature), "is_precipitation": precipitation}
    else:
        raise HTTPException(status_code=500, detail="Failed to parse temperature from Tomorrow.io response")


def get_weather_forecast_from_tomorrow_io(api_key: str, country: str, city: str, when: datetime):
    url = f"https://api.tomorrow.io/v4/weather/forecast"
    when_s = str(when)[:10]
    #print(when_s)
    # Параметры URL
    params = {
        "location": f"{city}/{country}",
        "apikey": api_key,
    }

    headers = {"accept": "application/json"}

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    #print(response.text)
    data = response.json()
    relevant_data = None
    for daily_data in data.get("timelines", {}).get("daily", []):
        # Сравниваем дату
        if daily_data.get("time", "")[:10] == when_s:
            #print(daily_data.get("time", "")[:10])
            # Извлекаем температуру и осадки
            #values = daily_data.get("data", {}).get("values", {})
            temperature_avg = daily_data.get("values", {}).get("temperatureAvg", None)
            precipitation_avg = daily_data.get("values", {}).get("precipitationProbabilityAvg", 0)
            precipitation_avg = precipitation_avg > 0
            # temperature_avg = daily_data.get("temperatureAvg", None)
            # precipitation_avg = daily_data.get("precipitationProbabilityAvg", 0)
            #
            # # Теперь у вас есть нужные данные
            # relevant_data = {
            #     "temp_celsius": temperature_avg,
            #     "is_precipitation": precipitation_avg,
            # }
            break

    # temperature_avg = 1
    # precipitation_avg = 1
    if temperature_avg is not None:
        return {"temp_celsius": str(temperature_avg), "is_precipitation": precipitation_avg}
    else:
        raise HTTPException(status_code=500, detail="Failed to parse temperature from Tomorrow.io response")

def get_weather_from_weather_api(api_key: str, country: str, city: str, when: datetime):
    configuration = swagger_client.Configuration()
    configuration.api_key['key'] = '3dbe11fc94a34345887200931230612'

    api_instance = swagger_client.APIsApi(swagger_client.ApiClient(configuration))
    q = f"{city}/{country}"

    try:
        # Realtime API
        api_response = api_instance.realtime_weather(q)
        #print(api_response)
    except ApiException as e:
        print("Exception when calling APIsApi->realtime_weather: %s\n" % e)
        raise HTTPException(status_code=500, detail="Failed to get weather data from WeatherAPI")

    #data = api_response.json()

    # Парсинг данных из ответа
    values = api_response.get("current", {}) #.get("values", {})
    temperature = values.get("temp_c", None)
    #temperature = 1

    # Проверка, есть ли осадки
    precipitation_probability = values.get("precip_mm", 0)
    print('precipitation_probability ', precipitation_probability)
    #precipitation_probability = 1
    precipitation = precipitation_probability > 0


    if temperature is not None:
        return {"temp_celsius": str(temperature), "is_precipitation": precipitation}
    else:
        raise HTTPException(status_code=500, detail="Failed to parse temperature from Tomorrow.io response")

def get_weather_forecast_from_weather_api(api_key: str, country: str, city: str, when: datetime):
    configuration = swagger_client.Configuration()
    configuration.api_key['key'] = '3dbe11fc94a34345887200931230612'

    api_instance = swagger_client.APIsApi(swagger_client.ApiClient(configuration))
    q = f"{city}/{country}"

    days = 5

    dt = str(when)[:10]

    try:
        # Forecast API
        api_response = api_instance.forecast_weather(q, days, dt=dt)
        #print(api_response)
    except ApiException as e:
        print("Exception when calling APIsApi->forecast_weather: %s\n" % e)
        raise HTTPException(status_code=500, detail="Failed to get weather data from WeatherAPI")


    #print(response.text)
    #data = response.json()
    relevant_data = None
    for daily_data in api_response.get("forecast", {}).get("forecastday", []):
        # Сравниваем дату
        if daily_data.get("date", "")[:10] == dt:
            #print(daily_data.get("time", "")[:10])
            # Извлекаем температуру и осадки
            #values = daily_data.get("data", {}).get("values", {})
            temperature_avg = daily_data.get("day", {}).get("avgtemp_c", None)
            precipitation_avg = daily_data.get("day", {}).get("totalprecip_mm", 0)
            precipitation_avg = precipitation_avg > 0
            break

    # temperature_avg = 1
    # precipitation_avg = 1
    if temperature_avg is not None:
        return {"temp_celsius": str(temperature_avg), "is_precipitation": precipitation_avg}
    else:
        raise HTTPException(status_code=500, detail="Failed to parse temperature from Tomorrow.io response")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
