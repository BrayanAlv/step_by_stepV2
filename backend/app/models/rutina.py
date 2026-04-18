from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, Enum, Time, Date, Float, TIMESTAMP, func
from sqlalchemy.orm import relationship, validates
from app.core.database import Base
from app.models.base import SoftDeleteMixin, MySQLBigInteger
from datetime import timedelta, time

class CategoriaRutina(Base):
    """Categorías para organizar rutinas de forma jerárquica."""
    __tablename__ = "categorias_rutina"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text)
    padre_id = Column(MySQLBigInteger(), ForeignKey("categorias_rutina.id"), nullable=True)
    estado = Column(Boolean, default=True)

    subcategorias = relationship("CategoriaRutina", backref="padre", remote_side=[id])
    rutinas = relationship("Rutina", back_populates="categoria")

class HabitoCategoria(Base):
    """Categorías predefinidas para hábitos."""
    __tablename__ = "habitos_categoria"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text)
    estado = Column(Boolean, default=True)

class Rutina(Base, SoftDeleteMixin):
    """
    Rutinas de hábitos. Una rutina contiene múltiples hábitos.
    Implementa soft delete para mantener historial.
    """
    __tablename__ = "rutinas"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    usuario_id = Column(MySQLBigInteger(), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    categoria_id = Column(MySQLBigInteger(), ForeignKey("categorias_rutina.id"), nullable=True)
    nombre = Column(String(100), nullable=False)
    momento_dia = Column(Enum('mañana', 'tarde', 'noche', 'personalizado'), default='mañana')
    es_publica = Column(Boolean, default=False)
    creada_por_ia = Column(Boolean, default=False)
    estado = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    usuario = relationship("Usuario", back_populates="rutinas")
    habitos = relationship("Habito", back_populates="rutina", cascade="all, delete-orphan")
    categoria = relationship("CategoriaRutina", back_populates="rutinas")
    ratings = relationship("RutinaRating", back_populates="rutina")
    likes = relationship("LikeRutina", back_populates="rutina")

class RutinaRating(Base):
    __tablename__ = "rutina_ratings"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    rutina_id = Column(MySQLBigInteger(), ForeignKey("rutinas.id", ondelete="CASCADE"))
    usuario_id = Column(MySQLBigInteger(), ForeignKey("usuarios.id"))
    puntuacion = Column(Integer, nullable=False) # 1 a 5
    comentario = Column(Text)
    fecha = Column(TIMESTAMP, server_default=func.now())

    rutina = relationship("Rutina", back_populates="ratings")

class HistorialRutina(Base):
    __tablename__ = "historial_rutinas"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    usuario_id = Column(MySQLBigInteger(), ForeignKey("usuarios.id", ondelete="CASCADE"))
    rutina_id = Column(MySQLBigInteger(), ForeignKey("rutinas.id"))
    fecha_completada = Column(TIMESTAMP, server_default=func.now())
    duracion_total_min = Column(Integer)

class Habito(Base, SoftDeleteMixin):
    """
    Hábitos individuales que pertenecen a una rutina.
    Implementa soft delete para mantener historial de cambios.
    """
    __tablename__ = "habitos"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    rutina_id = Column(MySQLBigInteger(), ForeignKey("rutinas.id", ondelete="CASCADE"), nullable=False)
    categoria_id = Column(MySQLBigInteger(), ForeignKey("habitos_categoria.id"), nullable=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    tiempo_programado = Column(Time)
    tiempo_duracion_min = Column(Integer)
    orden = Column(Integer, default=0)
    estado = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    rutina = relationship("Rutina", back_populates="habitos")
    seguimientos = relationship("SeguimientoHabito", back_populates="habito", cascade="all, delete-orphan")

    @validates('tiempo_programado')
    def validate_tiempo_programado(self, key, value):
        """Convierte timedelta a time si es necesario."""
        if isinstance(value, timedelta):
            total_seconds = int(value.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            return time(hour=hours, minute=minutes, second=seconds)
        return value

class SeguimientoHabito(Base, SoftDeleteMixin):
    __tablename__ = "seguimiento_habitos"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    habito_id = Column(MySQLBigInteger(), ForeignKey("habitos.id", ondelete="CASCADE"))
    fecha = Column(Date, server_default=func.current_date())
    estado = Column(Boolean, default=False)
    nota = Column(Text)
    estado_animo = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    habito = relationship("Habito", back_populates="seguimientos")

class RutinaIAGenerada(Base):
    __tablename__ = "rutinas_ia_generadas"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    usuario_id = Column(MySQLBigInteger(), ForeignKey("usuarios.id", ondelete="CASCADE"))
    prompt_usado = Column(Text, nullable=False)
    respuesta_ia = Column(Text, nullable=False)
    rutina_id = Column(MySQLBigInteger(), ForeignKey("rutinas.id"), nullable=True)
    modelo_ia = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    usuario = relationship("Usuario")
    rutina = relationship("Rutina")
