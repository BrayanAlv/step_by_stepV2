from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class SeguimientoCreate(BaseModel):
    habito_id: int = Field(..., example=1)
    fecha: Optional[date] = Field(None, example="2023-10-27")
    estado: bool = Field(True, example=True)
    nota: Optional[str] = Field(None, example="Me sentí con mucha energía")
    estado_animo: Optional[str] = Field(None, example="Felicidad")
