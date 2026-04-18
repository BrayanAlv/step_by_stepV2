from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import datetime, timedelta
import math

class SeguidorBase(BaseModel):
    seguido_id: int

class SeguidorCreate(SeguidorBase):
    pass

class Seguidor(SeguidorBase):
    id: int
    seguidor_id: int
    fecha_seguimiento: datetime
    class Config:
        from_attributes = True

class UsuarioSimple(BaseModel):
    id: int
    nombre: str
    foto_perfil: Optional[str] = None
    class Config:
        from_attributes = True

class UsuarioConSuscripcion(BaseModel):
    id: int
    nombre: str
    correo_electronico: str
    foto_perfil: Optional[str] = None
    plan_nombre: Optional[str] = None
    es_premium: Optional[bool] = False
    es_suscripcion_activa: Optional[bool] = False
    tipo_suscripcion_pagada: Optional[str] = None
    fecha_fin_suscripcion: Optional[datetime] = None

    class Config:
        from_attributes = True

class SuscripcionDetalle(BaseModel):
    plan_id: Optional[int] = None
    plan_nombre: str = "Gratuito"
    fecha_fin_trial: Optional[datetime] = None
    dias_restantes: int = 0
    dias_trial_totales: int = 14
    es_premium: bool = False

    # Campos opcionales para no romper endpoints actuales
    fecha_inicio_plan: Optional[datetime] = None
    duracion_plan_dias: Optional[int] = None

    @model_validator(mode="after")
    def calcular_dias_restantes(self):
        duraciones_por_plan = {
            1: 14,   # Gratuito
            2: 30,   # Pro Mensual
            3: 365,  # Elite Anual
            4: 30,   # Equipo
        }

        duracion = self.duracion_plan_dias or duraciones_por_plan.get(self.plan_id) or self.dias_trial_totales or 14
        self.dias_trial_totales = duracion

        if self.fecha_fin_trial is None and self.fecha_inicio_plan is not None:
            self.fecha_fin_trial = self.fecha_inicio_plan + timedelta(days=duracion)

        if self.fecha_fin_trial:
            ahora = datetime.now(self.fecha_fin_trial.tzinfo) if self.fecha_fin_trial.tzinfo else datetime.utcnow()
            segundos_restantes = (self.fecha_fin_trial - ahora).total_seconds()
            self.dias_restantes = max(math.ceil(segundos_restantes / 86400), 0)

        return self

class PlanUpdate(BaseModel):
    plan_id: int
