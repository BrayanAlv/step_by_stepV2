from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey, Text, Boolean, DECIMAL, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import SoftDeleteMixin, MySQLBigInteger

class Plan(Base):
    __tablename__ = "planes"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    duracion_trial_dias = Column(Integer, default=14)
    limite_rutinas = Column(Integer)
    permite_ia = Column(Boolean, default=False)
    permite_mascota = Column(Boolean, default=False)
    notificaciones_avanzadas = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    usuarios = relationship("Usuario", back_populates="plan")

class Usuario(Base, SoftDeleteMixin):
    __tablename__ = "usuarios"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido_paterno = Column(String(100))
    apellido_materno = Column(String(100))
    correo_electronico = Column(String(150), unique=True, nullable=False, index=True)
    contrasena = Column(String(255), nullable=False)
    telefono = Column(String(20))
    fecha_registro = Column(TIMESTAMP, server_default=func.now())
    fecha_fin_trial = Column(TIMESTAMP, nullable=True)
    estado = Column(String(20), default="activo")
    foto_perfil = Column(Text)
    plan_id = Column(MySQLBigInteger(), ForeignKey("planes.id"))
    
    # Campos para suscripción pagada
    stripe_customer_id = Column(String(255), nullable=True, index=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    tipo_suscripcion_pagada = Column(String(50), nullable=True)  # mensual, trimestral, anual
    fecha_inicio_suscripcion = Column(TIMESTAMP, nullable=True)
    fecha_fin_suscripcion = Column(TIMESTAMP, nullable=True)
    es_suscripcion_activa = Column(Boolean, default=False)

    plan = relationship("Plan", back_populates="usuarios")
    perfil = relationship("PerfilUsuario", back_populates="usuario", uselist=False)
    dispositivos = relationship("DispositivoFCM", back_populates="usuario")
    rutinas = relationship("Rutina", back_populates="usuario")
    mascota = relationship("MascotaVirtual", back_populates="usuario", uselist=False)
    logros = relationship("UsuarioLogro", back_populates="usuario")

    seguidores = relationship(
        "Seguidor",
        foreign_keys="[Seguidor.seguido_id]",
        back_populates="seguido"
    )
    siguiendo = relationship(
        "Seguidor",
        foreign_keys="[Seguidor.seguidor_id]",
        back_populates="seguidor"
    )

class Seguidor(Base):
    __tablename__ = "seguidores"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    seguidor_id = Column(MySQLBigInteger(), ForeignKey("usuarios.id", ondelete="CASCADE"))
    seguido_id = Column(MySQLBigInteger(), ForeignKey("usuarios.id", ondelete="CASCADE"))
    fecha_seguimiento = Column(TIMESTAMP, server_default=func.now())

    seguidor = relationship("Usuario", foreign_keys=[seguidor_id], back_populates="siguiendo")
    seguido = relationship("Usuario", foreign_keys=[seguido_id], back_populates="seguidores")

    __table_args__ = (UniqueConstraint('seguidor_id', 'seguido_id', name='_seguidor_seguido_uc'),)

class PerfilUsuario(Base, SoftDeleteMixin):
    __tablename__ = "perfil_usuario"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    usuario_id = Column(MySQLBigInteger(), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    biografia = Column(Text)
    objetivos = Column(Text)
    progreso = Column(DECIMAL(5, 2), default=0.00)
    
    usuario = relationship("Usuario", back_populates="perfil")
