from sqlalchemy import Column, String, ForeignKey, Text, TIMESTAMP, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import SoftDeleteMixin, MySQLBigInteger

class PublicacionComunidad(Base, SoftDeleteMixin):
    __tablename__ = "publicaciones_comunidad"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    usuario_id = Column(MySQLBigInteger(), ForeignKey("usuarios.id"))
    rutina_id = Column(MySQLBigInteger(), ForeignKey("rutinas.id"))
    descripcion = Column(Text)
    fecha_publicacion = Column(TIMESTAMP, server_default=func.now())

class Comentario(Base, SoftDeleteMixin):
    __tablename__ = "comentarios"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    publicacion_id = Column(MySQLBigInteger(), ForeignKey("publicaciones_comunidad.id", ondelete="CASCADE"))
    usuario_id = Column(MySQLBigInteger(), ForeignKey("usuarios.id"))
    contenido = Column(Text, nullable=False)
    fecha = Column(TIMESTAMP, server_default=func.now())

class Like(Base):
    __tablename__ = "likes"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    publicacion_id = Column(MySQLBigInteger(), ForeignKey("publicaciones_comunidad.id", ondelete="CASCADE"))
    usuario_id = Column(MySQLBigInteger(), ForeignKey("usuarios.id"))
    __table_args__ = (UniqueConstraint('publicacion_id', 'usuario_id', name='_publicacion_usuario_uc'),)

class LikeRutina(Base):
    __tablename__ = "likes_rutina"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    rutina_id = Column(MySQLBigInteger(), ForeignKey("rutinas.id", ondelete="CASCADE"))
    usuario_id = Column(MySQLBigInteger(), ForeignKey("usuarios.id"))
    fecha = Column(TIMESTAMP, server_default=func.now())
    
    rutina = relationship("Rutina", back_populates="likes")
    __table_args__ = (UniqueConstraint('rutina_id', 'usuario_id', name='_rutina_usuario_like_uc'),)
