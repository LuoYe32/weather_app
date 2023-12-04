from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import requests, uvicorn

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
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Роут для прогноза погоды
@app.post("/get_forecast", response_model=WeatherResponse)
def get_forecast(weather_request: WeatherRequest):
    try:
        # Используйте функции запроса к внешним сервисам
        weather_data = get_weather_from_service2(weather_request.country, weather_request.city, weather_request.when)
        # Обработайте данные, если необходимо
        # ...
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

def get_weather_from_tomorrow_io(api_key: str, country: str, city: str, when: datetime):
    # # Реализуйте запрос к первому внешнему сервису
    # # Например, используя библиотеку requests
    # url = f"https://api.service1.com/weather?country={country}&city={city}&when={when}"
    # response = requests.get(url)
    # response.raise_for_status()  # Проверка на ошибки HTTP
    # data = response.json()
    # # Обработка данных, если необходимо
    # # ...
    # return {"temp_celsius": data["temperature"], "is_precipitation": data["precipitation"]}
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
    precipitation = precipitation_probability > 0

    if temperature is not None:
        return {"temp_celsius": str(temperature), "is_precipitation": precipitation}
    else:
        raise HTTPException(status_code=500, detail="Failed to parse temperature from Tomorrow.io response")

def get_weather_from_service2(country: str, city: str, when: datetime):
    # Реализуйте запрос ко второму внешнему сервису
    # Например, используя библиотеку requests
    url = f"https://api.service2.com/forecast?country={country}&city={city}&when={when}"
    response = requests.get(url)
    response.raise_for_status()  # Проверка на ошибки HTTP
    data = response.json()
    # Обработка данных, если необходимо
    # ...
    return {"temp_celsius": data["temperature"], "is_precipitation": data["precipitation"]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
