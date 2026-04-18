"""
Servicios para gestionar Rutinas y Hábitos.
Implementa lógica CRUD completa con soft delete.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from sqlalchemy.orm import selectinload
from app.models import Rutina, Habito, Usuario, CategoriaRutina, HabitoCategoria
from app.schemas.rutina import (
    CategoriaRutinaCreate, HabitoCreate, HabitoUpdate,
    RutinaCreate, RutinaUpdate
)
from typing import List, Optional
from datetime import datetime

# ============================================================================
# RUTINAS - CRUD COMPLETO
# ============================================================================

async def get_rutinas(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Obtiene todas las rutinas no eliminadas con sus hábitos."""
    result = await db.execute(
        select(Rutina)
        .options(selectinload(Rutina.habitos))
        .where(Rutina.is_deleted == False)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_rutinas_por_usuario(db: AsyncSession, usuario_id: int, skip: int = 0, limit: int = 100):
    """Obtiene todas las rutinas activas de un usuario específico."""
    result = await db.execute(
        select(Rutina)
        .options(selectinload(Rutina.habitos))
        .where(
            Rutina.usuario_id == usuario_id,
            Rutina.is_deleted == False
        )
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_rutina_por_id(db: AsyncSession, rutina_id: int) -> Optional[Rutina]:
    """Obtiene una rutina específica con sus hábitos."""
    result = await db.execute(
        select(Rutina)
        .options(selectinload(Rutina.habitos))
        .where(
            Rutina.id == rutina_id,
            Rutina.is_deleted == False
        )
    )
    return result.scalar_one_or_none()

async def create_rutina(
    db: AsyncSession,
    rutina_in: RutinaCreate,
    usuario_id: int
) -> Rutina:
    """
    Crea una nueva rutina con sus hábitos asociados.

    Args:
        db: Sesión de BD
        rutina_in: Datos de la rutina a crear
        usuario_id: ID del usuario propietario

    Returns:
        La rutina creada con sus hábitos
    """
    # Crear rutina
    db_rutina = Rutina(
        usuario_id=usuario_id,
        nombre=rutina_in.nombre,
        momento_dia=rutina_in.momento_dia,
        es_publica=rutina_in.es_publica,
        categoria_id=rutina_in.categoria_id
    )
    db.add(db_rutina)
    await db.flush()  # Obtenemos el ID generado

    # Crear hábitos asociados
    for habito_in in rutina_in.habitos:
        db_habito = Habito(
            rutina_id=db_rutina.id,
            nombre=habito_in.nombre,
            descripcion=habito_in.descripcion,
            categoria_id=habito_in.categoria_id,
            tiempo_programado=habito_in.tiempo_programado,
            tiempo_duracion_min=habito_in.tiempo_duracion_min,
            orden=habito_in.orden
        )
        db.add(db_habito)

    await db.commit()
    await db.refresh(db_rutina, ["habitos"])
    return db_rutina

async def update_rutina(
    db: AsyncSession,
    rutina_id: int,
    rutina_update: RutinaUpdate,
    usuario_id: int
) -> Optional[Rutina]:
    """
    Actualiza los campos editables de una rutina.
    Solo el propietario puede actualizar.

    Args:
        db: Sesión de BD
        rutina_id: ID de la rutina
        rutina_update: Datos a actualizar
        usuario_id: ID del usuario (para verificar permisos)

    Returns:
        La rutina actualizada o None si no existe
    """
    result = await db.execute(
        select(Rutina).where(
            Rutina.id == rutina_id,
            Rutina.usuario_id == usuario_id,
            Rutina.is_deleted == False
        )
    )
    db_rutina = result.scalar_one_or_none()

    if not db_rutina:
        return None

    # Actualizar solo los campos no nulos
    update_data = rutina_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_rutina, field, value)

    db_rutina.updated_at = datetime.now()
    await db.commit()
    await db.refresh(db_rutina, ["habitos"])
    return db_rutina

async def delete_rutina(
    db: AsyncSession,
    rutina_id: int,
    usuario_id: int
) -> bool:
    """
    Realiza soft delete de una rutina (marca como eliminada).
    Solo el propietario puede eliminar.

    Args:
        db: Sesión de BD
        rutina_id: ID de la rutina
        usuario_id: ID del usuario

    Returns:
        True si se eliminó, False si no existe
    """
    result = await db.execute(
        select(Rutina).where(
            Rutina.id == rutina_id,
            Rutina.usuario_id == usuario_id,
            Rutina.is_deleted == False
        )
    )
    db_rutina = result.scalar_one_or_none()

    if not db_rutina:
        return False

    db_rutina.is_deleted = True
    db_rutina.deleted_at = datetime.now()

    # También eliminar lógicamente los hábitos asociados
    habitos = (await db.execute(
        select(Habito).where(Habito.rutina_id == rutina_id)
    )).scalars().all()

    for habito in habitos:
        habito.is_deleted = True
        habito.deleted_at = datetime.now()

    await db.commit()
    return True

async def restore_rutina(
    db: AsyncSession,
    rutina_id: int,
    usuario_id: int
) -> Optional[Rutina]:
    """
    Restaura una rutina eliminada (soft delete).

    Args:
        db: Sesión de BD
        rutina_id: ID de la rutina
        usuario_id: ID del usuario propietario

    Returns:
        La rutina restaurada o None
    """
    result = await db.execute(
        select(Rutina).where(
            Rutina.id == rutina_id,
            Rutina.usuario_id == usuario_id,
            Rutina.is_deleted == True
        )
    )
    db_rutina = result.scalar_one_or_none()

    if not db_rutina:
        return None

    db_rutina.is_deleted = False
    db_rutina.deleted_at = None

    # Restaurar hábitos asociados
    habitos = (await db.execute(
        select(Habito).where(Habito.rutina_id == rutina_id)
    )).scalars().all()

    for habito in habitos:
        habito.is_deleted = False
        habito.deleted_at = None

    await db.commit()
    await db.refresh(db_rutina, ["habitos"])
    return db_rutina

# ============================================================================
# HÁBITOS - CRUD COMPLETO
# ============================================================================

async def get_habitos_por_rutina(db: AsyncSession, rutina_id: int) -> List[Habito]:
    """Obtiene todos los hábitos activos de una rutina."""
    result = await db.execute(
        select(Habito).where(
            Habito.rutina_id == rutina_id,
            Habito.is_deleted == False
        )
        .order_by(Habito.orden)
    )
    return result.scalars().all()

async def get_habito_por_id(db: AsyncSession, habito_id: int) -> Optional[Habito]:
    """Obtiene un hábito específico."""
    result = await db.execute(
        select(Habito).where(
            Habito.id == habito_id,
            Habito.is_deleted == False
        )
    )
    return result.scalar_one_or_none()

async def create_habito(
    db: AsyncSession,
    habito_in: HabitoCreate,
    rutina_id: int
) -> Habito:
    """
    Crea un nuevo hábito en una rutina.

    Args:
        db: Sesión de BD
        habito_in: Datos del hábito
        rutina_id: ID de la rutina

    Returns:
        El hábito creado
    """
    db_habito = Habito(
        rutina_id=rutina_id,
        nombre=habito_in.nombre,
        descripcion=habito_in.descripcion,
        categoria_id=habito_in.categoria_id,
        tiempo_programado=habito_in.tiempo_programado,
        tiempo_duracion_min=habito_in.tiempo_duracion_min,
        orden=habito_in.orden
    )
    db.add(db_habito)
    await db.commit()
    await db.refresh(db_habito)
    return db_habito

async def update_habito(
    db: AsyncSession,
    habito_id: int,
    habito_update: HabitoUpdate,
    usuario_id: int
) -> Optional[Habito]:
    """
    Actualiza un hábito existente.
    Solo el propietario de la rutina puede actualizar.

    Args:
        db: Sesión de BD
        habito_id: ID del hábito
        habito_update: Datos a actualizar
        usuario_id: ID del usuario propietario

    Returns:
        El hábito actualizado o None
    """
    # Verificar que el hábito pertenece a una rutina del usuario
    result = await db.execute(
        select(Habito)
        .join(Rutina)
        .where(
            Habito.id == habito_id,
            Rutina.usuario_id == usuario_id,
            Habito.is_deleted == False
        )
    )
    db_habito = result.scalar_one_or_none()

    if not db_habito:
        return None

    # Actualizar solo los campos no nulos
    update_data = habito_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_habito, field, value)

    db_habito.updated_at = datetime.now()
    await db.commit()
    await db.refresh(db_habito)
    return db_habito

async def delete_habito(
    db: AsyncSession,
    habito_id: int,
    usuario_id: int
) -> bool:
    """
    Realiza soft delete de un hábito.

    Args:
        db: Sesión de BD
        habito_id: ID del hábito
        usuario_id: ID del usuario propietario

    Returns:
        True si se eliminó, False si no existe
    """
    result = await db.execute(
        select(Habito)
        .join(Rutina)
        .where(
            Habito.id == habito_id,
            Rutina.usuario_id == usuario_id,
            Habito.is_deleted == False
        )
    )
    db_habito = result.scalar_one_or_none()

    if not db_habito:
        return False

    db_habito.is_deleted = True
    db_habito.deleted_at = datetime.now()
    await db.commit()
    return True

async def restore_habito(
    db: AsyncSession,
    habito_id: int,
    usuario_id: int
) -> Optional[Habito]:
    """
    Restaura un hábito eliminado.

    Args:
        db: Sesión de BD
        habito_id: ID del hábito
        usuario_id: ID del usuario propietario

    Returns:
        El hábito restaurado o None
    """
    result = await db.execute(
        select(Habito)
        .join(Rutina)
        .where(
            Habito.id == habito_id,
            Rutina.usuario_id == usuario_id,
            Habito.is_deleted == True
        )
    )
    db_habito = result.scalar_one_or_none()

    if not db_habito:
        return None

    db_habito.is_deleted = False
    db_habito.deleted_at = None
    await db.commit()
    await db.refresh(db_habito)
    return db_habito

# ============================================================================
# CATEGORÍAS
# ============================================================================

async def get_categorias(db: AsyncSession, include_subcategories: bool = False):
    """Obtiene categorías de rutinas."""
    if include_subcategories:
        result = await db.execute(select(CategoriaRutina).where(CategoriaRutina.estado == True))
    else:
        result = await db.execute(select(CategoriaRutina).where(CategoriaRutina.estado == True, CategoriaRutina.padre_id == None))
    categories = result.scalars().all()
    return categories

async def create_categoria(db: AsyncSession, categoria: CategoriaRutinaCreate):
    """
    Crea una categoría de rutina.
    Maneja errores de duplicados y validaciones de BD.
    """
    try:
        db_cat = CategoriaRutina(**categoria.model_dump())
        db.add(db_cat)
        await db.flush()
        await db.refresh(db_cat)
        await db.commit()
        return db_cat
    except Exception as e:
        await db.rollback()
        # Log o re-raise según sea necesario
        raise


async def create_subcategoria(db: AsyncSession, categoria_padre_id: int, categoria: CategoriaRutinaCreate):
    parent = await db.execute(
        select(CategoriaRutina).where(
            CategoriaRutina.id == categoria_padre_id,
            CategoriaRutina.estado == True,
        )
    )
    parent_row = parent.scalar_one_or_none()
    if not parent_row:
        return None

    payload = categoria.model_dump()
    payload["padre_id"] = categoria_padre_id

    db_subcat = CategoriaRutina(**payload)
    db.add(db_subcat)
    await db.commit()
    await db.refresh(db_subcat)
    return db_subcat


async def soft_delete_categoria(db: AsyncSession, categoria_id: int) -> bool:
    check = await db.execute(
        select(CategoriaRutina).where(
            CategoriaRutina.id == categoria_id,
            CategoriaRutina.estado == True,
        )
    )
    existing = check.scalar_one_or_none()
    if not existing:
        return False

    # Soft delete recursivo: desactiva categoría y todos sus descendientes.
    await db.execute(
        text(
            """
            WITH RECURSIVE categoria_tree AS (
                SELECT id
                FROM categorias_rutina
                WHERE id = :categoria_id AND estado = 1
                UNION ALL
                SELECT c.id
                FROM categorias_rutina c
                INNER JOIN categoria_tree t ON c.padre_id = t.id
                WHERE c.estado = 1
            )
            UPDATE categorias_rutina
            SET estado = 0
            WHERE id IN (SELECT id FROM categoria_tree)
            """
        ),
        {"categoria_id": categoria_id},
    )
    await db.commit()
    return True


async def soft_delete_subcategoria(db: AsyncSession, subcategoria_id: int) -> bool:
    sub = await db.execute(
        select(CategoriaRutina).where(
            CategoriaRutina.id == subcategoria_id,
            CategoriaRutina.estado == True,
            CategoriaRutina.padre_id.is_not(None),
        )
    )
    sub_row = sub.scalar_one_or_none()
    if not sub_row:
        return False

    return await soft_delete_categoria(db, subcategoria_id)

async def get_habitos_por_categoria(db: AsyncSession, categoria_id: int):
    result = await db.execute(select(Habito).where(Habito.categoria_id == categoria_id, Habito.is_deleted == False))
    return result.scalars().all()

async def get_habito_categorias(db: AsyncSession):
    result = await db.execute(select(HabitoCategoria).where(HabitoCategoria.estado == True))
    return result.scalars().all()

async def get_rutina(db: AsyncSession, rutina_id: int):
    result = await db.execute(
        select(Rutina)
        .options(selectinload(Rutina.habitos))
        .where(Rutina.id == rutina_id, Rutina.is_deleted == False)
    )
    return result.scalar_one_or_none()

async def clone_rutina_for_user(db: AsyncSession, rutina_id: int, user_id: int):
    """Clona una rutina con todos sus hábitos para un usuario."""
    # Obtener rutina original
    original_rutina = await get_rutina(db, rutina_id)
    if not original_rutina:
        return None
    
    # SQL INSERT para nueva rutina clonada
    insert_rutina_query = text("""
        INSERT INTO rutinas (usuario_id, nombre, momento_dia, es_publica, creada_por_ia, estado)
        VALUES (:usuario_id, :nombre, :momento_dia, :es_publica, :creada_por_ia, :estado)
    """)
    result_rutina = await db.execute(insert_rutina_query, {
        "usuario_id": user_id,
        "nombre": f"Copia de {original_rutina.nombre}",
        "momento_dia": original_rutina.momento_dia,
        "es_publica": False,
        "creada_por_ia": original_rutina.creada_por_ia,
        "estado": original_rutina.estado
    })
    new_rutina_id = result_rutina.lastrowid
    
    # Clonar habitos con SQL INSERT
    result_h = await db.execute(text("SELECT * FROM habitos WHERE rutina_id = :r_id AND is_deleted = FALSE"), {"r_id": rutina_id})
    h_rows = result_h.mappings().all()
    original_habitos = [Habito(**row) for row in h_rows]
    
    insert_habito_query = text("""
        INSERT INTO habitos (rutina_id, categoria_id, nombre, descripcion, tiempo_programado, tiempo_duracion_min, orden, estado)
        VALUES (:rutina_id, :categoria_id, :nombre, :descripcion, :tiempo_programado, :tiempo_duracion_min, :orden, :estado)
    """)
    
    for h in original_habitos:
        await db.execute(insert_habito_query, {
            "rutina_id": new_rutina_id,
            "categoria_id": h.categoria_id,
            "nombre": h.nombre,
            "descripcion": h.descripcion,
            "tiempo_programado": h.tiempo_programado,
            "tiempo_duracion_min": h.tiempo_duracion_min,
            "orden": h.orden,
            "estado": h.estado
        })
    
    await db.commit()
    
    # Obtener la nueva rutina con sus hábitos para retornar
    result_final = await db.execute(text("SELECT * FROM rutinas WHERE id = :id"), {"id": new_rutina_id})
    rutina_row = result_final.mappings().first()
    new_rutina = Rutina(**rutina_row)
    
    h_result = await db.execute(text("SELECT * FROM habitos WHERE rutina_id = :r_id AND is_deleted = FALSE"), {"r_id": new_rutina_id})
    h_rows = h_result.mappings().all()
    new_rutina.habitos = [Habito(**row) for row in h_rows]
    
    return new_rutina
