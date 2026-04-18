from sqlalchemy import Column, String, ForeignKey, Text, Boolean, Enum, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import SoftDeleteMixin, MySQLBigInteger

class DispositivoFCM(Base, SoftDeleteMixin):
    __tablename__ = "dispositivos_fcm"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    usuario_id = Column(MySQLBigInteger(), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    token_fcm = Column(String(255), unique=True, nullable=False)
    plataforma = Column(Enum('web', 'android', 'ios', 'movil', 'mobile'))
    activo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    usuario = relationship("Usuario", back_populates="dispositivos")

class CanalNotificacion(Base):
    __tablename__ = "canales_notificacion"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    slug = Column(String(50), unique=True, nullable=False)
    nombre_visible = Column(String(100), nullable=False)
    descripcion = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

class UsuarioSuscripcion(Base):
    __tablename__ = "usuario_suscripciones"
    usuario_id = Column(MySQLBigInteger(), ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    canal_id = Column(MySQLBigInteger(), ForeignKey("canales_notificacion.id", ondelete="CASCADE"), primary_key=True)
    activo = Column(Boolean, default=True)

class NotificacionHistorial(Base, SoftDeleteMixin):
    __tablename__ = "notificaciones_historial"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    usuario_id = Column(MySQLBigInteger(), ForeignKey("usuarios.id", ondelete="CASCADE"))
    titulo = Column(String(150))
    mensaje = Column(Text)
    tipo = Column(String(50))
    leida = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
