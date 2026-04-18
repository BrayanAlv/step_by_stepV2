from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from jose import JWTError, jwt
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.models import Usuario, PerfilUsuario, MascotaVirtual, Plan
from app.schemas import UserRegister, Token, TokenData

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        usuario_id: int = payload.get("sub")
        if usuario_id is None:
            raise credentials_exception
        token_data = TokenData(usuario_id=usuario_id)
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(text("SELECT * FROM usuarios WHERE id = :id"), {"id": token_data.usuario_id})
    row = result.mappings().first()
    if row is None:
        raise credentials_exception
    user = Usuario(**row)
    return user

@router.post("/register", response_model=Token, summary="Registrar nuevo usuario", description="Crea un nuevo usuario, su perfil y su mascota virtual. Se le asigna el plan 'Free' con 14 días de trial automáticamente.")
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    # Verificar si el usuario ya existe
    result = await db.execute(text("SELECT id FROM usuarios WHERE correo_electronico = :email"), {"email": user_in.correo_electronico})
    if result.mappings().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Obtener plan 'Free' por defecto (asumiendo ID 1 o buscando por nombre)
    result_plan = await db.execute(text("SELECT id FROM planes WHERE nombre = 'Free'"))
    plan_row = result_plan.mappings().first()
    plan_free_id = plan_row["id"] if plan_row else None

    # Crear usuario
    hashed_password = get_password_hash(user_in.contrasena)
    
    # SQL INSERT para Usuario
    insert_user_query = text("""
        INSERT INTO usuarios (nombre, apellido_paterno, apellido_materno, correo_electronico, contrasena, telefono, plan_id)
        VALUES (:nombre, :apellido_paterno, :apellido_materno, :correo_electronico, :contrasena, :telefono, :plan_id)
    """)
    result_user = await db.execute(insert_user_query, {
        "nombre": user_in.nombre,
        "apellido_paterno": user_in.apellido_paterno,
        "apellido_materno": user_in.apellido_materno,
        "correo_electronico": user_in.correo_electronico,
        "contrasena": hashed_password,
        "telefono": user_in.telefono,
        "plan_id": plan_free_id
    })
    user_id = result_user.lastrowid
    
    # Crear Perfil y Mascota con SQL INSERT
    await db.execute(text("INSERT INTO perfil_usuario (usuario_id) VALUES (:user_id)"), {"user_id": user_id})
    await db.execute(text("INSERT INTO mascota_virtual (usuario_id) VALUES (:user_id)"), {"user_id": user_id})
    
    await db.commit()
    
    # Obtener el usuario creado para el token
    result_final = await db.execute(text("SELECT * FROM usuarios WHERE id = :id"), {"id": user_id})
    row = result_final.mappings().first()
    new_user = Usuario(**row)
    
    access_token = create_access_token(data={"sub": str(new_user.id), "plan_id": new_user.plan_id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token, summary="Iniciar sesión", description="Autentica al usuario con correo y contraseña para obtener un token JWT. El token incluye `usuario_id` y `plan_id`.")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM usuarios WHERE correo_electronico = :email"), {"email": form_data.username})
    row = result.mappings().first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = Usuario(**row)
    if not verify_password(form_data.password, user.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id), "plan_id": user.plan_id})
    return {"access_token": access_token, "token_type": "bearer"}
