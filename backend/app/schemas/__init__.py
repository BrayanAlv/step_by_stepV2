from app.schemas.auth import UserRegister, Token, TokenData
from app.schemas.rutina import (
    HabitoBase, HabitoCreate, HabitoUpdate, Habito, RutinaBase, RutinaCreate, RutinaUpdate, Rutina,
    CategoriaRutina, CategoriaRutinaCreate, HabitoCategoria, HabitoCategoriaCreate,
    RutinaRating, RutinaRatingCreate,
    HistorialRutina, HistorialRutinaCreate,
    ChecklistResponse, ChecklistHabitoItem, ChecklistRutinaItem
)
from app.schemas.seguimiento import SeguimientoCreate
from app.schemas.notificacion import FCMTokenCreate, SuscripcionUpdate, NotificacionSend, NotificacionMasiva
from app.schemas.usuario import Seguidor, SeguidorCreate, UsuarioSimple, UsuarioConSuscripcion, SuscripcionDetalle, PlanUpdate
from app.schemas.frase import FraseMotivacional, FraseMotivacionalCreate
from app.schemas.comunidad import Comentario, ComentarioCreate, ComentarioContenidoCreate
from app.schemas.pago import (
    CrearPagoIntentRequest, CrearPagoIntentResponse,
    WebhookEventResponse, PagoHistorial, SuscripcionResponse
)
