import json
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models import Usuario, RutinaIAGenerada
from app.schemas.rutina import (
    IAInput,
    RutinaIAResponse,
    NanoBotChatInput,
    NanoBotChatResponse,
    RutinaCreate,
)
from app.services.ai_service import ai_service
from app.services import notification_service, rutinas_service

router = APIRouter(prefix="/ia", tags=["IA"])


def _sanitize_ai_categoria_ids(
    rutina_payload: dict[str, Any],
    valid_rutina_categoria_ids: set[int],
    valid_habito_categoria_ids: set[int],
) -> dict[str, Any]:
    """Ajusta categoria_id inválidos de IA a None para evitar errores FK."""
    sanitized = dict(rutina_payload)

    rutina_categoria_id = sanitized.get("categoria_id")
    if rutina_categoria_id is not None and rutina_categoria_id not in valid_rutina_categoria_ids:
        sanitized["categoria_id"] = None

    habitos = sanitized.get("habitos", [])
    if isinstance(habitos, list):
        normalized_habitos: list[dict[str, Any]] = []
        for habito in habitos:
            if not isinstance(habito, dict):
                continue
            habito_copy = dict(habito)
            habito_categoria_id = habito_copy.get("categoria_id")
            if habito_categoria_id is not None and habito_categoria_id not in valid_habito_categoria_ids:
                habito_copy["categoria_id"] = None
            normalized_habitos.append(habito_copy)
        sanitized["habitos"] = normalized_habitos

    return sanitized

@router.post("/routine/generate", response_model=RutinaIAResponse, summary="Generar rutina con IA")
async def generate_ai_routine(
    input_data: IAInput, 
    current_user: Usuario = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """
    Generar una rutina personalizada con IA.
    """
    try:
        # Obtener todas las categorías reales para ayudar a la IA (incluyendo subcategorías)
        categories_db = await rutinas_service.get_categorias(db, include_subcategories=True)
        categories_data = [{"id": c.id, "nombre": c.nombre} for c in categories_db]
        
        # Obtener categorías de hábitos
        habits_categories_db = await rutinas_service.get_habito_categorias(db)
        habits_categories_data = [{"id": c.id, "nombre": c.nombre} for c in habits_categories_db]
        
        # Aquí se podrían obtener hábitos previos del usuario para enriquecer el prompt
        user_info = input_data.model_dump()
        
        # Llamar al servicio de IA con las categorías disponibles
        ai_response = await ai_service.generate_routine(
            user_info, 
            categories=categories_data,
            habit_categories=habits_categories_data
        )
        
        # Guardar en historial
        historial = RutinaIAGenerada(
            usuario_id=current_user.id,
            prompt_usado=json.dumps(user_info),
            respuesta_ia=json.dumps(ai_response),
            modelo_ia=ai_service.get_last_used_model()
        )
        db.add(historial)
        
        # Notificación de rutina generada
        await notification_service.send_push_notification(
            db,
            user_id=current_user.id,
            title="Rutina lista",
            body="Tu rutina personalizada creada con IA ya está lista ✨",
            tipo="ia"
        )
        
        await db.commit()
        
        return ai_response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar rutina con IA: {str(e)}"
        )

@router.post("/motivation/generate", summary="Generar frase motivacional con IA")
async def generate_motivation(
    current_user: Usuario = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """
    Genera una frase motivacional basada en las rutinas actuales del usuario.
    """
    try:
        # Obtener nombres de rutinas actuales del usuario
        query = text("SELECT nombre FROM rutinas WHERE usuario_id = :u_id AND deleted_at IS NULL")
        result = await db.execute(query, {"u_id": current_user.id})
        routines = [row[0] for row in result.all()]
        
        summary = ", ".join(routines) if routines else "No tiene rutinas activas"
        
        phrase = await ai_service.generate_motivational_phrase(summary)
        
        return {"frase_motivacional": phrase}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar frase: {str(e)}"
        )

@router.post(
    "/chat",
    response_model=NanoBotChatResponse,
    summary="Nano Bot de rutinas",
    description="Chat de habilidades mínimas para consultar rutinas del usuario o crear una rutina desde prompt.",
)
async def nano_bot_chat(
    input_data: NanoBotChatInput,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        intent = ai_service.detect_chat_intent(input_data.mensaje, input_data.intent)

        if intent == "consultar_rutinas":
            rutinas = await rutinas_service.get_rutinas_por_usuario(db, current_user.id)
            return {
                "intent_detectado": "consultar_rutinas",
                "mensaje": f"Encontré {len(rutinas)} rutina(s) activas.",
                "rutinas": rutinas,
            }

        if intent == "crear_rutina":
            categories_db = await rutinas_service.get_categorias(db, include_subcategories=True)
            categories_data = [{"id": c.id, "nombre": c.nombre} for c in categories_db]
            valid_rutina_categoria_ids = {c["id"] for c in categories_data}

            habits_categories_db = await rutinas_service.get_habito_categorias(db)
            habits_categories_data = [{"id": c.id, "nombre": c.nombre} for c in habits_categories_db]
            valid_habito_categoria_ids = {c["id"] for c in habits_categories_data}

            user_info = ai_service.build_routine_prompt_data_from_chat(input_data.mensaje)
            ai_response = await ai_service.generate_routine(
                user_info,
                categories=categories_data,
                habit_categories=habits_categories_data,
            )

            rutina_payload = ai_response.get("rutina")
            if not rutina_payload:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="La IA no devolvió una rutina válida",
                )

            rutina_payload = _sanitize_ai_categoria_ids(
                rutina_payload,
                valid_rutina_categoria_ids,
                valid_habito_categoria_ids,
            )

            rutina_validada = RutinaCreate.model_validate(rutina_payload)

            historial = RutinaIAGenerada(
                usuario_id=current_user.id,
                prompt_usado=json.dumps(user_info),
                respuesta_ia=json.dumps(ai_response),
                modelo_ia=ai_service.get_last_used_model(),
            )

            if input_data.guardar_rutina:
                rutina_creada = await rutinas_service.create_rutina(db, rutina_validada, current_user.id)
                historial.rutina_id = rutina_creada.id
                db.add(historial)
                await db.commit()
                return {
                    "intent_detectado": "crear_rutina",
                    "mensaje": "Rutina creada correctamente desde el chat.",
                    "rutina_creada": rutina_creada,
                }

            db.add(historial)
            await db.commit()
            return {
                "intent_detectado": "crear_rutina",
                "mensaje": "Te comparto una rutina sugerida. Activa guardar_rutina para persistirla.",
                "rutina_sugerida": rutina_validada,
            }

        return {
            "intent_detectado": "fallback",
            "mensaje": "Puedo ayudarte a consultar tus rutinas o crear una rutina desde un prompt.",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en nano bot: {str(e)}",
        )
