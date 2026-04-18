from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserRegister(BaseModel):
    nombre: str = Field(..., example="Juan")
    apellido_paterno: Optional[str] = Field(None, example="Pérez")
    apellido_materno: Optional[str] = Field(None, example="García")
    correo_electronico: EmailStr = Field(..., example="juan.perez@example.com")
    contrasena: str = Field(..., example="password123")
    telefono: Optional[str] = Field(None, example="+521234567890")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    usuario_id: Optional[int] = None
    plan_id: Optional[int] = None
