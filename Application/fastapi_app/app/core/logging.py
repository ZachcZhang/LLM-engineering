"""
日志配置
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings


def setup_logging():
    """设置应用日志"""
    
    # 创建logs目录
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # 根日志器配置
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # 清除现有处理器
    root_logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL)
    console_formatter = logging.Formatter(settings.LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器
    file_handler = RotatingFileHandler(
        logs_dir / "yis_core.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    file_formatter = logging.Formatter(settings.LOG_FORMAT)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 错误日志文件处理器
    error_handler = RotatingFileHandler(
        logs_dir / "error.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    # 设置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志器"""
    return logging.getLogger(name) 