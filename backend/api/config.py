from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Configuration manager for Aegis Ocean V2.
    Automatically loads environment variables from the root .env file.
    """
    # API Credentials (ESA / Copernicus)
    CDSE_CLIENT_ID: str
    CDSE_CLIENT_SECRET: str
    CMEMS_KEY: str
    
    # Hybrid Database Stack
    DATABASE_URL: str
    CLICKHOUSE_URL: str
    
    # Mathematical Constants for Layer 4 Physics & Spatial Hashing
    H3_RESOLUTION: int = 7
    WINDAGE_COEFF: float = 0.03
    PARTICLE_COUNT: int = 2000
    
    # Pydantic V2 Configuration Directive
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

# Instantiate the global settings singleton used across all layers
settings = Settings()