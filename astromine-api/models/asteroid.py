from pydantic import BaseModel
from typing import Optional

class AsteroideResponse(BaseModel):
    id: int
    nome: str
    classe: Optional[str] = None
    diametro: Optional[float] = None
    formato: Optional[str] = None
    massa: Optional[float] = None
    densidade: Optional[float] = None
    volume: Optional[float] = None
    distancia_min_terra: Optional[float] = None

    class Config:
        orm_mode = True

# class Asteroid(BaseModel):
#     # id: Optional[int] = None
#     name: str
#     estimated_size_min: float
#     estimated_size_max: float
#     velocity_kph: float
#     distance_from_earth_km: float
#     orbital_class: str
#     is_potentially_hazardous: bool
#     created_at: Optional[str] = None

