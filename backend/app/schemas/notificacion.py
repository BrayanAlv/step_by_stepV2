from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from enum import Enum as PyEnum

class Plataforma(str, PyEnum):
    web = "web"
    android = "android"
    ios = "ios"
    movil = "movil"
    mobile = "mobile"

class FCMTokenCreate(BaseModel):
    token_fcm: str
    plataforma: Plataforma

class NotificacionHistorialResponse(BaseModel):
    id: int
    titulo: str
    mensaje: str
    tipo: Optional[str]
    leida: bool
    created_at: datetime
    class Config:
        from_attributes = True

class SuscripcionUpdate(BaseModel):
    slug: str
    activo: bool

class NotificacionSend(BaseModel):
    usuario_id: int
    titulo: str
    mensaje: str
    data: Optional[dict] = None

class NotificacionMasiva(BaseModel):
    slug_canal: str
    titulo: str
    mensaje: str
    data: Optional[dict] = None

class NotificacionPorToken(BaseModel):
    """Schema para enviar notificación directa a un token FCM"""
    token_fcm: str
    titulo: str
    mensaje: str
    data: Optional[dict] = None
    tipo: Optional[str] = "general"
