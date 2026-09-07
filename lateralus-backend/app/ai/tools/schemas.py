from pydantic import BaseModel


class GetWeatherResponse(BaseModel):
    city: str
    temp_c: int
    condition: str