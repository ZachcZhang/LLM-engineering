"""
核心配置模块
"""
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 项目基本信息
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "YisCore Medical Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置 - 使用用户提供的PostgreSQL配置
    DATABASE_URL: str = "postgresql://root:123456@127.0.0.1:5433/project_db"
    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 10
    POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 1800
    
    # JWT 配置
    SECRET_KEY: str = "yiscore-medical-platform-secret-key-2025"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30 # 30 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 60  # 60 days
    
    # CORS 配置
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://localhost:5173",  # Vite 默认端口
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080",
        "http://0.0.0.0:3000",
        "http://0.0.0.0:8000"
    ]

    @field_validator("BACKEND_CORS_ORIGINS")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DIR: str = "logs"
    

    # Redis配置
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    
    OPENAI_API_BASE: str = "https://mdi.hkust-gz.edu.cn/hpc/qwen3/v1"
    OPENAI_API_KEY: str = "mdi"
    LLM_MODEL: str = "Qwen/Qwen3-32B"

    # LLM上下文-最大医疗报告数量
    MAX_MEDICAL_REPORTS: int = 20
    
    #LLM上下文-最大药物数量
    MAX_MEDICATIONS: int = 20

    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()