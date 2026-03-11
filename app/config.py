"""
配置管理模块
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # ChemPrice API Keys
    molport_api_key: Optional[str] = None
    molport_username: Optional[str] = None
    molport_password: Optional[str] = None
    chemspace_api_key: Optional[str] = None
    mcule_api_key: Optional[str] = None
    
    # Server Config
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
