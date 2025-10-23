"""
FastAPI主应用
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import logging
from app.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import Base, engine, SessionLocal
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)

from contextlib import asynccontextmanager

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""

    # 启动时初始化
    logger.info("YisCore API启动中...")

    # 初始化数据
    db = SessionLocal()
    try:
        pass
    except Exception as e:
        logger.error(f"初始化失败: {e}")
    finally:
        db.close()
    
    logger.info("YisCore API启动完成")
    yield

    """应用关闭事件"""
    logger.info("YisCore API关闭中...")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# 注册错误处理器
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 设置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_origin_regex=None,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
        "X-Requested-With",
        "Accept",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers"
    ],
    expose_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization"
    ],
    max_age=600,  # 预检请求缓存10分钟
)

# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    """
    API根路径
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs_url": f"{settings.API_V1_STR}/docs"
    }


@app.get("/health")
def health_check():
    """
    健康检查端点
    """
    return {"status": "healthy", "service": settings.PROJECT_NAME} 