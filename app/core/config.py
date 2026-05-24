from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Ateliê Digital - Order API"
    ENVIRONMENT: str = "development"
    DESCRIPTION: str = 'Microsserviço de gerenciamento de pedidos'
    VERSION: str = '0.1.0'
    
    # Secret key para decodificar os tokens JWT enviados pelo API Gateway/Auth
    SECRET_KEY: str 
    ALGORITHM: str 
    MERCADO_PAGO_TOKEN: str
    MELHOR_ENVIO_TOKEN: str
    WEBHOOK_SECRET: str

    DATABASE_URL: str

    REDIS_URL: str

    CATALOG_API_BASE_URL: str
    ACCOUNTS_API_BASE_URL: str
    
    # Essa configuração diz ao Pydantic para ler o arquivo .env automaticamente
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

 