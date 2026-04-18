from sqlalchemy import Column, String, Integer, ForeignKey, Text, TIMESTAMP, Enum, Boolean, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import MySQLBigInteger

class MascotaVirtual(Base):
    __tablename__ = "mascota_virtual"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    usuario_id = Column(MySQLBigInteger(), ForeignKey("usuarios.id", ondelete="CASCADE"))
    nombre = Column(String(50), default='Buddy')
    estado_animo = Column(String(50), default='feliz')
    nivel = Column(Integer, default=1)
    experiencia = Column(Integer, default=0)
    
    usuario = relationship("Usuario", back_populates="mascota")

class Logro(Base):
    __tablename__ = "logros"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    icono = Column(String(100))
    tipo = Column(Enum('habitos', 'rutinas', 'racha', 'social'), nullable=False)
    meta = Column(Integer, nullable=False)
    experiencia_otorgada = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

class UsuarioLogro(Base):
    __tablename__ = "usuario_logros"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    usuario_id = Column(MySQLBigInteger(), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    logro_id = Column(MySQLBigInteger(), ForeignKey("logros.id", ondelete="CASCADE"), nullable=False)
    progreso = Column(Integer, default=0)
    completado = Column(Boolean, default=False)
    fecha_completado = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    __table_args__ = (UniqueConstraint('usuario_id', 'logro_id', name='_usuario_logro_uc'),)
    
    usuario = relationship("Usuario", back_populates="logros")
