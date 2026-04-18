from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Step by Step"
    SECRET_KEY: str = "YOUR_SECRET_KEY_HERE" #
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1444
    
    DATABASE_URL: str = "mysql+aiomysql://root:Lisa7870@localhost/rutinas_test"
    
    # Configuración de Firebase
    FIREBASE_SERVICE_ACCOUNT_JSON: Optional[str] = "/app/app/core/step-by-step-2ef81-firebase-adminsdk-fbsvc-a96d65d8ba.json"
    FIREBASE_ENABLED: bool = True

    # Configuración de IA
    AI_PROVIDER: str = "gemini"
    AI_MODEL: str = "gemini-3.1-flash-lite-preview"
    AI_FALLBACK_MODEL: str = "gemini-2.5-flash"
    AI_API_KEY: str = ""
    AI_TIMEOUT: int = 30
    AI_MAX_TOKENS: int = 1000
    AI_TEMPERATURE: float = 0.7

    # Configuración de Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_CURRENCY: str = "mxn"

    class Config:
        env_file = ".env"

settings = Settings()
