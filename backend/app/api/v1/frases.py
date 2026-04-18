from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas.frase import FraseMotivacional, FraseMotivacionalCreate
from app.services import frases_service

router = APIRouter(prefix="/frases", tags=["frases"])

@router.get("/", response_model=List[FraseMotivacional], summary="Listar frases motivacionales")
async def list_frases(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Obtiene la lista de frases motivacionales.
    Se usa GET porque es una operación de lectura.
    """
    return await frases_service.get_frases(db, skip=skip, limit=limit)

@router.post("/", response_model=FraseMotivacional, status_code=status.HTTP_201_CREATED, summary="Crear frase motivacional")
async def create_frase(frase: FraseMotivacionalCreate, db: AsyncSession = Depends(get_db)):
    """
    Crea una nueva frase motivacional.
    Se usa POST porque se está creando un nuevo recurso.
    """
    nueva_frase = await frases_service.create_frase(db, frase)
    return nueva_frase


@router.delete("/{frase_id}", summary="Eliminar frase (Soft delete)")
async def delete_frase(frase_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await frases_service.delete_frase(db, frase_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Frase no encontrada")
    return {"status": "success", "message": "Frase eliminada correctamente"}

