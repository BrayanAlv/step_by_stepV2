from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models import SeguimientoHabito, MascotaVirtual, Habito, Rutina

async def update_mascota_status(db: AsyncSession, user_id: int):
    # Calcular porcentaje de seguimiento de la última semana
    una_semana_atras = datetime.now() - timedelta(days=7)
    
    # Query para obtener todos los habitos del usuario
    query_habitos = text("""
        SELECT h.id FROM habitos h
        JOIN rutinas r ON h.rutina_id = r.id
        WHERE r.usuario_id = :user_id
    """)
    habitos_ids_result = await db.execute(query_habitos, {"user_id": user_id})
    habitos_rows = habitos_ids_result.mappings().all()
    habitos_ids = [row["id"] for row in habitos_rows]
    
    if not habitos_ids:
        return
    
    # Seguimientos totales en la última semana
    # SQLAlchemy .in_ handles the list expansion automatically with text() if using bindparams
    # or we can just use the ORM if list expansion is complex, 
    # but let's try to stick to raw-ish SQL
    
    total_query = text("""
        SELECT COUNT(id) FROM seguimiento_habitos 
        WHERE habito_id IN :habitos_ids AND fecha >= :fecha
    """)
    total_result = await db.execute(total_query, {"habitos_ids": tuple(habitos_ids), "fecha": una_semana_atras.date()})
    total = total_result.scalar() or 0
    
    if total == 0:
        estado_animo = "neutral"
    else:
        # Seguimientos completados (estado = 1)
        completados_query = text("""
            SELECT COUNT(id) FROM seguimiento_habitos 
            WHERE habito_id IN :habitos_ids AND fecha >= :fecha AND estado = 1
        """)
        completados_result = await db.execute(completados_query, {"habitos_ids": tuple(habitos_ids), "fecha": una_semana_atras.date()})
        completados = completados_result.scalar() or 0
        
        porcentaje = (completados / total) * 100
        
        if porcentaje > 80:
            estado_animo = "muy feliz"
        elif porcentaje > 50:
            estado_animo = "feliz"
        elif porcentaje > 20:
            estado_animo = "triste"
        else:
            estado_animo = "deprimido"
            
    # Actualizar mascota
    mascota_query = text("SELECT * FROM mascota_virtual WHERE usuario_id = :user_id")
    mascota_result = await db.execute(mascota_query, {"user_id": user_id})
    mascota_row = mascota_result.mappings().first()
    
    if mascota_row:
        # SQL UPDATE para MascotaVirtual
        update_query = text("""
            UPDATE mascota_virtual 
            SET estado_animo = :estado 
            WHERE usuario_id = :user_id
        """)
        await db.execute(update_query, {"estado": estado_animo, "user_id": user_id})
        await db.commit()

async def add_exp_to_mascota(db: AsyncSession, user_id: int, exp: int):
    mascota_query = text("SELECT * FROM mascota_virtual WHERE usuario_id = :user_id")
    mascota_result = await db.execute(mascota_query, {"user_id": user_id})
    mascota_row = mascota_result.mappings().first()
    
    if mascota_row:
        mascota = MascotaVirtual(**mascota_row)
        new_exp = mascota.experiencia + exp
        new_nivel = mascota.nivel
        
        # Lógica de nivel (simple)
        if new_exp >= new_nivel * 100:
            new_exp -= new_nivel * 100
            new_nivel += 1
            
        # SQL UPDATE para MascotaVirtual
        update_query = text("""
            UPDATE mascota_virtual 
            SET experiencia = :exp, nivel = :nivel 
            WHERE usuario_id = :user_id
        """)
        await db.execute(update_query, {
            "exp": new_exp,
            "nivel": new_nivel,
            "user_id": user_id
        })
        await db.commit()
