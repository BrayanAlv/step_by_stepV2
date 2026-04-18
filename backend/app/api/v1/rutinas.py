from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import selectinload
from typing import List
from datetime import timedelta, time, date
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models import (
    Rutina, Habito, Usuario, SeguimientoHabito, 
    CategoriaRutina, RutinaRating, HistorialRutina, LikeRutina
)
from app.schemas import (
    RutinaCreate, RutinaUpdate, Rutina as RutinaSchema, SeguimientoCreate,
    Habito as HabitoSchema,
    CategoriaRutina as CategoriaSchema, CategoriaRutinaCreate as CategoriaSchemaCreate,
    HabitoCategoria as HabitoCategoriaSchema, HabitoCreate, HabitoUpdate,
    RutinaRatingCreate, HistorialRutinaCreate,
    HistorialRutina as HistorialSchema, UsuarioSimple,
    ChecklistResponse,
)
from app.services import rutinas_service, notification_service
from app.services.rutinas_service import clone_rutina_for_user
from app.services.gamificacion_service import update_mascota_status, add_exp_to_mascota

router = APIRouter(prefix="/rutinas", tags=["rutinas"])

def _convert_timedelta_to_time(value):
    """Convierte timedelta a time si es necesario."""
    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return time(hour=hours, minute=minutes, second=seconds)
    return value

def _normalize_habit_row(habit_dict: dict) -> dict:
    """Normaliza un diccionario de hábito convirtiendo timedelta a time."""
    if 'tiempo_programado' in habit_dict:
        habit_dict['tiempo_programado'] = _convert_timedelta_to_time(habit_dict['tiempo_programado'])
    return habit_dict

async def _ensure_saved_routines_table(db: AsyncSession):
    """Crea la tabla de rutinas guardadas si aún no existe."""
    await db.execute(text("""
        CREATE TABLE IF NOT EXISTS rutinas_guardadas (
            id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
            usuario_id BIGINT UNSIGNED NOT NULL,
            rutina_id BIGINT UNSIGNED NOT NULL,
            created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
            is_deleted TINYINT(1) DEFAULT 0,
            deleted_at TIMESTAMP NULL DEFAULT NULL,
            PRIMARY KEY (id),
            UNIQUE KEY uq_rutina_guardada_usuario_rutina (usuario_id, rutina_id),
            KEY idx_rutinas_guardadas_usuario_deleted (usuario_id, is_deleted),
            CONSTRAINT fk_rutinas_guardadas_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            CONSTRAINT fk_rutinas_guardadas_rutina FOREIGN KEY (rutina_id) REFERENCES rutinas(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """))

@router.get("/", response_model=List[RutinaSchema], summary="Listar todas las rutinas")
async def list_all_routines(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Obtiene todas las rutinas registradas en el sistema (que no han sido eliminadas).
    """
    return await rutinas_service.get_rutinas(db, skip=skip, limit=limit)

@router.get("/me", response_model=List[RutinaSchema], summary="Obtener mis rutinas", description="Retorna todas las rutinas del usuario autenticado, incluyendo sus hábitos asociados.")
async def get_my_routines(current_user: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Obtiene todas las rutinas del usuario autenticado.
    """
    return await rutinas_service.get_rutinas_por_usuario(db, current_user.id)

@router.post("/", response_model=RutinaSchema, summary="Crear rutina", description="Crea una nueva rutina con sus hábitos asociados para el usuario autenticado. Sujeto a restricciones de Trial.")
async def create_routine(rutina_in: RutinaCreate, current_user: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Nota: El middleware de Trial validará esto antes de entrar aquí
    
    # SQL INSERT para Rutina
    insert_rutina_query = text("""
        INSERT INTO rutinas (usuario_id, nombre, momento_dia, es_publica)
        VALUES (:usuario_id, :nombre, :momento_dia, :es_publica)
    """)
    result_rutina = await db.execute(insert_rutina_query, {
        "usuario_id": current_user.id,
        "nombre": rutina_in.nombre,
        "momento_dia": rutina_in.momento_dia,
        "es_publica": rutina_in.es_publica
    })
    rutina_id = result_rutina.lastrowid
    
    # SQL INSERT para Habitos
    insert_habito_query = text("""
        INSERT INTO habitos (rutina_id, nombre, descripcion, categoria_id, tiempo_programado, tiempo_duracion_min, orden)
        VALUES (:rutina_id, :nombre, :descripcion, :categoria_id, :tiempo_programado, :tiempo_duracion_min, :orden)
    """)
    
    for h in rutina_in.habitos:
        await db.execute(insert_habito_query, {
            "rutina_id": rutina_id,
            "nombre": h.nombre,
            "descripcion": h.descripcion,
            "categoria_id": h.categoria_id,
            "tiempo_programado": h.tiempo_programado,
            "tiempo_duracion_min": h.tiempo_duracion_min,
            "orden": h.orden
        })
    
    await db.commit()
    
    # Obtener la rutina creada con sus hábitos para la respuesta
    result_final = await db.execute(text("SELECT * FROM rutinas WHERE id = :id"), {"id": rutina_id})
    rutina_row = result_final.mappings().first()
    new_rutina = Rutina(**rutina_row)
    
    h_result = await db.execute(text("SELECT * FROM habitos WHERE rutina_id = :r_id AND deleted_at IS NULL"), {"r_id": rutina_id})
    h_rows = h_result.mappings().all()
    new_rutina.habitos = [Habito(**row) for row in h_rows]
    
    return new_rutina

@router.post("/copiar/{rutina_id}", response_model=RutinaSchema, summary="Copiar rutina pública", description="Clona una rutina pública y todos sus hábitos para el usuario autenticado. El clon se marca como privado por defecto.")
async def copy_routine(rutina_id: int, current_user: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    cloned = await clone_rutina_for_user(db, rutina_id, current_user.id)
    if not cloned:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")
    return cloned

@router.post("/habitos/check", summary="Marcar cumplimiento de hábito", description="Registra el cumplimiento de un hábito para una fecha específica. Otorga EXP a la mascota virtual si el estado es completado (1).")
async def check_habit(seguimiento_in: SeguimientoCreate, current_user: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Verificar que el hábito pertenezca al usuario
    query = text("""
        SELECT h.* FROM habitos h
        JOIN rutinas r ON h.rutina_id = r.id
        WHERE h.id = :habito_id AND r.usuario_id = :user_id
    """)
    habit_result = await db.execute(query, {"habito_id": seguimiento_in.habito_id, "user_id": current_user.id})
    habit_row = habit_result.mappings().first()
    if not habit_row:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    
    habit = Habito(**habit_row)
        
    # SQL INSERT para SeguimientoHabito
    insert_seguimiento_query = text("""
        INSERT INTO seguimiento_habitos (habito_id, fecha, estado, nota, estado_animo)
        VALUES (:habito_id, :fecha, :estado, :nota, :estado_animo)
    """)
    await db.execute(insert_seguimiento_query, {
        "habito_id": seguimiento_in.habito_id,
        "fecha": seguimiento_in.fecha,
        "estado": seguimiento_in.estado,
        "nota": seguimiento_in.nota,
        "estado_animo": seguimiento_in.estado_animo
    })
    
    if seguimiento_in.estado:
        await add_exp_to_mascota(db, current_user.id, 10) # 10 EXP por check
        await update_mascota_status(db, current_user.id)
    
    await db.commit()
    return {"status": "success"}

@router.get(
    "/checklist",
    response_model=ChecklistResponse,
    summary="Checklist de hábitos y rutinas completadas",
    description="Retorna, para el usuario autenticado, los hábitos marcados y las rutinas completadas. Permite filtrar por fecha con el parámetro `fecha` (YYYY-MM-DD).",
)
async def get_checklist(
    fecha: date | None = None,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    habit_query = text("""
        SELECT
            sh.id,
            sh.habito_id,
            h.nombre AS habito_nombre,
            r.id AS rutina_id,
            r.nombre AS rutina_nombre,
            sh.fecha,
            sh.estado,
            sh.nota,
            sh.estado_animo
        FROM seguimiento_habitos sh
        JOIN habitos h ON h.id = sh.habito_id
        JOIN rutinas r ON r.id = h.rutina_id
        WHERE r.usuario_id = :u_id
          AND sh.is_deleted = 0
          AND h.is_deleted = 0
          AND r.is_deleted = 0
          AND (:fecha IS NULL OR sh.fecha = :fecha)
        ORDER BY sh.fecha DESC, sh.id DESC
    """)
    habits_result = await db.execute(habit_query, {"u_id": current_user.id, "fecha": fecha})

    routine_query = text("""
        SELECT
            hr.id,
            hr.rutina_id,
            r.nombre AS rutina_nombre,
            hr.fecha_completada,
            hr.duracion_total_min
        FROM historial_rutinas hr
        JOIN rutinas r ON r.id = hr.rutina_id
        WHERE hr.usuario_id = :u_id
          AND r.is_deleted = 0
          AND (:fecha IS NULL OR DATE(hr.fecha_completada) = :fecha)
        ORDER BY hr.fecha_completada DESC, hr.id DESC
    """)
    routines_result = await db.execute(routine_query, {"u_id": current_user.id, "fecha": fecha})

    return {
        "habitos": habits_result.mappings().all(),
        "rutinas": routines_result.mappings().all(),
    }

# --- Nuevos Endpoints ---

@router.post("/categorias", response_model=CategoriaSchema, status_code=status.HTTP_201_CREATED, summary="Crear categoría de rutina")
async def create_category(categoria: CategoriaSchemaCreate, db: AsyncSession = Depends(get_db)):
    """
    Crea una nueva categoría para organizar las rutinas.
    """
    try:
        return await rutinas_service.create_categoria(db, categoria)
    except Exception as e:
        # Verificar si es error de duplicado
        error_str = str(e).lower()
        if "duplicate" in error_str or "unique" in error_str:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"La categoría '{categoria.nombre}' ya existe"
            )
        # Para otros errores
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear categoría: {str(e)}"
        )


@router.post(
    "/categorias/{categoria_id}/subcategorias",
    response_model=CategoriaSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Crear subcategoría",
)
async def create_subcategory(categoria_id: int, categoria: CategoriaSchemaCreate, db: AsyncSession = Depends(get_db)):
    subcategoria = await rutinas_service.create_subcategoria(db, categoria_id, categoria)
    if not subcategoria:
        raise HTTPException(status_code=404, detail="Categoría padre no encontrada")
    return subcategoria

@router.get("/categorias", response_model=List[CategoriaSchema], summary="Listar categorías de rutinas")
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM categorias_rutina WHERE estado = 1 AND padre_id IS NULL"))
    rows = result.mappings().all()
    categories = []
    for row in rows:
        cat = CategoriaSchema.model_validate(row)
        # Buscar subcategorías
        sub_result = await db.execute(text("SELECT * FROM categorias_rutina WHERE padre_id = :p_id AND estado = 1"), {"p_id": cat.id})
        cat.subcategorias = [CategoriaSchema.model_validate(s_row) for s_row in sub_result.mappings().all()]
        categories.append(cat)
    return categories


@router.delete("/categorias/{categoria_id}", summary="Eliminar categoría (Soft delete recursivo)")
async def delete_category(categoria_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await rutinas_service.soft_delete_categoria(db, categoria_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return {"status": "success", "message": "Categoría eliminada correctamente"}


@router.delete("/categorias/subcategorias/{subcategoria_id}", summary="Eliminar subcategoría (Soft delete recursivo)")
async def delete_subcategory(subcategoria_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await rutinas_service.soft_delete_subcategoria(db, subcategoria_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Subcategoría no encontrada")
    return {"status": "success", "message": "Subcategoría eliminada correctamente"}

@router.post("/habitos/{rutina_id}", response_model=HabitoSchema, status_code=status.HTTP_201_CREATED, summary="Crear un hábito en una rutina")
async def create_habit(rutina_id: int, habito: HabitoCreate, current_user: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Crea un nuevo hábito asociado a una rutina específica.
    """
    new_habit = await rutinas_service.create_habito(db, habito, rutina_id)
    
    # Programar recordatorio si tiene tiempo_programado
    if new_habit.tiempo_programado:
        await notification_service.schedule_habit_reminder(
            user_id=current_user.id,
            title="Recordatorio",
            body=f"Es hora de tu hábito: {new_habit.nombre}",
            scheduled_time=new_habit.tiempo_programado
        )
    
    return new_habit

@router.post(
    "/categorias/{categoria_id}/habitos/{rutina_id}",
    response_model=HabitoSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Crear hábito en categoría",
    description="Crea un hábito dentro de una rutina del usuario y fuerza su `categoria_id` con la categoría indicada en la URL.",
)
async def create_habit_in_category(
    categoria_id: int,
    rutina_id: int,
    habito: HabitoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rutina = await rutinas_service.get_rutina_por_id(db, rutina_id)
    if not rutina or rutina.usuario_id != current_user.id:
        raise HTTPException(status_code=404, detail="Rutina no encontrada o no tienes permisos")

    categoria_result = await db.execute(
        text("SELECT id FROM habitos_categoria WHERE id = :c_id AND estado = 1"),
        {"c_id": categoria_id},
    )
    if not categoria_result.first():
        raise HTTPException(status_code=404, detail="Categoría de hábito no encontrada")

    habito_categoria = habito.model_copy(update={"categoria_id": categoria_id})
    return await rutinas_service.create_habito(db, habito_categoria, rutina_id)

@router.get("/habitos/por-categoria/{categoria_id}", response_model=List[HabitoSchema], summary="Listar hábitos por categoría")
async def list_habits_by_category(categoria_id: int, db: AsyncSession = Depends(get_db)):
    """
    Lista todos los hábitos asociados a una categoría específica.
    """
    return await rutinas_service.get_habitos_por_categoria(db, categoria_id)

@router.get("/habitos/categorias", response_model=List[HabitoCategoriaSchema], summary="Listar categorías de hábitos")
async def get_habit_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM habitos_categoria WHERE estado = 1"))
    return result.mappings().all()

@router.post("/like/{rutina_id}", summary="Dar like a una rutina")
async def like_routine(rutina_id: int, current_user: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Verificar si ya existe el like
    check_query = text("SELECT id FROM likes_rutina WHERE rutina_id = :r_id AND usuario_id = :u_id")
    result = await db.execute(check_query, {"r_id": rutina_id, "u_id": current_user.id})
    if result.first():
        # Si existe, lo quitamos (Toggle)
        await db.execute(text("DELETE FROM likes_rutina WHERE rutina_id = :r_id AND usuario_id = :u_id"), {"r_id": rutina_id, "u_id": current_user.id})
        await db.commit()
        return {"status": "unliked"}
    
    await db.execute(text("INSERT INTO likes_rutina (rutina_id, usuario_id) VALUES (:r_id, :u_id)"), {"r_id": rutina_id, "u_id": current_user.id})
    
    # Notificación de nuevo like
    rutina_res = await db.execute(text("SELECT usuario_id FROM rutinas WHERE id = :id"), {"id": rutina_id})
    rutina_row = rutina_res.mappings().first()
    if rutina_row and rutina_row["usuario_id"] != current_user.id:
        await notification_service.send_push_notification(
            db,
            user_id=rutina_row["usuario_id"],
            title="Nuevo like",
            body=f"A {current_user.nombre} le gustó tu rutina",
            tipo="social"
        )

    await db.commit()
    return {"status": "liked"}

@router.post("/rate/{rutina_id}", summary="Calificar una rutina")
async def rate_routine(rutina_id: int, rating_in: RutinaRatingCreate, current_user: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Upsert rating
    check_query = text("SELECT id FROM rutina_ratings WHERE rutina_id = :r_id AND usuario_id = :u_id")
    result = await db.execute(check_query, {"r_id": rutina_id, "u_id": current_user.id})
    
    if result.first():
        update_query = text("""
            UPDATE rutina_ratings SET puntuacion = :p, comentario = :c, fecha = CURRENT_TIMESTAMP
            WHERE rutina_id = :r_id AND usuario_id = :u_id
        """)
        await db.execute(update_query, {"p": rating_in.puntuacion, "c": rating_in.comentario, "r_id": rutina_id, "u_id": current_user.id})
    else:
        insert_query = text("""
            INSERT INTO rutina_ratings (rutina_id, usuario_id, puntuacion, comentario)
            VALUES (:r_id, :u_id, :p, :c)
        """)
        await db.execute(insert_query, {"r_id": rutina_id, "u_id": current_user.id, "p": rating_in.puntuacion, "c": rating_in.comentario})
    
    await db.commit()
    return {"status": "success", "message": "Calificación registrada"}

@router.post("/completar", summary="Registrar rutina completada (Historial)")
async def complete_routine(historial_in: HistorialRutinaCreate, current_user: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    insert_query = text("""
        INSERT INTO historial_rutinas (usuario_id, rutina_id, duracion_total_min)
        VALUES (:u_id, :r_id, :d)
    """)
    await db.execute(insert_query, {"u_id": current_user.id, "r_id": historial_in.rutina_id, "d": historial_in.duracion_total_min})
    
    # Podríamos dar más EXP por completar rutina completa
    await add_exp_to_mascota(db, current_user.id, 50)
    await update_mascota_status(db, current_user.id)
    
    # Notificación de rutina completada
    await notification_service.send_push_notification(
        db,
        user_id=current_user.id,
        title="Rutina completada",
        body="¡Excelente trabajo! Ganaste 50 EXP para tu mascota",
        tipo="gamificacion"
    )
    
    await db.commit()
    return {"status": "success", "message": "Historial de rutina registrado"}

@router.post(
    "/guardadas/{rutina_id}",
    summary="Guardar o quitar rutina guardada",
    description="Toggle de guardado: si la rutina no está guardada la guarda; si ya está guardada la desmarca con soft delete.",
)
async def toggle_save_routine(rutina_id: int, current_user: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _ensure_saved_routines_table(db)

    rutina_check = await db.execute(
        text("SELECT id FROM rutinas WHERE id = :r_id AND is_deleted = 0"),
        {"r_id": rutina_id},
    )
    if not rutina_check.first():
        raise HTTPException(status_code=404, detail="Rutina no encontrada")

    existing = await db.execute(
        text("""
            SELECT id, is_deleted
            FROM rutinas_guardadas
            WHERE usuario_id = :u_id AND rutina_id = :r_id
        """),
        {"u_id": current_user.id, "r_id": rutina_id},
    )
    row = existing.mappings().first()

    if not row:
        await db.execute(
            text("""
                INSERT INTO rutinas_guardadas (usuario_id, rutina_id, is_deleted, deleted_at)
                VALUES (:u_id, :r_id, 0, NULL)
            """),
            {"u_id": current_user.id, "r_id": rutina_id},
        )
        await db.commit()
        return {"status": "saved"}

    if row["is_deleted"] == 1:
        await db.execute(
            text("""
                UPDATE rutinas_guardadas
                SET is_deleted = 0, deleted_at = NULL
                WHERE id = :id
            """),
            {"id": row["id"]},
        )
        await db.commit()
        return {"status": "saved"}

    await db.execute(
        text("""
            UPDATE rutinas_guardadas
            SET is_deleted = 1, deleted_at = CURRENT_TIMESTAMP
            WHERE id = :id
        """),
        {"id": row["id"]},
    )
    await db.commit()
    return {"status": "unsaved"}

@router.get(
    "/guardadas",
    response_model=List[RutinaSchema],
    summary="Listar rutinas guardadas",
    description="Lista las rutinas guardadas activas del usuario autenticado (excluye guardados eliminados lógicamente).",
)
async def get_saved_routines(current_user: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _ensure_saved_routines_table(db)

    result = await db.execute(text("""
        SELECT r.*
        FROM rutinas_guardadas rg
        JOIN rutinas r ON r.id = rg.rutina_id
        WHERE rg.usuario_id = :u_id
          AND rg.is_deleted = 0
          AND r.is_deleted = 0
        ORDER BY rg.created_at DESC
    """), {"u_id": current_user.id})
    rows = result.mappings().all()
    rutinas = [Rutina(**row) for row in rows]

    for r in rutinas:
        h_result = await db.execute(
            text("SELECT * FROM habitos WHERE rutina_id = :r_id AND is_deleted = 0"),
            {"r_id": r.id},
        )
        r.habitos = [Habito(**_normalize_habit_row(dict(row))) for row in h_result.mappings().all()]

    return rutinas

@router.delete("/{rutina_id}", summary="Eliminar rutina (Soft delete)")
async def delete_routine(rutina_id: int, current_user: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Realiza un soft delete de una rutina. Solo el dueño de la rutina puede eliminarla.
    """
    success = await rutinas_service.delete_rutina(db, rutina_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Rutina no encontrada o no tienes permisos para eliminarla")
    return {"status": "success", "message": "Rutina eliminada correctamente"}

@router.delete(
    "/habitos/{habito_id}",
    summary="Eliminar hábito (Soft delete)",
    description="Realiza soft delete del hábito validando propiedad de la rutina por parte del usuario autenticado.",
)
async def delete_habit(habito_id: int, current_user: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    success = await rutinas_service.delete_habito(db, habito_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Hábito no encontrado o no tienes permisos para eliminarlo")
    return {"status": "success", "message": "Hábito eliminado correctamente"}

@router.get("/historial", response_model=List[HistorialSchema], summary="Obtener mi historial de rutinas")
async def get_my_history(current_user: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM historial_rutinas WHERE usuario_id = :u_id ORDER BY fecha_completada DESC")
    result = await db.execute(query, {"u_id": current_user.id})
    return result.mappings().all()

@router.get("/likes/{rutina_id}", response_model=List[UsuarioSimple], summary="Usuarios que dieron like a esta rutina")
async def get_routine_likes(rutina_id: int, db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT u.id, u.nombre, u.foto_perfil FROM usuarios u
        JOIN likes_rutina l ON u.id = l.usuario_id
        WHERE l.rutina_id = :r_id
    """)
    result = await db.execute(query, {"r_id": rutina_id})
    return result.mappings().all()

@router.get("/perfil/{usuario_id}", summary="Obtener perfil público de usuario")
async def get_user_profile(usuario_id: int, db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT u.id, u.nombre, u.apellido_paterno, u.foto_perfil, 
               (SELECT COUNT(*) FROM seguidores WHERE seguido_id = u.id) as seguidores_count,
               (SELECT COUNT(*) FROM seguidores WHERE seguidor_id = u.id) as siguiendo_count
        FROM usuarios u
        WHERE u.id = :u_id
    """)
    result = await db.execute(query, {"u_id": usuario_id})
    user = result.mappings().first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Obtener rutinas públicas
    r_query = text("SELECT id, nombre, momento_dia FROM rutinas WHERE usuario_id = :u_id AND es_publica = 1 AND deleted_at IS NULL")
    r_result = await db.execute(r_query, {"u_id": usuario_id})
    
    return {
        "usuario": user,
        "rutinas_publicas": r_result.mappings().all()
    }

@router.put("/{rutina_id}", response_model=RutinaSchema, status_code=status.HTTP_200_OK,
    summary="🔄 Editar rutina",
    description="Actualiza una rutina existente del usuario autenticado.")
async def update_routine(
    rutina_id: int,
    rutina_in: RutinaUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    # 🔄 Editar Rutina

    Actualiza una rutina existente. Solo el propietario puede editarla.

    ## Campos editables:
    - **nombre**: string (1-100 caracteres)
    - **momento_dia**: "mañana" | "tarde" | "noche" | "personalizado"
    - **es_publica**: true/false
    - **categoria_id**: ID de categoría (opcional)

    ## Ejemplo de request:
    ```json
    {
      "nombre": "Rutina Matutina Mejorada",
      "momento_dia": "mañana",
      "es_publica": true
    }
    ```

    ## Campos NO editables desde aquí:
    - `id` (immutable)
    - `usuario_id` (no se puede cambiar propietario)
    - `habitos` (usar endpoints de hábitos)
    - `is_deleted`, `deleted_at` (solo con DELETE/restore)

    ## Respuesta (200 OK):
    Devuelve la rutina completamente actualizada con todos sus hábitos.
    """
    # Verify ownership and get routine with relationships
    query = text("""
        SELECT * FROM rutinas 
        WHERE id = :r_id AND usuario_id = :u_id AND is_deleted = 0
    """)
    result = await db.execute(query, {"r_id": rutina_id, "u_id": current_user.id})
    rutina_row = result.mappings().first()

    if not rutina_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rutina no encontrada o no tienes permisos para editarla",
        )

    # Update routine fields
    update_query = text("""
        UPDATE rutinas 
        SET nombre = :nombre, 
            momento_dia = :momento_dia, 
            es_publica = :es_publica,
            categoria_id = :categoria_id,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :r_id AND usuario_id = :u_id
    """)

    await db.execute(update_query, {
        "nombre": rutina_in.nombre,
        "momento_dia": rutina_in.momento_dia,
        "es_publica": rutina_in.es_publica,
        "categoria_id": rutina_in.categoria_id,
        "r_id": rutina_id,
        "u_id": current_user.id
    })

    await db.commit()

    # Fetch updated routine with habits
    final_query = text("""
        SELECT * FROM rutinas 
        WHERE id = :r_id
    """)
    final_result = await db.execute(final_query, {"r_id": rutina_id})
    updated_row = final_result.mappings().first()

    h_query = text("""
        SELECT * FROM habitos 
        WHERE rutina_id = :r_id AND is_deleted = 0
    """)
    h_result = await db.execute(h_query, {"r_id": rutina_id})
    habitos_rows = h_result.mappings().all()

    # Build response object with normalized data
    rutina_dict = dict(updated_row)
    rutina_dict['habitos'] = [_normalize_habit_row(dict(row)) for row in habitos_rows]

    return RutinaSchema(**rutina_dict)


@router.put("/habitos/{habito_id}", response_model=HabitoSchema, status_code=status.HTTP_200_OK,
    summary="🔄 Editar hábito",
    description="Actualiza un hábito existente del usuario autenticado.")
async def update_habit(
    habito_id: int,
    habito_in: HabitoUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    # 🔄 Editar Hábito

    Actualiza un hábito existente. Solo el propietario de la rutina puede editarlo.

    ## Campos editables:
    - **nombre**: string (1-100 caracteres)
    - **descripcion**: string (opcional)
    - **tiempo_programado**: "HH:MM" (ejemplo: "07:00")
    - **tiempo_duracion_min**: integer (1-480 minutos)
    - **orden**: integer (posición en la rutina)

    ## Ejemplo de request:
    ```json
    {
      "nombre": "Meditación profunda",
      "tiempo_programado": "06:30",
      "tiempo_duracion_min": 20,
      "orden": 1
    }
    ```

    ## Campos NO editables:
    - `id` (immutable)
    - `rutina_id` (no se puede cambiar de rutina)
    - `is_deleted`, `deleted_at` (solo con DELETE/restore)

    ## Respuesta (200 OK):
    Devuelve el hábito completamente actualizado.
    """
    habito = await rutinas_service.update_habito(
        db=db,
        habito_id=habito_id,
        habito_update=habito_in,
        usuario_id=current_user.id,
    )
    if not habito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hábito no encontrado o no tienes permisos para editarlo",
        )
    return habito
