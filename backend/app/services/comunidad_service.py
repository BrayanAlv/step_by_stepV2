from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

async def get_comentarios_por_rutina(db: AsyncSession, rutina_id: int):
    pub_result = await db.execute(text("""
        SELECT id
        FROM publicaciones_comunidad
        WHERE rutina_id = :rutina_id AND deleted_at IS NULL
        LIMIT 1
    """), {"rutina_id": rutina_id})
    publicacion = pub_result.mappings().first()

    if not publicacion:
        return []

    comentarios_result = await db.execute(text("""
        SELECT id, publicacion_id, usuario_id, contenido, fecha
        FROM comentarios
        WHERE publicacion_id = :publicacion_id AND deleted_at IS NULL
        ORDER BY fecha DESC, id DESC
    """), {"publicacion_id": publicacion["id"]})
    return comentarios_result.mappings().all()

async def create_comentario_por_rutina(
    db: AsyncSession,
    rutina_id: int,
    usuario_id: int,
    contenido: str,
):
    rutina_result = await db.execute(text("""
        SELECT id
        FROM rutinas
        WHERE id = :rutina_id AND is_deleted = 0
        LIMIT 1
    """), {"rutina_id": rutina_id})
    if not rutina_result.first():
        return None

    pub_result = await db.execute(text("""
        SELECT id
        FROM publicaciones_comunidad
        WHERE rutina_id = :rutina_id AND deleted_at IS NULL
        LIMIT 1
    """), {"rutina_id": rutina_id})
    publicacion = pub_result.mappings().first()

    if not publicacion:
        insert_pub = await db.execute(text("""
            INSERT INTO publicaciones_comunidad (usuario_id, rutina_id, descripcion)
            VALUES (:usuario_id, :rutina_id, NULL)
        """), {"usuario_id": usuario_id, "rutina_id": rutina_id})
        publicacion_id = insert_pub.lastrowid
    else:
        publicacion_id = publicacion["id"]

    insert_com = await db.execute(text("""
        INSERT INTO comentarios (publicacion_id, usuario_id, contenido)
        VALUES (:publicacion_id, :usuario_id, :contenido)
    """), {
        "publicacion_id": publicacion_id,
        "usuario_id": usuario_id,
        "contenido": contenido,
    })
    await db.commit()
    comentario_id = insert_com.lastrowid

    comentario_result = await db.execute(text("""
        SELECT id, publicacion_id, usuario_id, contenido, fecha
        FROM comentarios
        WHERE id = :comentario_id
    """), {"comentario_id": comentario_id})
    return comentario_result.mappings().first()

async def delete_comentario(
    db: AsyncSession,
    comentario_id: int,
    usuario_id: int,
) -> bool:
    result = await db.execute(text("""
        SELECT id
        FROM comentarios
        WHERE id = :comentario_id
          AND usuario_id = :usuario_id
          AND deleted_at IS NULL
        LIMIT 1
    """), {"comentario_id": comentario_id, "usuario_id": usuario_id})
    comentario = result.first()
    if not comentario:
        return False

    await db.execute(text("""
        UPDATE comentarios
        SET deleted_at = CURRENT_TIMESTAMP
        WHERE id = :comentario_id
    """), {"comentario_id": comentario_id})
    await db.commit()
    return True

