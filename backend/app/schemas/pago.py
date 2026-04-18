from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class CrearPagoIntentRequest(BaseModel):
    """Schema para crear un Payment Intent en Stripe"""
    user_id: int = Field(..., description="ID del usuario")
    plan_type: Literal["mensual", "trimestral", "anual"] = Field(..., description="Tipo de plan")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "plan_type": "mensual"
            }
        }


class CrearPagoIntentResponse(BaseModel):
    """Response del Payment Intent"""
    clientSecret: str = Field(..., description="Client secret para completar el pago en cliente")
    paymentIntentId: str = Field(..., description="ID del Payment Intent en Stripe")
    amount: int = Field(..., description="Monto en centavos")
    currency: str = Field(..., description="Moneda ISO 4217")
    plan_type: str = Field(..., description="Tipo de plan")

    class Config:
        json_schema_extra = {
            "example": {
                "clientSecret": "pi_test_1234_secret_5678",
                "paymentIntentId": "pi_test_1234",
                "amount": 9900,
                "currency": "mxn",
                "plan_type": "mensual"
            }
        }


class WebhookEventResponse(BaseModel):
    """Response para validación de webhook"""
    status: str = Field(..., description="Estado del procesamiento")
    message: str = Field(..., description="Mensaje descriptivo")


class PagoHistorial(BaseModel):
    """Historial de pagos del usuario"""
    id: Optional[int] = None
    stripe_payment_intent_id: str
    usuario_id: int
    monto: int
    moneda: str
    plan_type: str
    estado: str  # succeeded, processing, requires_payment_method, canceled
    fecha_creacion: datetime
    fecha_completado: Optional[datetime] = None

    class Config:
        from_attributes = True


class SuscripcionResponse(BaseModel):
    """Detalles de la suscripción activa"""
    es_suscripcion_activa: bool
    tipo_suscripcion_pagada: Optional[str] = None
    fecha_inicio_suscripcion: Optional[datetime] = None
    fecha_fin_suscripcion: Optional[datetime] = None
    dias_restantes: int = 0
    stripe_subscription_id: Optional[str] = None

    class Config:
        from_attributes = True

