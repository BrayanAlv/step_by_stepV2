from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import time, datetime
from enum import Enum

# ============= ENUMS =============
class MomentoDiaEnum(str, Enum):
    """Momentos del día disponibles para rutinas."""
    MANANA = "mañana"
    TARDE = "tarde"
    NOCHE = "noche"
    PERSONALIZADO = "personalizado"

# ============= CATEGORÍAS DE RUTINA =============
class CategoriaRutinaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None
    padre_id: Optional[int] = None

class CategoriaRutinaCreate(CategoriaRutinaBase):
    pass

class CategoriaRutina(CategoriaRutinaBase):
    id: int
    estado: bool = True
    subcategorias: List['CategoriaRutina'] = []

    class Config:
        from_attributes = True

# ============= CATEGORÍAS DE HÁBITO =============
class HabitoCategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None

class HabitoCategoriaCreate(HabitoCategoriaBase):
    pass

class HabitoCategoria(HabitoCategoriaBase):
    id: int
    estado: bool = True

    class Config:
        from_attributes = True

# ============= HÁBITOS =============
class HabitoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del hábito")
    descripcion: Optional[str] = Field(None, max_length=500)
    categoria_id: Optional[int] = None
    tiempo_programado: Optional[time] = Field(None, description="Hora en formato HH:MM")
    tiempo_duracion_min: Optional[int] = Field(None, ge=1, le=480, description="Duración en minutos (1-480)")
    orden: int = Field(0, ge=0, description="Orden de ejecución en la rutina")

    @field_validator('tiempo_duracion_min')
    @classmethod
    def validate_duracion(cls, v):
        if v is not None and (v < 1 or v > 480):
            raise ValueError("La duración debe estar entre 1 y 480 minutos")
        return v

class HabitoCreate(HabitoBase):
    """Schema para crear un hábito nuevo."""
    pass

class HabitoUpdate(BaseModel):
    """Schema para actualizar un hábito existente."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    tiempo_programado: Optional[time] = None
    tiempo_duracion_min: Optional[int] = Field(None, ge=1, le=480)
    orden: Optional[int] = Field(None, ge=0)

class Habito(HabitoBase):
    id: int
    rutina_id: int
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class HabitoDetail(Habito):
    """Hábito con información adicional para respuestas detalladas."""
    pass

# ============= RUTINAS =============
class RutinaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre de la rutina")
    momento_dia: MomentoDiaEnum = Field(MomentoDiaEnum.MANANA, description="Momento del día")
    es_publica: bool = Field(False, description="Si la rutina es visible públicamente")
    categoria_id: Optional[int] = None

class RutinaCreate(RutinaBase):
    """Schema para crear una rutina con sus hábitos."""
    habitos: List[HabitoCreate] = Field(
        default=[],
        description="Lista de hábitos que componen la rutina",
        example=[
            {
                "nombre": "Tomar agua",
                "descripcion": "500ml al despertar",
                "tiempo_programado": "07:00",
                "tiempo_duracion_min": 5,
                "orden": 1
            }
        ]
    )

class RutinaUpdate(BaseModel):
    """Schema para actualizar una rutina existente."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    momento_dia: Optional[MomentoDiaEnum] = None
    es_publica: Optional[bool] = None
    categoria_id: Optional[int] = None

class Rutina(RutinaBase):
    id: int
    usuario_id: int
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    habitos: List[Habito] = []
    rating_promedio: Optional[float] = 0.0
    total_likes: Optional[int] = 0

    class Config:
        from_attributes = True

class RutinaDetail(Rutina):
    """Rutina con información completa para respuestas detalladas."""
    pass

# ============= RATINGS Y LIKES =============
class RutinaRatingBase(BaseModel):
    puntuacion: int = Field(..., ge=1, le=5, description="Puntuación de 1 a 5")
    comentario: Optional[str] = Field(None, max_length=500)

class RutinaRatingCreate(RutinaRatingBase):
    pass

class RutinaRating(RutinaRatingBase):
    id: int
    rutina_id: int
    usuario_id: int
    fecha: datetime

    class Config:
        from_attributes = True

class LikeRutina(BaseModel):
    rutina_id: int
    usuario_id: int
    fecha: datetime

    class Config:
        from_attributes = True

# ============= HISTORIAL =============
class HistorialRutinaCreate(BaseModel):
    rutina_id: int
    duracion_total_min: Optional[int] = Field(None, ge=0)

class HistorialRutina(BaseModel):
    id: int
    usuario_id: int
    rutina_id: int
    fecha_completada: datetime
    duracion_total_min: Optional[int] = None

    class Config:
        from_attributes = True

class ChecklistHabitoItem(BaseModel):
    id: int
    habito_id: int
    habito_nombre: str
    rutina_id: int
    rutina_nombre: str
    fecha: datetime | str
    estado: bool | int
    nota: Optional[str] = None
    estado_animo: Optional[str] = None

class ChecklistRutinaItem(BaseModel):
    id: int
    rutina_id: int
    rutina_nombre: str
    fecha_completada: datetime
    duracion_total_min: Optional[int] = None

class ChecklistResponse(BaseModel):
    habitos: List[ChecklistHabitoItem]
    rutinas: List[ChecklistRutinaItem]

# ============= IA =============
class IAInput(BaseModel):
    objetivo: str
    nivel: str = "principiante"
    dias_por_semana: int = 5
    tiempo_disponible_min: int = 30
    categoria: str = "bienestar"

class RutinaIAResponse(BaseModel):
    rutina: RutinaCreate
    frase_motivacional: str

class RutinaIAGenerada(BaseModel):
    id: int
    usuario_id: int
    prompt_usado: str
    respuesta_ia: str
    rutina_id: Optional[int]
    modelo_ia: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============= NANO BOT CHAT =============
class NanoBotChatInput(BaseModel):
    mensaje: str = Field(..., min_length=2, max_length=1500)
    intent: Literal["auto", "consultar_rutinas", "crear_rutina"] = "auto"
    guardar_rutina: bool = True


class NanoBotChatResponse(BaseModel):
    intent_detectado: Literal["consultar_rutinas", "crear_rutina", "fallback"]
    mensaje: str
    rutinas: Optional[List[Rutina]] = None
    rutina_creada: Optional[Rutina] = None
    rutina_sugerida: Optional[RutinaCreate] = None

