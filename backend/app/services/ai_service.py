import json
import httpx
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Literal
import unicodedata
import re
from datetime import time
from app.core.config import settings


class AIServiceError(Exception):
    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        status_code: Optional[int] = None,
        is_transient: bool = False,
        is_config_error: bool = False,
    ):
        super().__init__(message)
        self.model = model
        self.status_code = status_code
        self.is_transient = is_transient
        self.is_config_error = is_config_error

class AIProvider(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str) -> str:
        pass

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    async def generate_response(self, prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": settings.AI_TEMPERATURE,
                "maxOutputTokens": settings.AI_MAX_TOKENS,
            }
        }
        try:
            async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT) as client:
                response = await client.post(url, json=payload)
        except (httpx.TimeoutException, httpx.RequestError) as exc:
            raise AIServiceError(
                f"Error de red/timeout con Gemini [{self.model}]: {str(exc)}",
                model=self.model,
                is_transient=True,
            )

        if response.status_code != 200:
            error_text = response.text
            error_message = error_text
            error_status = ""
            try:
                payload = response.json()
                error_obj = payload.get("error", {}) if isinstance(payload, dict) else {}
                error_message = error_obj.get("message", error_text)
                error_status = error_obj.get("status", "")
            except Exception:
                pass

            is_transient = response.status_code in (429, 500, 502, 503, 504)
            is_config_error = response.status_code in (400, 404) or error_status in ("NOT_FOUND", "INVALID_ARGUMENT")

            raise AIServiceError(
                f"Error de Gemini [{self.model}] ({response.status_code}): {error_message}",
                model=self.model,
                status_code=response.status_code,
                is_transient=is_transient,
                is_config_error=is_config_error,
            )

        data = response.json()
        try:
            return data['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            raise AIServiceError(
                f"Respuesta inesperada de Gemini [{self.model}]",
                model=self.model,
            )

class AIService:
    def __init__(self):
        if settings.AI_PROVIDER == "gemini":
            self.primary_provider = GeminiProvider(settings.AI_API_KEY, settings.AI_MODEL)
            self.fallback_provider = GeminiProvider(settings.AI_API_KEY, settings.AI_FALLBACK_MODEL)
            self._last_used_model = settings.AI_MODEL
        else:
            # Fallback o otros providers
            raise ValueError(f"Provider {settings.AI_PROVIDER} no soportado actualmente")

    def get_last_used_model(self) -> str:
        return self._last_used_model

    async def _generate_with_fallback(self, prompt: str) -> str:
        try:
            response = await self.primary_provider.generate_response(prompt)
            self._last_used_model = self.primary_provider.model
            return response
        except AIServiceError as primary_error:
            # Solo usamos fallback para errores transitorios del modelo principal.
            if not primary_error.is_transient:
                raise Exception(str(primary_error))

            if self.fallback_provider.model == self.primary_provider.model:
                raise primary_error

            try:
                response = await self.fallback_provider.generate_response(prompt)
                self._last_used_model = self.fallback_provider.model
                return response
            except AIServiceError as fallback_error:
                if fallback_error.is_config_error:
                    raise Exception(
                        f"Modelo fallback inválido/no disponible ({self.fallback_provider.model}). "
                        "Revisa AI_FALLBACK_MODEL con el endpoint ListModels de Gemini. "
                        f"Detalle: {fallback_error}"
                    )

                raise Exception(
                    "No se pudo generar respuesta con IA. "
                    f"Primary ({self.primary_provider.model}): {primary_error} | "
                    f"Fallback ({self.fallback_provider.model}): {fallback_error}"
                )

    def detect_chat_intent(self, message: str, requested_intent: str = "auto") -> Literal["consultar_rutinas", "crear_rutina", "fallback"]:
        """Detecta intención de forma simple para no bloquear el flujo por dependencias externas."""
        if requested_intent in ("consultar_rutinas", "crear_rutina"):
            return requested_intent  # type: ignore[return-value]

        normalized = self._normalize_text(message)

        create_tokens = [
            "crear", "crea", "genera", "generar", "construir", "construye", "armar", "arma",
            "disenar", "disena", "preparar", "prepara", "planear", "planea",
            "nueva rutina", "rutina nueva", "rutina para",
            "nuevo habito", "nuevos habitos",
        ]
        if any(token in normalized for token in create_tokens):
            return "crear_rutina"

        # Heurística contextual: solicitudes de ayuda + palabra rutina suelen ser intención de creación.
        if "rutina" in normalized and any(token in normalized for token in ["ayudame", "quiero", "necesito", "podrias", "puedes"]):
            return "crear_rutina"

        if any(token in normalized for token in ["mis rutinas", "ver rutinas", "listar rutinas", "consultar rutinas", "rutinas activas", "mostrar rutinas"]):
            return "consultar_rutinas"
        return "fallback"

    def _normalize_text(self, text: str) -> str:
        value = (text or "").strip().lower()
        return "".join(
            c for c in unicodedata.normalize("NFD", value)
            if unicodedata.category(c) != "Mn"
        )

    def build_routine_prompt_data_from_chat(self, message: str) -> Dict[str, Any]:
        """Mapea el mensaje libre del chat a requerimientos estructurados."""
        normalized = self._normalize_text(message)

        nivel = "principiante"
        if "intermedio" in normalized:
            nivel = "intermedio"
        elif "avanzado" in normalized:
            nivel = "avanzado"

        dias_por_semana = 5
        dias_match = re.search(r"(\d+)\s*(dias|dia)", normalized)
        if dias_match:
            dias_por_semana = max(1, min(7, int(dias_match.group(1))))

        tiempo_disponible_min = 30
        minutos_match = re.search(r"(\d+)\s*(minutos|minuto|min)", normalized)
        if minutos_match:
            tiempo_disponible_min = max(10, min(240, int(minutos_match.group(1))))

        momento_preferido = "mañana"
        if "noche" in normalized or "dormir" in normalized or "sueno" in normalized:
            momento_preferido = "noche"
        elif "tarde" in normalized:
            momento_preferido = "tarde"
        elif "personalizado" in normalized:
            momento_preferido = "personalizado"

        categoria = "bienestar"
        if any(token in normalized for token in ["sueno", "dormir", "descanso"]):
            categoria = "sueño"
        elif any(token in normalized for token in ["productividad", "enfoque", "estudio"]):
            categoria = "productividad"
        elif any(token in normalized for token in ["ejercicio", "fitness", "entrenamiento"]):
            categoria = "actividad"

        return {
            "objetivo": message,
            "nivel": nivel,
            "dias_por_semana": dias_por_semana,
            "tiempo_disponible_min": tiempo_disponible_min,
            "categoria": categoria,
            "momento_preferido": momento_preferido,
        }

    async def generate_routine(self, user_data: Dict[str, Any], categories: Optional[List[Dict[str, Any]]] = None, habit_categories: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        categories_str = ""
        if categories:
            categories_str = "CATEGORÍAS DE RUTINA disponibles (usa éstas para la rutina principal):\n" + "\n".join([f"- ID {c['id']}: {c['nombre']}" for c in categories])
        else:
            categories_str = "No hay categorías de rutina. Usa null."

        habit_categories_str = ""
        if habit_categories:
            habit_categories_str = "CATEGORÍAS DE HÁBITO disponibles (usa éstas para los hábitos individuales dentro de la rutina):\n" + "\n".join([f"- ID {c['id']}: {c['nombre']}" for c in habit_categories])
        else:
            habit_categories_str = "No hay categorías de hábito. Usa null."

        prompt = f"""
        Actúa como un experto en productividad y bienestar. 
        Genera una rutina personalizada en formato JSON estricto para un usuario con los siguientes datos:
        - Objetivo: {user_data.get('objetivo')}
        - Nivel: {user_data.get('nivel')}
        - Días por semana: {user_data.get('dias_por_semana')}
        - Tiempo disponible: {user_data.get('tiempo_disponible_min')} minutos
        - Categoría de interés sugerida por el usuario: {user_data.get('categoria')}
        - Momento preferido sugerido: {user_data.get('momento_preferido', 'mañana')}
        
        {categories_str}
        
        {habit_categories_str}

        INSTRUCCIONES CRÍTICAS DE ID:
        1. Para el objeto 'rutina', el campo 'categoria_id' DEBE ser un ID de la lista 'CATEGORÍAS DE RUTINA'.
        2. Para cada elemento en la lista 'habitos', el campo 'categoria_id' DEBE ser un ID de la lista 'CATEGORÍAS DE HÁBITO'.
        3. Si ninguna categoría encaja, usa null. NUNCA uses texto o nombres.

        FORMATO ESTRICTO COMPATIBLE CON BASE DE DATOS:
        1. Solo se permiten estas claves en rutina: nombre, momento_dia, es_publica, categoria_id, habitos.
        2. Solo se permiten estas claves en cada hábito: nombre, descripcion, categoria_id, tiempo_programado, tiempo_duracion_min, orden.
        3. momento_dia SOLO puede ser uno de: "mañana", "tarde", "noche", "personalizado".
        4. tiempo_programado debe estar en formato "HH:MM:SS".
        5. tiempo_duracion_min debe ser entero entre 1 y 480.
        6. orden debe iniciar en 1 y ser consecutivo.
        7. Usa es_publica = false por defecto.
        8. Alinea la rutina con el momento preferido y el objetivo del usuario.
        
        La respuesta DEBE ser ÚNICAMENTE un objeto JSON válido.
        
        Estructura JSON requerida:
        {{
            "rutina": {{
                "nombre": "Nombre de la rutina inspirador",
                "momento_dia": "mañana",
                "categoria_id": ID_DE_CATEGORIA_RUTINA_O_NULL,
                "habitos": [
                    {{
                        "nombre": "Nombre del hábito",
                        "descripcion": "Descripción breve",
                        "tiempo_programado": "HH:MM:SS",
                        "tiempo_duracion_min": 10,
                        "orden": 1,
                        "categoria_id": ID_DE_CATEGORIA_HABITO_O_NULL
                    }}
                ]
            }},
            "frase_motivacional": "Una frase inspiradora personalizada"
        }}
        """

        # Primer intento normal.
        response_text = await self._generate_with_fallback(prompt)
        parsed = self._parse_json_from_ai_response(response_text)
        if parsed is not None:
            return self._normalize_ai_routine_payload(parsed, user_data)

        # Reintento único con instrucciones más estrictas para evitar respuestas truncadas/markdown.
        retry_prompt = prompt + """

        IMPORTANTE:
        - Responde SOLO JSON válido en una sola línea (sin ```json ni texto adicional).
        - No expliques nada.
        - Si el contenido es largo, reduce descripciones pero entrega JSON completo y bien cerrado.
        """
        retry_response = await self._generate_with_fallback(retry_prompt)
        parsed_retry = self._parse_json_from_ai_response(retry_response)
        if parsed_retry is not None:
            return self._normalize_ai_routine_payload(parsed_retry, user_data)

        raise Exception(f"La IA no devolvió un JSON válido: {retry_response}")

    async def generate_motivational_phrase(self, routines_summary: str) -> str:
        prompt = f"""
        Basado en estas rutinas actuales del usuario: {routines_summary}
        Genera una frase motivacional corta, potente y personalizada.
        Sólo devuelve la frase, nada más.
        """
        return await self._generate_with_fallback(prompt)

    def _parse_json_from_ai_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        cleaned = self._strip_markdown_fences(response_text)
        json_candidate = self._extract_balanced_json(cleaned)
        if not json_candidate:
            return None
        try:
            parsed = json.loads(json_candidate)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None

    def _strip_markdown_fences(self, text: str) -> str:
        return re.sub(r"^```(?:json)?\s*|\s*```$", "", (text or "").strip(), flags=re.IGNORECASE)

    def _extract_balanced_json(self, text: str) -> Optional[str]:
        start = text.find("{")
        if start == -1:
            return None

        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                continue

            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]

        return None

    def _normalize_ai_routine_payload(self, payload: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        routine = payload.get("rutina", {}) if isinstance(payload, dict) else {}
        if not isinstance(routine, dict):
            routine = {}

        habitos_raw = routine.get("habitos", [])
        if not isinstance(habitos_raw, list):
            habitos_raw = []

        normalized_habitos: List[Dict[str, Any]] = []
        for idx, habito in enumerate(habitos_raw, start=1):
            if not isinstance(habito, dict):
                continue

            nombre = str(habito.get("nombre") or f"Hábito {idx}").strip()[:100]
            descripcion = habito.get("descripcion")
            if descripcion is not None:
                descripcion = str(descripcion).strip()[:500]

            categoria_id = self._to_int_or_none(habito.get("categoria_id"))
            tiempo_programado = self._normalize_time_str(habito.get("tiempo_programado"), idx)
            duracion = self._to_int_or_none(habito.get("tiempo_duracion_min"))
            if duracion is None:
                duracion = 10
            duracion = max(1, min(480, duracion))

            normalized_habitos.append(
                {
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "categoria_id": categoria_id,
                    "tiempo_programado": tiempo_programado,
                    "tiempo_duracion_min": duracion,
                    "orden": idx,
                }
            )

        if not normalized_habitos:
            normalized_habitos = [
                {
                    "nombre": "Respiración consciente",
                    "descripcion": "Respira de forma lenta y profunda para bajar el estrés.",
                    "categoria_id": None,
                    "tiempo_programado": "21:00:00",
                    "tiempo_duracion_min": 10,
                    "orden": 1,
                }
            ]

        momento_dia = self._normalize_momento_dia(routine.get("momento_dia"), user_data.get("momento_preferido"))

        normalized_rutina = {
            "nombre": str(routine.get("nombre") or "Rutina personalizada").strip()[:100],
            "momento_dia": momento_dia,
            "es_publica": bool(routine.get("es_publica", False)),
            "categoria_id": self._to_int_or_none(routine.get("categoria_id")),
            "habitos": normalized_habitos,
        }

        return {
            "rutina": normalized_rutina,
            "frase_motivacional": str(payload.get("frase_motivacional") or "Un paso a la vez también es progreso.").strip(),
        }

    def _to_int_or_none(self, value: Any) -> Optional[int]:
        try:
            if value is None:
                return None
            return int(value)
        except (TypeError, ValueError):
            return None

    def _normalize_momento_dia(self, value: Any, fallback: Any = None) -> str:
        allowed = {"mañana", "tarde", "noche", "personalizado"}
        if isinstance(value, str):
            val = value.strip().lower()
            if val in allowed:
                return val
            if self._normalize_text(val) == "manana":
                return "mañana"

        if isinstance(fallback, str):
            fb = fallback.strip().lower()
            if fb in allowed:
                return fb
            if self._normalize_text(fb) == "manana":
                return "mañana"

        return "mañana"

    def _normalize_time_str(self, value: Any, order: int) -> str:
        if isinstance(value, str):
            candidate = value.strip()
            if re.match(r"^\d{2}:\d{2}:\d{2}$", candidate):
                return candidate
            if re.match(r"^\d{2}:\d{2}$", candidate):
                return f"{candidate}:00"

        hour = min(23, max(0, 6 + order))
        return time(hour=hour, minute=0, second=0).strftime("%H:%M:%S")

ai_service = AIService()
