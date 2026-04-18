"""
Servicio de pagos con Stripe
Maneja la creación de PaymentIntents y webhooks
"""
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import Dict, Optional
from app.core.config import settings

# Configurar API key de Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Mapeo de planes a montos en centavos (MXN)
PLAN_PRICES = {
    "mensual": 9900,      # 99 MXN
    "trimestral": 24900,  # 249 MXN
    "anual": 89900        # 899 MXN
}

# Mapeo de planes a duración en días
PLAN_DURATION_DAYS = {
    "mensual": 30,
    "trimestral": 90,
    "anual": 365
}


def _inferir_tipo_desde_plan(plan_nombre: Optional[str]) -> Optional[str]:
    if not plan_nombre:
        return None
    nombre = plan_nombre.lower()
    if "anual" in nombre:
        return "anual"
    if "trimes" in nombre:
        return "trimestral"
    if "mens" in nombre:
        return "mensual"
    return None


async def validar_usuario_existe(db: AsyncSession, user_id: int) -> bool:
    """Verifica que el usuario existe"""
    query = text("SELECT id FROM usuarios WHERE id = :user_id AND is_deleted = 0")
    result = await db.execute(query, {"user_id": user_id})
    return result.first() is not None


async def obtener_datos_usuario(db: AsyncSession, user_id: int) -> Optional[Dict]:
    """Obtiene datos del usuario para Stripe"""
    query = text("""
        SELECT id, nombre, correo_electronico, stripe_customer_id 
        FROM usuarios 
        WHERE id = :user_id AND is_deleted = 0
    """)
    result = await db.execute(query, {"user_id": user_id})
    return result.mappings().first()


async def obtener_o_crear_stripe_customer(db: AsyncSession, user_id: int) -> str:
    """Obtiene o crea customer en Stripe"""
    usuario = await obtener_datos_usuario(db, user_id)

    if not usuario:
        raise ValueError("Usuario no encontrado")

    # Si ya tiene customer_id, retornarlo
    if usuario["stripe_customer_id"]:
        return usuario["stripe_customer_id"]

    # Crear nuevo customer en Stripe
    customer = stripe.Customer.create(
        email=usuario["correo_electronico"],
        name=usuario["nombre"],
        metadata={"user_id": user_id}
    )

    # Guardar customer_id en BD
    update_query = text("""
        UPDATE usuarios 
        SET stripe_customer_id = :customer_id 
        WHERE id = :user_id
    """)
    await db.execute(update_query, {
        "customer_id": customer.id,
        "user_id": user_id
    })
    await db.commit()

    return customer.id


async def crear_payment_intent(
    db: AsyncSession,
    user_id: int,
    plan_type: str
) -> Dict:
    """Crea un PaymentIntent en Stripe"""

    # Validar plan
    if plan_type not in PLAN_PRICES:
        raise ValueError(f"Plan inválido: {plan_type}. Opciones: {', '.join(PLAN_PRICES.keys())}")

    # Validar usuario
    if not await validar_usuario_existe(db, user_id):
        raise ValueError("Usuario no encontrado")

    # Obtener o crear customer
    customer_id = await obtener_o_crear_stripe_customer(db, user_id)

    # Obtener monto
    amount = PLAN_PRICES[plan_type]

    # Crear PaymentIntent
    payment_intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=settings.STRIPE_CURRENCY,
        customer=customer_id,
        description=f"Suscripción {plan_type} - Step by Step",
        metadata={
            "user_id": user_id,
            "plan_type": plan_type
        }
    )

    return {
        "clientSecret": payment_intent.client_secret,
        "paymentIntentId": payment_intent.id,
        "amount": amount,
        "currency": settings.STRIPE_CURRENCY,
        "plan_type": plan_type
    }


async def activar_suscripcion(
    db: AsyncSession,
    user_id: int,
    plan_type: str,
    payment_intent_id: str
) -> bool:
    """Activa la suscripción del usuario tras pago exitoso"""

    if plan_type not in PLAN_DURATION_DAYS:
        raise ValueError(f"Plan inválido: {plan_type}")

    # Calcular fechas
    fecha_inicio = datetime.now()
    duracion_dias = PLAN_DURATION_DAYS[plan_type]
    fecha_fin = fecha_inicio + timedelta(days=duracion_dias)

    # Actualizar usuario
    update_query = text("""
        UPDATE usuarios 
        SET 
            es_suscripcion_activa = 1,
            tipo_suscripcion_pagada = :plan_type,
            stripe_subscription_id = :payment_intent_id,
            fecha_inicio_suscripcion = :fecha_inicio,
            fecha_fin_suscripcion = :fecha_fin,
            estado = 'activo'
        WHERE id = :user_id
    """)

    await db.execute(update_query, {
        "plan_type": plan_type,
        "payment_intent_id": payment_intent_id,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "user_id": user_id
    })

    await db.commit()
    return True


async def procesar_webhook_payment_intent_succeeded(
    db: AsyncSession,
    payment_intent: Dict
) -> bool:
    """Procesa webhook de pago exitoso"""

    metadata = payment_intent.get("metadata", {})
    user_id = int(metadata.get("user_id"))
    plan_type = metadata.get("plan_type")
    payment_intent_id = payment_intent.get("id")

    if not user_id or not plan_type:
        raise ValueError("Metadatos incompletos en PaymentIntent")

    # Activar suscripción
    await activar_suscripcion(db, user_id, plan_type, payment_intent_id)

    return True


async def procesar_webhook_payment_intent_failed(
    db: AsyncSession,
    payment_intent: Dict
) -> bool:
    """Procesa webhook de pago fallido"""

    metadata = payment_intent.get("metadata", {})
    user_id = int(metadata.get("user_id"))

    # Aquí puedes guardar un log o enviar notificación
    # Por ahora solo lo registramos
    print(f"Pago fallido para usuario {user_id}")

    return True


async def obtener_suscripcion_activa(db: AsyncSession, user_id: int) -> Optional[Dict]:
    """Obtiene detalles de la suscripción activa del usuario"""
    query = text("""
        SELECT 
            u.es_suscripcion_activa,
            u.tipo_suscripcion_pagada,
            u.fecha_inicio_suscripcion,
            u.fecha_fin_suscripcion,
            u.stripe_subscription_id,
            u.fecha_fin_trial,
            p.nombre AS plan_nombre
        FROM usuarios u
        LEFT JOIN planes p ON p.id = u.plan_id
        WHERE u.id = :user_id
    """)
    result = await db.execute(query, {"user_id": user_id})
    suscripcion = result.mappings().first()

    if not suscripcion:
        return None

    ahora = datetime.now()
    plan_nombre = suscripcion.get("plan_nombre")
    tipo_suscripcion = suscripcion.get("tipo_suscripcion_pagada") or _inferir_tipo_desde_plan(plan_nombre)

    # Primero intenta con fechas de suscripción Stripe; si no existen, usa trial como respaldo.
    fecha_fin = suscripcion.get("fecha_fin_suscripcion") or suscripcion.get("fecha_fin_trial")
    fecha_inicio = suscripcion.get("fecha_inicio_suscripcion")

    # Regla de estado:
    # - Si hay fecha_fin, manda la fecha (vencida => inactiva).
    # - Si no hay fecha_fin, usa el flag almacenado en BD.
    es_activa = bool(suscripcion.get("es_suscripcion_activa"))
    if fecha_fin:
        es_activa = fecha_fin > ahora

    dias_restantes = 0
    if fecha_fin:
        delta = fecha_fin - ahora
        dias_restantes = max(0, delta.days)

    return {
        "es_suscripcion_activa": es_activa,
        "tipo_suscripcion_pagada": tipo_suscripcion,
        "fecha_inicio_suscripcion": fecha_inicio,
        "fecha_fin_suscripcion": fecha_fin,
        "dias_restantes": dias_restantes,
        "stripe_subscription_id": suscripcion.get("stripe_subscription_id"),
    }


def verificar_signature_webhook(request_body: bytes, stripe_signature: str) -> Dict:
    """Verifica la firma del webhook de Stripe"""
    try:
        event = stripe.Webhook.construct_event(
            request_body,
            stripe_signature,
            settings.STRIPE_WEBHOOK_SECRET
        )
        return event
    except ValueError:
        raise ValueError("Payload inválido")
    except stripe.error.SignatureVerificationError:
        raise ValueError("Firma de webhook inválida")

