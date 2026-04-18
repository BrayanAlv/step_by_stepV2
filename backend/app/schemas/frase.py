from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FraseMotivacionalBase(BaseModel):
    texto: str
    autor: Optional[str] = "Anónimo"
    categoria: Optional[str] = None

class FraseMotivacionalCreate(FraseMotivacionalBase):
    pass

class FraseMotivacional(FraseMotivacionalBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
