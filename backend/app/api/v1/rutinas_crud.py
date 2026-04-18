"""
Endpoints CRUD para Rutinas y Hábitos.
Implementa operaciones completas: Create, Read, Update, Delete y Restore.

Convenciones:
- GET /rutinas → Listar todas
- GET /rutinas/{id} → Obtener por ID
- GET /rutinas/usuario/me → Mis rutinas
- POST /rutinas → Crear nueva
- PUT /rutinas/{id} → Actualizar
- DELETE /rutinas/{id} → Eliminar (soft delete)
- POST /rutinas/{id}/restore → Restaurar eliminada

Similar para /habitos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models import Usuario, Rutina, Habito
from app.schemas.rutina import (
    RutinaCreate, RutinaUpdate, Rutina as RutinaSchema, RutinaDetail,
    HabitoCreate, HabitoUpdate, Habito as HabitoSchema, HabitoDetail,
    MomentoDiaEnum
)
from app.services import rutinas_service

router = APIRouter(
    prefix="/v1",
    tags=["rutinas-crud"],
    responses={
        400: {"description": "Datos inválidos o validación fallida"},
        401: {"description": "No autenticado - Token JWT requerido"},
        403: {"description": "No autorizado - Sin permisos para esta acción"},
        404: {"description": "Recurso no encontrado"},
        409: {"description": "Conflicto - Violación de integridad de datos"},
        500: {"description": "Error interno del servidor"}
    }
)

# ============================================================================
# RUTINAS - ENDPOINTS
# ============================================================================

@router.get("/rutinas", response_model=List[RutinaSchema], summary="Listar todas las rutinas")
async def list_all_routines(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene todas las rutinas públicas o del sistema.
    Excluye rutinas eliminadas.

    **Parámetros de paginación:**
    - skip: Cantidad de registros a saltar (default: 0)
    - limit: Cantidad máxima a retornar (default: 100, máximo: 1000)
    """
    return await rutinas_service.get_rutinas(db, skip=skip, limit=limit)

@router.get("/rutinas/usuario/me", response_model=List[RutinaSchema], summary="Mis rutinas")
async def get_my_routines(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene todas las rutinas del usuario autenticado.
    Retorna rutinas con sus hábitos asociados.
    """
    return await rutinas_service.get_rutinas_por_usuario(
        db, current_user.id, skip=skip, limit=limit
    )

@router.get("/rutinas/{rutina_id}", response_model=RutinaDetail, summary="Obtener rutina por ID")
async def get_routine_detail(
    rutina_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene los detalles completos de una rutina específica.
    Incluye todos sus hábitos asociados.

    Retorna 404 si la rutina no existe o fue eliminada.
    """
    rutina = await rutinas_service.get_rutina_por_id(db, rutina_id)
    if not rutina:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rutina no encontrada"
        )
    return rutina

@router.post("/rutinas", response_model=RutinaSchema, status_code=status.HTTP_201_CREATED, summary="Crear rutina")
async def create_routine(
    rutina_in: RutinaCreate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Crea una nueva rutina con sus hábitos asociados.

    **Parámetros principales:**
    - nombre: Nombre de la rutina (requerido)
    - momento_dia: mañana | tarde | noche | personalizado
    - es_publica: Si es visible públicamente
    - habitos: Lista de hábitos a incluir (opcional)

    **Ejemplo de cuerpo:**
    ```json
    {
        "nombre": "Rutina matutina",
        "momento_dia": "mañana",
        "es_publica": false,
        "habitos": [
            {
                "nombre": "Tomar agua",
                "tiempo_programado": "07:00",
                "tiempo_duracion_min": 5,
                "orden": 1
            }
        ]
    }
    ```
    """
    try:
        rutina = await rutinas_service.create_rutina(db, rutina_in, current_user.id)
        return rutina
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/rutinas/{rutina_id}", response_model=RutinaSchema, summary="Actualizar rutina")
async def update_routine(
    rutina_id: int,
    rutina_update: RutinaUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza una rutina existente.

    **Campos editables:**
    - nombre
    - momento_dia
    - es_publica
    - categoria_id

    Solo el propietario de la rutina puede actualizarla.
    """
    rutina = await rutinas_service.update_rutina(
        db, rutina_id, rutina_update, current_user.id
    )
    if not rutina:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rutina no encontrada o no tienes permisos para actualizarla"
        )
    return rutina

@router.delete("/rutinas/{rutina_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar rutina (Soft Delete)")
async def delete_routine(
    rutina_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina lógicamente una rutina (soft delete).

    - Marca la rutina como eliminada
    - Registra la fecha de eliminación
    - También marca sus hábitos como eliminados
    - Los datos se mantienen en la BD por auditoría

    Solo el propietario puede eliminar su rutina.
    """
    success = await rutinas_service.delete_rutina(db, rutina_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rutina no encontrada o no tienes permisos para eliminarla"
        )

@router.post("/rutinas/{rutina_id}/restore", response_model=RutinaSchema, summary="Restaurar rutina eliminada")
async def restore_routine(
    rutina_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Restaura una rutina que fue eliminada.

    - Desmarca como eliminada
    - Limpia la fecha de eliminación
    - Restaura todos sus hábitos asociados

    Solo el propietario puede restaurar su rutina.
    """
    rutina = await rutinas_service.restore_rutina(db, rutina_id, current_user.id)
    if not rutina:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rutina no encontrada o no fue eliminada"
        )
    return rutina

# ============================================================================
# HÁBITOS - ENDPOINTS
# ============================================================================

@router.get("/rutinas/{rutina_id}/habitos", response_model=List[HabitoSchema], summary="Listar hábitos de una rutina")
async def list_routine_habits(
    rutina_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene todos los hábitos activos de una rutina.
    Retornados en orden de ejecución.
    """
    # Verificar que la rutina existe
    rutina = await rutinas_service.get_rutina_por_id(db, rutina_id)
    if not rutina:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rutina no encontrada"
        )

    return await rutinas_service.get_habitos_por_rutina(db, rutina_id)

@router.get("/habitos/{habito_id}", response_model=HabitoDetail, summary="Obtener hábito por ID")
async def get_habit_detail(
    habito_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene los detalles de un hábito específico.
    """
    habito = await rutinas_service.get_habito_por_id(db, habito_id)
    if not habito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hábito no encontrado"
        )
    return habito

@router.post("/rutinas/{rutina_id}/habitos", response_model=HabitoSchema, status_code=status.HTTP_201_CREATED, summary="Crear hábito en rutina")
async def create_habit(
    rutina_id: int,
    habito_in: HabitoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Crea un nuevo hábito en una rutina específica.

    **Parámetros principales:**
    - nombre: Nombre del hábito (requerido)
    - tiempo_programado: Hora en formato HH:MM (opcional)
    - tiempo_duracion_min: Duración en minutos 1-480 (opcional)
    - orden: Posición en la secuencia de ejecución (default: 0)

    **Ejemplo de cuerpo:**
    ```json
    {
        "nombre": "Tomar agua",
        "descripcion": "500ml al despertar",
        "tiempo_programado": "07:00",
        "tiempo_duracion_min": 5,
        "orden": 1
    }
    ```

    Solo el propietario de la rutina puede crear hábitos.
    """
    # Verificar que la rutina existe y pertenece al usuario
    rutina = await rutinas_service.get_rutina_por_id(db, rutina_id)
    if not rutina or rutina.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rutina no encontrada o no tienes permisos"
        )

    try:
        habito = await rutinas_service.create_habito(db, habito_in, rutina_id)
        return habito
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/habitos/{habito_id}", response_model=HabitoSchema, summary="Actualizar hábito")
async def update_habit(
    habito_id: int,
    habito_update: HabitoUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza un hábito existente.

    **Campos editables:**
    - nombre
    - descripcion
    - tiempo_programado
    - tiempo_duracion_min
    - orden

    Solo el propietario de la rutina puede actualizar sus hábitos.
    """
    habito = await rutinas_service.update_habito(
        db, habito_id, habito_update, current_user.id
    )
    if not habito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hábito no encontrado o no tienes permisos para actualizarlo"
        )
    return habito

@router.delete("/habitos/{habito_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar hábito (Soft Delete)")
async def delete_habit(
    habito_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina lógicamente un hábito (soft delete).

    - Marca el hábito como eliminado
    - Registra la fecha de eliminación
    - Los datos se mantienen por auditoría

    Solo el propietario de la rutina puede eliminar hábitos.
    """
    success = await rutinas_service.delete_habito(db, habito_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hábito no encontrado o no tienes permisos para eliminarlo"
        )

@router.post("/habitos/{habito_id}/restore", response_model=HabitoSchema, summary="Restaurar hábito eliminado")
async def restore_habit(
    habito_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Restaura un hábito que fue eliminado.

    - Desmarca como eliminado
    - Limpia la fecha de eliminación

    Solo el propietario de la rutina puede restaurar hábitos.
    """
    habito = await rutinas_service.restore_habito(db, habito_id, current_user.id)
    if not habito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hábito no encontrado o no fue eliminado"
        )
    return habito

