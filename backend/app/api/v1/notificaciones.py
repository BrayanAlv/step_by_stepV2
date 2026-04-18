from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models import Usuario
from app.schemas.notificacion import FCMTokenCreate, NotificacionHistorialResponse, NotificacionPorToken
from app.services.notificaciones_service import notification_service

router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])

@router.post("/dispositivo", summary="Registrar token FCM")
async def register_token(
    token_in: FCMTokenCreate, 
    current_user: Usuario = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """
    Registra o actualiza el token FCM del dispositivo actual para el usuario autenticado.
    """
    await notification_service.register_device_token(
        db, current_user.id, token_in.token_fcm, token_in.plataforma
    )
    return {"message": "Token registrado correctamente", "data": {}}

@router.get("/", response_model=List[NotificacionHistorialResponse], summary="Obtener historial de notificaciones")
async def get_notifications_history(
    current_user: Usuario = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna el historial de notificaciones enviadas al usuario.
    """
    return await notification_service.get_history(db, current_user.id)

@router.patch("/{id}/leer", summary="Marcar notificación como leída")
async def mark_notification_read(
    id: int, 
    current_user: Usuario = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """
    Marca una notificación específica como leída.
    """
    await notification_service.mark_as_read(db, current_user.id, id)
    return {"message": "Notificación marcada como leída", "data": {}}

@router.delete("/dispositivo", summary="Eliminar token FCM")
async def delete_token(
    token_fcm: str = None, 
    current_user: Usuario = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina el token FCM especificado (o todos si no se provee) para el usuario autenticado.
    """
    await notification_service.delete_device_token(db, current_user.id, token_fcm)
    return {"message": "Token eliminado correctamente", "data": {}}

@router.post("/enviar-por-token", summary="Enviar notificación por token FCM")
async def send_notification_by_token(
    notification_in: NotificacionPorToken
):
    """
    Envía una notificación push directamente a un token FCM específico.

    **Parámetros:**
    - **token_fcm**: Token del dispositivo FCM destino (requerido)
    - **titulo**: Título de la notificación (requerido)
    - **mensaje**: Cuerpo de la notificación (requerido)
    - **data**: Datos adicionales en formato JSON (opcional)
    - **tipo**: Tipo de notificación: "general", "recordatorio", "motivacion", etc. (opcional)

    **Ejemplo de uso:**
    ```json
    {
        "token_fcm": "abc123xyz...",
        "titulo": "¡Recordatorio!",
        "mensaje": "Es hora de tu rutina matutina",
        "data": {"rutina_id": 1, "accion": "abrir_rutina"},
        "tipo": "recordatorio"
    }
    ```
    """
    try:
        result = await notification_service.send_push_notification_by_token(
            title=notification_in.titulo,
            body=notification_in.mensaje,
            token_fcm=notification_in.token_fcm,
            data=notification_in.data,
            tipo=notification_in.tipo
        )
        return {
            "message": "Notificación enviada correctamente",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al enviar notificación: {str(e)}"
        )
