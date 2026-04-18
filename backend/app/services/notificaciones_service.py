import logging
import firebase_admin
from firebase_admin import credentials, messaging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.config import settings
from datetime import datetime

logger = logging.getLogger(__name__)

# Inicializar Firebase si está habilitado
firebase_app = None
if settings.FIREBASE_ENABLED:
    try:
        import os
        json_path = settings.FIREBASE_SERVICE_ACCOUNT_JSON
        
        if json_path and os.path.exists(json_path):
            try:
                # Verificar si ya existe una app inicializada
                firebase_app = firebase_admin.get_app()
                logger.info("Firebase Admin SDK ya estaba inicializado")
            except ValueError:
                # No existe, inicializar
                cred = credentials.Certificate(json_path)
                firebase_app = firebase_admin.initialize_app(cred)
                logger.info(f"Firebase Admin SDK inicializado desde archivo: {json_path}")
        else:
            logger.warning("FIREBASE_ENABLED es True pero no se encontró FIREBASE_SERVICE_ACCOUNT_JSON válido.")
            settings.FIREBASE_ENABLED = False
    except Exception as e:
        logger.error(f"Error inicializando Firebase Admin SDK: {e}")
        settings.FIREBASE_ENABLED = False

class NotificationService:
    async def register_device_token(self, db: AsyncSession, user_id: int, token_fcm: str, plataforma: str):
        # MySQL doesn't support ON DUPLICATE KEY with text(), better to use raw sql for upsert
        query = text("""
            INSERT INTO dispositivos_fcm (usuario_id, token_fcm, plataforma, activo)
            VALUES (:u_id, :token, :plat, 1)
            ON DUPLICATE KEY UPDATE 
            usuario_id = :u_id, plataforma = :plat, activo = 1, updated_at = CURRENT_TIMESTAMP
        """)
        await db.execute(query, {"u_id": user_id, "token": token_fcm, "plat": plataforma})
        await db.commit()

    async def delete_device_token(self, db: AsyncSession, user_id: int, token_fcm: str = None):
        if token_fcm:
            query = text("DELETE FROM dispositivos_fcm WHERE usuario_id = :u_id AND token_fcm = :token")
            await db.execute(query, {"u_id": user_id, "token": token_fcm})
        else:
            query = text("DELETE FROM dispositivos_fcm WHERE usuario_id = :u_id")
            await db.execute(query, {"u_id": user_id})
        await db.commit()

    async def send_push_notification(self, db: AsyncSession, user_id: int, title: str, body: str, data: dict = None, tipo: str = "general"):
        # 1. Guardar en historial
        await self.save_notification_history(db, user_id, title, body, tipo)
        
        if not settings.FIREBASE_ENABLED or not firebase_app:
            logger.info(f"[MOCK PUSH] User {user_id}: {title} - {body}")
            return

        # 2. Obtener tokens
        try:
            query = text("SELECT token_fcm FROM dispositivos_fcm WHERE usuario_id = :u_id AND activo = 1")
            result = await db.execute(query, {"u_id": user_id})
            tokens = [row[0] for row in result.all()]

            if not tokens:
                logger.info(f"No tokens registrados para usuario {user_id}")
                return

            # 3. Enviar vía FCM
            message = messaging.MulticastMessage(
                notification=messaging.Notification(title=title, body=body),
                data=data,
                tokens=tokens
            )
            # Note: messaging.send_multicast expects a list of tokens
            response = messaging.send_multicast(message)
            logger.info(f"Notificaciones enviadas: {response.success_count} exitosas, {response.failure_count} fallidas")
        except Exception as e:
            logger.error(f"Error enviando notificación FCM: {e}")

    async def send_push_notification_by_token(self, title: str, body: str, token_fcm: str, data: dict = None, tipo: str = "general"):
        """
        Envía una notificación push directamente a un token FCM específico.
        No requiere autenticación, solo el token del dispositivo.
        Firebase requiere que todos los valores en data sean strings.
        """
        if not settings.FIREBASE_ENABLED or not firebase_app:
            logger.info(f"[MOCK PUSH] Token {token_fcm}: {title} - {body}")
            return {"status": "mock", "message": "Notificación enviada en modo mock"}

        try:
            # Convertir todos los valores en data a strings (requisito de Firebase)
            converted_data = None
            if data:
                converted_data = {
                    str(k): str(v) for k, v in data.items()
                }

            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=converted_data,
                token=token_fcm
            )
            response = messaging.send(message)
            logger.info(f"Notificación enviada exitosamente. ID: {response}")
            return {"status": "success", "message_id": response}
        except Exception as e:
            logger.error(f"Error enviando notificación FCM por token: {e}")
            return {"status": "error", "message": str(e)}

    async def save_notification_history(self, db: AsyncSession, user_id: int, title: str, body: str, tipo: str):
        query = text("""
            INSERT INTO notificaciones_historial (usuario_id, titulo, mensaje, tipo, leida)
            VALUES (:u_id, :title, :msg, :tipo, 0)
        """)
        await db.execute(query, {"u_id": user_id, "title": title, "msg": body, "tipo": tipo})
        await db.commit()

    async def get_history(self, db: AsyncSession, user_id: int):
        query = text("SELECT * FROM notificaciones_historial WHERE usuario_id = :u_id ORDER BY created_at DESC")
        result = await db.execute(query, {"u_id": user_id})
        return result.mappings().all()

    async def mark_as_read(self, db: AsyncSession, user_id: int, notification_id: int):
        query = text("UPDATE notificaciones_historial SET leida = 1 WHERE id = :id AND usuario_id = :u_id")
        await db.execute(query, {"id": notification_id, "u_id": user_id})
        await db.commit()

    async def schedule_habit_reminder(self, user_id: int, title: str, body: str, scheduled_time):
        # Esta función será llamada desde los endpoints para programar recordatorios en el scheduler global
        # Importación tardía para evitar circular dependency
        from app.main import scheduler
        from app.core.database import SessionLocal
        import asyncio
        
        async def send_scheduled():
            async with SessionLocal() as db:
                await self.send_push_notification(db, user_id, title, body, tipo="recordatorio")

        def job_wrapper():
            # Ejecutar corutina en el event loop principal si es posible o crear uno nuevo
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(send_scheduled())
                else:
                    loop.run_until_complete(send_scheduled())
            except RuntimeError:
                asyncio.run(send_scheduled())

        scheduler.add_job(job_wrapper, 'cron', hour=scheduled_time.hour, minute=scheduled_time.minute)
        logger.info(f"Recordatorio programado para usuario {user_id} a las {scheduled_time}")

    async def send_daily_motivation(self, db: AsyncSession, user_id: int, phrase: str):
        await self.send_push_notification(db, user_id, "Tu frase del día", phrase, tipo="motivacion")

notification_service = NotificationService()
