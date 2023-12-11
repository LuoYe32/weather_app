# Weather Service

This service provides weather information using FastAPI.

## Setup

1. Install dependencies:

   ```
   pip install -r requirements.txt
2. Run the service:

    ```
    uvicorn main:app --reload
---

## Usage

* Access the API documentation at http://localhost:8000/docs for interactive documentation.
* Make API requests to: 
    * http://localhost:8000/get_now to get current weather information.
    * http://localhost:8000/get_forecast to get weather forecast up to 5 days.
---

## Docker
To run the service using Docker:

1. Build the Docker image:

    ```
    docker build -t weather_app
2. Run the Docker container:
    ```
     docker run -d --name weather_app -p 8000:80 weather_app
3. Stop the Docker container
    ```
    docker stop weather_app
### Used web services
* [Tomorrow.io](https://www.tomorrow.io/weather-api/)
* [WeatherAPI](https://www.weatherapi.com)
