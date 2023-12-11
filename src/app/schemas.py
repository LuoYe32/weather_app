from __future__ import print_function

from pydantic import BaseModel

# class WeatherRequest(BaseModel):
#     country: str = (Query(..., description="Country"),)
#     city: str = Query(..., description="City")
#     when: datetime = (Query(datetime.now(), description="Datetime"),)


class WeatherResponse(BaseModel):
    temp_celsius: str
    is_precipitation: bool
