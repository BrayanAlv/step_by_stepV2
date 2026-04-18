from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

async def get_usuarios(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    es_premium: Optional[bool] = None,
):
    base_query = """
        SELECT u.id, u.nombre, u.correo_electronico, u.foto_perfil, 
               p.nombre as plan_nombre, 
               u.es_suscripcion_activa,
               u.tipo_suscripcion_pagada,
               u.fecha_fin_suscripcion,
               (p.nombre NOT IN ('Gratuito', 'Free') OR (p.nombre IS NULL AND u.es_suscripcion_activa = 1)) as es_premium
        FROM usuarios u
        LEFT JOIN planes p ON u.plan_id = p.id
        WHERE u.deleted_at IS NULL
    """

    params = {"skip": skip, "limit": limit}
    if es_premium is True:
        base_query += " AND (p.nombre NOT IN ('Gratuito', 'Free') OR u.es_suscripcion_activa = 1)"
    elif es_premium is False:
        base_query += " AND (p.nombre IN ('Gratuito', 'Free') OR p.nombre IS NULL) AND u.es_suscripcion_activa = 0"

    base_query += " ORDER BY u.id LIMIT :skip, :limit"
    result = await db.execute(text(base_query), params)
    return result.mappings().all()

async def get_usuario_by_id(db: AsyncSession, usuario_id: int):
    result = await db.execute(text("""
        SELECT id, nombre, foto_perfil
        FROM usuarios
        WHERE id = :usuario_id AND deleted_at IS NULL
    """), {"usuario_id": usuario_id})
    return result.mappings().first()
