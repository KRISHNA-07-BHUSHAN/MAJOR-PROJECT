# sentinalCloud-backend/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "SentinelCloud Backend API"
    APP_VERSION: str = "1.0.0"
    
    # Use lowercase for standard convention
    MODELS_DIR: str = "saved_models"
    
    # SCALER_PATH has been removed
    
    DETECTION_THRESHOLD: float = 0.5
    SHAP_NSAMPLES: int = 100

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()