from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import selectinload
from typing import List
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models import Rutina, Habito
from app.schemas import (
    Rutina as RutinaSchema,
    Comentario as ComentarioSchema,
    ComentarioContenidoCreate,
)
from app.models import Usuario
from app.services import comunidad_service

router = APIRouter(prefix="/comunidad", tags=["comunidad"])

@router.get("/comentarios/{rutina_id}", response_model=List[ComentarioSchema], summary="Obtener comentarios por rutina")
async def get_comments_by_routine(rutina_id: int, db: AsyncSession = Depends(get_db)):
    """
    Obtiene los comentarios asociados a una rutina a través de su publicación en la comunidad.
    Si la rutina no ha sido compartida en la comunidad, retorna una lista vacía.
    """
    return await comunidad_service.get_comentarios_por_rutina(db, rutina_id)

@router.post(
    "/comentarios/{rutina_id}",
    response_model=ComentarioSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Crear comentario en rutina",
    description="Crea un comentario para la rutina indicada. Si no existe publicación activa para la rutina, se crea automáticamente.",
)
async def create_comment_by_routine(
    rutina_id: int,
    comentario_in: ComentarioContenidoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    comentario = await comunidad_service.create_comentario_por_rutina(
        db=db,
        rutina_id=rutina_id,
        usuario_id=current_user.id,
        contenido=comentario_in.contenido,
    )
    if not comentario:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")
    return comentario

@router.delete(
    "/comentarios/{comentario_id}",
    summary="Eliminar comentario (Soft delete)",
    description="Elimina lógicamente un comentario propio marcando `deleted_at`.",
)
async def delete_comment(
    comentario_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    success = await comunidad_service.delete_comentario(db, comentario_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario no encontrado o no tienes permisos para eliminarlo",
        )
    return {"status": "success", "message": "Comentario eliminado correctamente"}

@router.get("/explorar", response_model=List[RutinaSchema], summary="Explorar rutinas públicas", description="Acceso público. Retorna todas las rutinas marcadas como `es_publica = 1`. Ideal para la vitrina de la aplicación.")
async def explorar_rutinas_publicas(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT * FROM rutinas 
        WHERE es_publica = 1 AND deleted_at IS NULL
    """)
    result = await db.execute(query)
    rows = result.mappings().all()
    rutinas = [Rutina(**row) for row in rows]
    
    for r in rutinas:
        h_query = text("SELECT * FROM habitos WHERE rutina_id = :r_id AND deleted_at IS NULL")
        h_result = await db.execute(h_query, {"r_id": r.id})
        h_rows = h_result.mappings().all()
        r.habitos = [Habito(**row) for row in h_rows]
        
    return rutinas
