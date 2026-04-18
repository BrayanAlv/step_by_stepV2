from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy import Column, TIMESTAMP, Boolean
from app.core.database import Base

class SoftDeleteMixin:
    """
    Mixin para implementar soft delete (eliminación lógica).
    Registra cuándo fue eliminado un registro sin eliminarlo físicamente.
    """
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)

# Define common BigInteger type for MySQL to be unsigned if needed
def MySQLBigInteger():
    return BIGINT(unsigned=True)
