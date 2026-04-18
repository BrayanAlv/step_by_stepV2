from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ComentarioBase(BaseModel):
    publicacion_id: int
    contenido: str

class ComentarioCreate(ComentarioBase):
    pass

class ComentarioContenidoCreate(BaseModel):
    contenido: str

class Comentario(ComentarioBase):
    id: int
    usuario_id: int
    fecha: datetime

    class Config:
        from_attributes = True
