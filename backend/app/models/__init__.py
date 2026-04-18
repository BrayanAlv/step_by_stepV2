from app.models.base import SoftDeleteMixin
from app.models.usuario import Plan, Usuario, PerfilUsuario, Seguidor
from app.models.rutina import HabitoCategoria, Rutina, Habito, SeguimientoHabito, CategoriaRutina, RutinaRating, HistorialRutina, RutinaIAGenerada
from app.models.notificacion import DispositivoFCM, CanalNotificacion, UsuarioSuscripcion, NotificacionHistorial
from app.models.comunidad import PublicacionComunidad, Comentario, Like, LikeRutina
from app.models.gamificacion import MascotaVirtual, Logro, UsuarioLogro
from app.models.frase import FraseMotivacional
