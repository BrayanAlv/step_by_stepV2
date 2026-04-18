from sqlalchemy import Column, String, Text, TIMESTAMP, func
from app.core.database import Base
from app.models.base import MySQLBigInteger, SoftDeleteMixin

class FraseMotivacional(Base, SoftDeleteMixin):
    __tablename__ = "frases_motivacionales"
    id = Column(MySQLBigInteger(), primary_key=True, index=True)
    texto = Column(Text, nullable=False)
    autor = Column(String(100), default="Anónimo")
    categoria = Column(String(50), index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
