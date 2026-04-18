"""
TESTS UNITARIOS - CRUD RUTINAS Y HÁBITOS

Ejemplos de pruebas para verificar la correcta implementación.

Ejecutar con:
    pytest app/tests/test_rutinas_crud.py -v
    pytest app/tests/test_rutinas_crud.py::test_create_rutina -v
"""
import pytest
from datetime import datetime, time
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Rutina, Habito, Usuario
from app.schemas.rutina import RutinaCreate, HabitoCreate, RutinaUpdate, HabitoUpdate
from app.services import rutinas_service


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
async def usuario_test(db: AsyncSession):
    """Crea un usuario de prueba."""
    from sqlalchemy import insert
    # Implement usuario creation
    usuario = Usuario(
        id=999,
        nombre="Test User",
        correo_electronico="test@example.com",
        contrasena="hashed_password",
        plan_id=1
    )
    db.add(usuario)
    await db.commit()
    return usuario


# ============================================================================
# TESTS - CREAR RUTINA
# ============================================================================

@pytest.mark.asyncio
async def test_create_rutina_simple(db: AsyncSession, usuario_test):
    """Test: Crear una rutina sin hábitos."""
    rutina_data = RutinaCreate(
        nombre="Rutina Test",
        momento_dia="mañana",
        es_publica=False,
        habitos=[]
    )

    rutina = await rutinas_service.create_rutina(db, rutina_data, usuario_test.id)

    assert rutina.id is not None
    assert rutina.nombre == "Rutina Test"
    assert rutina.momento_dia == "mañana"
    assert rutina.usuario_id == usuario_test.id
    assert rutina.is_deleted == False
    assert rutina.deleted_at is None
    assert len(rutina.habitos) == 0


@pytest.mark.asyncio
async def test_create_rutina_con_habitos(db: AsyncSession, usuario_test):
    """Test: Crear una rutina con hábitos asociados."""
    habito1 = HabitoCreate(
        nombre="Meditación",
        tiempo_programado=time(6, 0, 0),
        tiempo_duracion_min=10,
        orden=1
    )
    habito2 = HabitoCreate(
        nombre="Ejercicio",
        tiempo_programado=time(6, 10, 0),
        tiempo_duracion_min=30,
        orden=2
    )

    rutina_data = RutinaCreate(
        nombre="Rutina Completa",
        momento_dia="mañana",
        es_publica=False,
        habitos=[habito1, habito2]
    )

    rutina = await rutinas_service.create_rutina(db, rutina_data, usuario_test.id)

    assert rutina.id is not None
    assert len(rutina.habitos) == 2
    assert rutina.habitos[0].nombre == "Meditación"
    assert rutina.habitos[1].nombre == "Ejercicio"
    assert rutina.habitos[0].orden == 1
    assert rutina.habitos[1].orden == 2


@pytest.mark.asyncio
async def test_create_rutina_validacion_duracion(db: AsyncSession, usuario_test):
    """Test: Validación de duración de hábito (1-480 minutos)."""
    habito_invalido = HabitoCreate(
        nombre="Hábito Inválido",
        tiempo_duracion_min=500,  # Mayor a 480
        orden=1
    )

    rutina_data = RutinaCreate(
        nombre="Rutina Test",
        momento_dia="mañana",
        habitos=[habito_invalido]
    )

    with pytest.raises(ValueError):
        await rutinas_service.create_rutina(db, rutina_data, usuario_test.id)


# ============================================================================
# TESTS - OBTENER RUTINA
# ============================================================================

@pytest.mark.asyncio
async def test_get_rutina_por_id(db: AsyncSession, usuario_test):
    """Test: Obtener una rutina por ID."""
    # Crear rutina
    rutina_data = RutinaCreate(
        nombre="Rutina Para Obtener",
        momento_dia="tarde",
        es_publica=True,
        habitos=[]
    )
    rutina_creada = await rutinas_service.create_rutina(db, rutina_data, usuario_test.id)

    # Obtener rutina
    rutina = await rutinas_service.get_rutina_por_id(db, rutina_creada.id)

    assert rutina is not None
    assert rutina.id == rutina_creada.id
    assert rutina.nombre == "Rutina Para Obtener"
    assert rutina.es_publica == True


@pytest.mark.asyncio
async def test_get_rutina_no_existe(db: AsyncSession):
    """Test: Obtener una rutina que no existe retorna None."""
    rutina = await rutinas_service.get_rutina_por_id(db, 99999)

    assert rutina is None


@pytest.mark.asyncio
async def test_get_rutina_eliminada(db: AsyncSession, usuario_test):
    """Test: Una rutina eliminada no aparece en búsquedas."""
    # Crear rutina
    rutina_data = RutinaCreate(
        nombre="Rutina a Eliminar",
        momento_dia="mañana",
        habitos=[]
    )
    rutina_creada = await rutinas_service.create_rutina(db, rutina_data, usuario_test.id)
    rutina_id = rutina_creada.id

    # Eliminar rutina
    await rutinas_service.delete_rutina(db, rutina_id, usuario_test.id)

    # Intentar obtener
    rutina = await rutinas_service.get_rutina_por_id(db, rutina_id)

    assert rutina is None  # No aparece


@pytest.mark.asyncio
async def test_get_rutinas_por_usuario(db: AsyncSession, usuario_test):
    """Test: Obtener todas las rutinas de un usuario."""
    # Crear 3 rutinas
    for i in range(3):
        rutina_data = RutinaCreate(
            nombre=f"Rutina {i}",
            momento_dia="mañana",
            habitos=[]
        )
        await rutinas_service.create_rutina(db, rutina_data, usuario_test.id)

    # Obtener rutinas del usuario
    rutinas = await rutinas_service.get_rutinas_por_usuario(db, usuario_test.id)

    assert len(rutinas) == 3
    for rutina in rutinas:
        assert rutina.usuario_id == usuario_test.id


# ============================================================================
# TESTS - ACTUALIZAR RUTINA
# ============================================================================

@pytest.mark.asyncio
async def test_update_rutina(db: AsyncSession, usuario_test):
    """Test: Actualizar los datos de una rutina."""
    # Crear rutina
    rutina_data = RutinaCreate(
        nombre="Rutina Original",
        momento_dia="mañana",
        es_publica=False,
        habitos=[]
    )
    rutina_creada = await rutinas_service.create_rutina(db, rutina_data, usuario_test.id)

    # Actualizar
    update_data = RutinaUpdate(
        nombre="Rutina Actualizada",
        es_publica=True,
        momento_dia="tarde"
    )
    rutina_actualizada = await rutinas_service.update_rutina(
        db, rutina_creada.id, update_data, usuario_test.id
    )

    assert rutina_actualizada.nombre == "Rutina Actualizada"
    assert rutina_actualizada.es_publica == True
    assert rutina_actualizada.momento_dia == "tarde"
    assert rutina_actualizada.updated_at > rutina_creada.created_at


@pytest.mark.asyncio
async def test_update_rutina_sin_permisos(db: AsyncSession, usuario_test):
    """Test: No se puede actualizar rutina de otro usuario."""
    # Crear rutina
    rutina_data = RutinaCreate(
        nombre="Rutina Ajena",
        momento_dia="mañana",
        habitos=[]
    )
    rutina_creada = await rutinas_service.create_rutina(db, rutina_data, usuario_test.id)

    # Intentar actualizar con otro usuario_id
    update_data = RutinaUpdate(nombre="Cambio No Permitido")
    resultado = await rutinas_service.update_rutina(
        db, rutina_creada.id, update_data, usuario_id=999  # Usuario diferente
    )

    assert resultado is None


# ============================================================================
# TESTS - SOFT DELETE
# ============================================================================

@pytest.mark.asyncio
async def test_delete_rutina_soft_delete(db: AsyncSession, usuario_test):
    """Test: Eliminar rutina realiza soft delete."""
    # Crear rutina
    rutina_data = RutinaCreate(
        nombre="Rutina a Eliminar",
        momento_dia="mañana",
        habitos=[]
    )
    rutina_creada = await rutinas_service.create_rutina(db, rutina_data, usuario_test.id)
    rutina_id = rutina_creada.id

    # Eliminar
    success = await rutinas_service.delete_rutina(db, rutina_id, usuario_test.id)

    assert success == True

    # Verificar que es soft delete (datos aún en BD pero marcados)
    result = await db.execute(
        select(Rutina).where(Rutina.id == rutina_id)
    )
    rutina_db = result.scalar_one_or_none()

    assert rutina_db is not None
    assert rutina_db.is_deleted == True
    assert rutina_db.deleted_at is not None


@pytest.mark.asyncio
async def test_delete_rutina_con_habitos(db: AsyncSession, usuario_test):
    """Test: Eliminar rutina también marca hábitos como eliminados."""
    # Crear rutina con hábitos
    habito = HabitoCreate(
        nombre="Hábito Test",
        tiempo_duracion_min=10,
        orden=1
    )
    rutina_data = RutinaCreate(
        nombre="Rutina con Hábitos",
        momento_dia="mañana",
        habitos=[habito]
    )
    rutina_creada = await rutinas_service.create_rutina(db, rutina_data, usuario_test.id)
    habito_id = rutina_creada.habitos[0].id

    # Eliminar rutina
    await rutinas_service.delete_rutina(db, rutina_creada.id, usuario_test.id)

    # Verificar que hábitos también se eliminaron
    h = await rutinas_service.get_habito_por_id(db, habito_id)
    assert h is None  # No aparece en búsquedas


@pytest.mark.asyncio
async def test_delete_rutina_no_existe(db: AsyncSession, usuario_test):
    """Test: Eliminar rutina que no existe retorna False."""
    success = await rutinas_service.delete_rutina(db, 99999, usuario_test.id)

    assert success == False


@pytest.mark.asyncio
async def test_delete_rutina_sin_permisos(db: AsyncSession, usuario_test):
    """Test: No se puede eliminar rutina de otro usuario."""
    # Crear rutina
    rutina_data = RutinaCreate(
        nombre="Rutina Ajena",
        momento_dia="mañana",
        habitos=[]
    )
    rutina_creada = await rutinas_service.create_rutina(db, rutina_data, usuario_test.id)

    # Intentar eliminar con otro usuario
    success = await rutinas_service.delete_rutina(db, rutina_creada.id, usuario_id=999)

    assert success == False


# ============================================================================
# TESTS - RESTORE
# ============================================================================

@pytest.mark.asyncio
async def test_restore_rutina(db: AsyncSession, usuario_test):
    """Test: Restaurar una rutina eliminada."""
    # Crear y eliminar rutina
    rutina_data = RutinaCreate(
        nombre="Rutina a Restaurar",
        momento_dia="mañana",
        habitos=[]
    )
    rutina_creada = await rutinas_service.create_rutina(db, rutina_data, usuario_test.id)
    rutina_id = rutina_creada.id

    await rutinas_service.delete_rutina(db, rutina_id, usuario_test.id)

    # Restaurar
    rutina_restaurada = await rutinas_service.restore_rutina(db, rutina_id, usuario_test.id)

    assert rutina_restaurada is not None
    assert rutina_restaurada.is_deleted == False
    assert rutina_restaurada.deleted_at is None


@pytest.mark.asyncio
async def test_restore_habitos_en_cascada(db: AsyncSession, usuario_test):
    """Test: Restaurar rutina también restaura sus hábitos."""
    # Crear rutina con hábitos
    habito = HabitoCreate(
        nombre="Hábito Test",
        tiempo_duracion_min=10,
        orden=1
    )
    rutina_data = RutinaCreate(
        nombre="Rutina con Hábitos",
        momento_dia="mañana",
        habitos=[habito]
    )
    rutina_creada = await rutinas_service.create_rutina(db, rutina_data, usuario_test.id)
    habito_id = rutina_creada.habitos[0].id

    # Eliminar
    await rutinas_service.delete_rutina(db, rutina_creada.id, usuario_test.id)

    # Restaurar
    await rutinas_service.restore_rutina(db, rutina_creada.id, usuario_test.id)

    # Verificar hábito restaurado
    h = await rutinas_service.get_habito_por_id(db, habito_id)
    assert h is not None
    assert h.is_deleted == False


# ============================================================================
# TESTS - HÁBITOS
# ============================================================================

@pytest.mark.asyncio
async def test_create_habito(db: AsyncSession, usuario_test):
    """Test: Crear un hábito en una rutina."""
    # Crear rutina
    rutina_data = RutinaCreate(
        nombre="Rutina Base",
        momento_dia="mañana",
        habitos=[]
    )
    rutina = await rutinas_service.create_rutina(db, rutina_data, usuario_test.id)

    # Crear hábito
    habito_data = HabitoCreate(
        nombre="Nuevo Hábito",
        tiempo_programado=time(7, 0, 0),
        tiempo_duracion_min=15,
        orden=1
    )
    habito = await rutinas_service.create_habito(db, habito_data, rutina.id)

    assert habito.id is not None
    assert habito.rutina_id == rutina.id
    assert habito.nombre == "Nuevo Hábito"
    assert habito.tiempo_duracion_min == 15


@pytest.mark.asyncio
async def test_get_habitos_por_rutina_ordenados(db: AsyncSession, usuario_test):
    """Test: Obtener hábitos ordenados por 'orden'."""
    # Crear rutina con hábitos
    habitos_data = [
        HabitoCreate(nombre="Hábito 3", orden=3),
        HabitoCreate(nombre="Hábito 1", orden=1),
        HabitoCreate(nombre="Hábito 2", orden=2),
    ]

    rutina_data = RutinaCreate(
        nombre="Rutina",
        momento_dia="mañana",
        habitos=habitos_data
    )
    rutina = await rutinas_service.create_rutina(db, rutina_data, usuario_test.id)

    # Obtener ordenados
    habitos = await rutinas_service.get_habitos_por_rutina(db, rutina.id)

    assert len(habitos) == 3
    assert habitos[0].nombre == "Hábito 1"
    assert habitos[1].nombre == "Hábito 2"
    assert habitos[2].nombre == "Hábito 3"


@pytest.mark.asyncio
async def test_update_habito(db: AsyncSession, usuario_test):
    """Test: Actualizar un hábito."""
    # Crear rutina con hábito
    habito_data = HabitoCreate(
        nombre="Hábito Original",
        tiempo_duracion_min=10,
        orden=1
    )
    rutina_data = RutinaCreate(
        nombre="Rutina",
        momento_dia="mañana",
        habitos=[habito_data]
    )
    rutina = await rutinas_service.create_rutina(db, rutina_data, usuario_test.id)
    habito_id = rutina.habitos[0].id

    # Actualizar
    update_data = HabitoUpdate(
        nombre="Hábito Actualizado",
        tiempo_duracion_min=20
    )
    habito_actualizado = await rutinas_service.update_habito(
        db, habito_id, update_data, usuario_test.id
    )

    assert habito_actualizado.nombre == "Hábito Actualizado"
    assert habito_actualizado.tiempo_duracion_min == 20


# ============================================================================
# TESTS - PAGINACIÓN
# ============================================================================

@pytest.mark.asyncio
async def test_get_rutinas_paginacion(db: AsyncSession, usuario_test):
    """Test: Paginación de rutinas."""
    # Crear 15 rutinas
    for i in range(15):
        rutina_data = RutinaCreate(
            nombre=f"Rutina {i}",
            momento_dia="mañana",
            habitos=[]
        )
        await rutinas_service.create_rutina(db, rutina_data, usuario_test.id)

    # Página 1
    rutinas_p1 = await rutinas_service.get_rutinas_por_usuario(
        db, usuario_test.id, skip=0, limit=5
    )
    assert len(rutinas_p1) == 5

    # Página 2
    rutinas_p2 = await rutinas_service.get_rutinas_por_usuario(
        db, usuario_test.id, skip=5, limit=5
    )
    assert len(rutinas_p2) == 5

    # Página 3
    rutinas_p3 = await rutinas_service.get_rutinas_por_usuario(
        db, usuario_test.id, skip=10, limit=5
    )
    assert len(rutinas_p3) == 5

    # Sin resultados
    rutinas_p4 = await rutinas_service.get_rutinas_por_usuario(
        db, usuario_test.id, skip=15, limit=5
    )
    assert len(rutinas_p4) == 0

# Para ejecutar estos tests:
# pytest app/tests/test_rutinas_crud.py -v
# pytest app/tests/test_rutinas_crud.py -k "test_create_rutina" -v
# pytest app/tests/test_rutinas_crud.py -k "soft_delete" -v

