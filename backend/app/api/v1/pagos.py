"""
Router para gestionar pagos con Stripe
Endpoints para crear PaymentIntents y procesar webhooks
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models import Usuario
from app.schemas.pago import (
    CrearPagoIntentRequest,
    CrearPagoIntentResponse,
    WebhookEventResponse,
    SuscripcionResponse
)
from app.services import pago_service
import stripe

router = APIRouter(
    prefix="/v1/pagos",
    tags=["Pagos"]
)


@router.post(
    "/crear-intent",
    response_model=CrearPagoIntentResponse,
    summary="Crear Payment Intent para pago",
    description="Crea un PaymentIntent en Stripe para iniciar el flujo de pago. Retorna el clientSecret que debe usarse en el frontend."
)
async def crear_payment_intent(
    pago_request: CrearPagoIntentRequest,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Crea un PaymentIntent en Stripe para una suscripción.

    **Parámetros:**
    - `user_id`: ID del usuario que realiza el pago
    - `plan_type`: Tipo de plan ("mensual", "trimestral", "anual")

    **Montos (MXN):**
    - Mensual: 99 MXN
    - Trimestral: 249 MXN
    - Anual: 899 MXN

    **Retorna:**
    - `clientSecret`: Secret para completar el pago en cliente
    - `paymentIntentId`: ID del PaymentIntent en Stripe
    - `amount`: Monto en centavos
    - `currency`: Moneda (mxn)
    - `plan_type`: Tipo de plan seleccionado
    """
    try:
        # Validar que el usuario actual es quien hace el pago
        if pago_request.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes crear un pago para otro usuario"
            )

        # Crear Payment Intent
        payment_intent_data = await pago_service.crear_payment_intent(
            db,
            pago_request.user_id,
            pago_request.plan_type
        )

        return payment_intent_data

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error con Stripe: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear Payment Intent: {str(e)}"
        )


@router.post(
    "/webhook",
    response_model=WebhookEventResponse,
    summary="Webhook de Stripe",
    description="Endpoint para recibir eventos de Stripe. Solo acepta solicitudes firmadas."
)
async def webhook_stripe(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Procesa webhooks de Stripe.

    **Eventos soportados:**
    - `payment_intent.succeeded`: Pago completado exitosamente
    - `payment_intent.payment_failed`: Pago fallido

    **Seguridad:**
    - Valida la firma del webhook
    - Solo procesa eventos autentificados
    """
    try:
        # Obtener el cuerpo crudo de la solicitud
        request_body = await request.body()
        stripe_signature = request.headers.get("stripe-signature")

        if not stripe_signature:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Falta stripe-signature header"}
            )

        # Verificar y construir el evento
        event = pago_service.verificar_signature_webhook(request_body, stripe_signature)

        # Procesar eventos
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            await pago_service.procesar_webhook_payment_intent_succeeded(db, payment_intent)

            return {
                "status": "success",
                "message": "Pago procesado correctamente"
            }

        elif event["type"] == "payment_intent.payment_failed":
            payment_intent = event["data"]["object"]
            await pago_service.procesar_webhook_payment_intent_failed(db, payment_intent)

            return {
                "status": "failed",
                "message": "Pago rechazado"
            }

        # Otros eventos se ignoran pero se retorna 200
        return {
            "status": "ignored",
            "message": f"Evento {event['type']} recibido pero no procesado"
        }

    except ValueError as e:
        # Error en validación de firma
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Error procesando webhook: {str(e)}"}
        )


@router.get(
    "/suscripcion",
    response_model=SuscripcionResponse,
    summary="Obtener detalles de suscripción activa",
    description="Retorna los detalles de la suscripción pagada activa del usuario"
)
async def obtener_suscripcion(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene detalles de la suscripción activa del usuario actual.

    **Retorna:**
    - `es_suscripcion_activa`: Boolean indicando si hay suscripción activa
    - `tipo_suscripcion_pagada`: Tipo de plan ("mensual", "trimestral", "anual")
    - `fecha_inicio_suscripcion`: Fecha de inicio de la suscripción
    - `fecha_fin_suscripcion`: Fecha de vencimiento
    - `dias_restantes`: Días restantes hasta vencimiento
    - `stripe_subscription_id`: ID del subscription en Stripe
    """
    try:
        suscripcion = await pago_service.obtener_suscripcion_activa(db, current_user.id)

        if not suscripcion:
            return {
                "es_suscripcion_activa": False,
                "tipo_suscripcion_pagada": None,
                "fecha_inicio_suscripcion": None,
                "fecha_fin_suscripcion": None,
                "dias_restantes": 0,
                "stripe_subscription_id": None
            }

        return suscripcion

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo suscripción: {str(e)}"
        )

