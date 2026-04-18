from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.frase import FraseMotivacional
from app.schemas.frase import FraseMotivacionalCreate
from datetime import datetime

async def get_frases(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(FraseMotivacional)
        .where(FraseMotivacional.is_deleted == False)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def create_frase(db: AsyncSession, frase: FraseMotivacionalCreate):
    db_frase = FraseMotivacional(**frase.model_dump())
    db.add(db_frase)
    await db.commit()
    await db.refresh(db_frase)
    return db_frase


async def delete_frase(db: AsyncSession, frase_id: int) -> bool:
    result = await db.execute(
        select(FraseMotivacional).where(
            FraseMotivacional.id == frase_id,
            FraseMotivacional.is_deleted == False,
        )
    )
    db_frase = result.scalar_one_or_none()
    if not db_frase:
        return False

    db_frase.is_deleted = True
    db_frase.deleted_at = datetime.now()
    await db.commit()
    return True

