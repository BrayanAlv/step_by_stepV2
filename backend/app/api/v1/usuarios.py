from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models import Usuario, Seguidor, Plan
from app.schemas import Seguidor as SeguidorSchema, SeguidorCreate, UsuarioSimple, UsuarioConSuscripcion, SuscripcionDetalle, PlanUpdate
from app.services import usuarios_service, notification_service
from datetime import datetime, timedelta

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.get("/", response_model=List[UsuarioConSuscripcion], summary="Listar todos los usuarios")
async def list_users(
    skip: int = Query(0, ge=0, description="Cantidad de registros a omitir"),
    limit: int = Query(100, ge=1, le=500, description="Cantidad máxima de usuarios a retornar"),
    es_premium: Optional[bool] = Query(None, description="Filtra usuarios premium (`true`) o gratuitos (`false`)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene la lista de todos los usuarios registrados.
    Puede filtrar por es_premium=true para usuarios premium o es_premium=false para freemium.
    """
    return await usuarios_service.get_usuarios(db, skip=skip, limit=limit, es_premium=es_premium)

@router.get("/premium/all", response_model=List[UsuarioConSuscripcion], summary="Obtener todos los usuarios premium pagados")
async def get_premium_users(
    skip: int = Query(0, ge=0, description="Cantidad de registros a omitir"),
    limit: int = Query(100, ge=1, le=500, description="Cantidad máxima de usuarios a retornar"),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene lista de usuarios con suscripción activa pagada a través de Stripe.
    """
    return await usuarios_service.get_usuarios(db, skip=skip, limit=limit, es_premium=True)

@router.get("/freemium/all", response_model=List[UsuarioConSuscripcion], summary="Obtener todos los usuarios freemium")
async def get_freemium_users(
    skip: int = Query(0, ge=0, description="Cantidad de registros a omitir"),
    limit: int = Query(100, ge=1, le=500, description="Cantidad máxima de usuarios a retornar"),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene lista de usuarios sin suscripción activa (freemium).
    """
    return await usuarios_service.get_usuarios(db, skip=skip, limit=limit, es_premium=False)

@router.get("/seguidores", response_model=List[UsuarioSimple], summary="Listar mis seguidores")
async def get_my_followers(current_user: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT u.id, u.nombre, u.foto_perfil FROM usuarios u
        JOIN seguidores s ON u.id = s.seguidor_id
        WHERE s.seguido_id = :u_id
    """)
    result = await db.execute(query, {"u_id": current_user.id})
    return result.mappings().all()

@router.get("/siguiendo", response_model=List[UsuarioSimple], summary="Listar personas que sigo")
async def get_following(current_user: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT u.id, u.nombre, u.foto_perfil FROM usuarios u
        JOIN seguidores s ON u.id = s.seguido_id
        WHERE s.seguidor_id = :u_id
    """)
    result = await db.execute(query, {"u_id": current_user.id})
    return result.mappings().all()

@router.get("/suscripcion", response_model=SuscripcionDetalle, summary="Detalles de mi suscripción")
async def get_my_subscription(current_user: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT p.id, p.nombre, p.duracion_trial_dias
        FROM planes p
        WHERE p.id = :plan_id
    """)
    result = await db.execute(query, {"plan_id": current_user.plan_id})
    plan = result.mappings().first()
    
    plan_nombre = plan["nombre"] if plan else "Sin Plan"
    dias_restantes = 0
    if current_user.fecha_fin_trial:
        delta = current_user.fecha_fin_trial - datetime.now()
        dias_restantes = max(0, delta.days)
    
    return {
        "plan_id": current_user.plan_id,
        "plan_nombre": plan_nombre,
        "fecha_fin_trial": current_user.fecha_fin_trial,
        "dias_restantes": dias_restantes,
        "es_premium": plan_nombre not in ["Gratuito", "Free", "Sin Plan"]
    }

@router.get("/{usuario_id}", response_model=UsuarioSimple, summary="Obtener usuario por ID para perfil")
async def get_user_by_id(usuario_id: int, db: AsyncSession = Depends(get_db)):
    """
    Obtiene la información de un usuario específico por su ID.
    """
    user = await usuarios_service.get_usuario_by_id(db, usuario_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.post("/seguir/{seguido_id}", summary="Seguir a un usuario")
async def follow_user(seguido_id: int, current_user: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if seguido_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes seguirte a ti mismo")
    
    check_user = await db.execute(text("SELECT id FROM usuarios WHERE id = :id"), {"id": seguido_id})
    if not check_user.first():
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    check_query = text("SELECT id FROM seguidores WHERE seguidor_id = :s_id AND seguido_id = :f_id")
    result = await db.execute(check_query, {"s_id": current_user.id, "f_id": seguido_id})
    
    if result.first():
        # Toggle: Dejar de seguir
        await db.execute(text("DELETE FROM seguidores WHERE seguidor_id = :s_id AND seguido_id = :f_id"), {"s_id": current_user.id, "f_id": seguido_id})
        await db.commit()
        return {"status": "unfollowed"}
    
    await db.execute(text("INSERT INTO seguidores (seguidor_id, seguido_id) VALUES (:s_id, :f_id)"), {"s_id": current_user.id, "f_id": seguido_id})
    
    # Notificación de nuevo seguidor
    await notification_service.send_push_notification(
        db, 
        user_id=seguido_id, 
        title="Nuevo seguidor", 
        body=f"{current_user.nombre} comenzó a seguirte",
        tipo="social"
    )
    
    await db.commit()
    return {"status": "followed"}

@router.post("/suscripcion/iniciar", summary="Iniciar suscripción (Asignar plan)")
async def start_subscription(plan_in: PlanUpdate, current_user: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Verificar que el plan existe
    plan_query = text("SELECT * FROM planes WHERE id = :p_id")
    plan_res = await db.execute(plan_query, {"p_id": plan_in.plan_id})
    plan = plan_res.mappings().first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    fecha_fin_trial = None
    if plan["nombre"] in ["Gratuito", "Free"]:
        fecha_fin_trial = datetime.now() + timedelta(days=plan["duracion_trial_dias"])
    
    update_query = text("""
        UPDATE usuarios 
        SET plan_id = :p_id, fecha_fin_trial = :f_trial, estado = 'activo'
        WHERE id = :u_id
    """)
    await db.execute(update_query, {
        "p_id": plan_in.plan_id,
        "f_trial": fecha_fin_trial,
        "u_id": current_user.id
    })
    await db.commit()
    
    return {"status": "success", "message": f"Suscripción al plan {plan['nombre']} iniciada"}
