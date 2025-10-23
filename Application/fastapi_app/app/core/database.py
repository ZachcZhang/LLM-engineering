"""
数据库连接模块
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from app.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,            # 例: postgresql+psycopg2://user:pwd@host:5432/db
    pool_size=getattr(settings, "POOL_SIZE", 5),           # 常驻连接数
    max_overflow=getattr(settings, "MAX_OVERFLOW", 10),    # 突发额外连接
    pool_timeout=getattr(settings, "POOL_TIMEOUT", 30),    # 无可用连接时的等待秒数
    pool_recycle=getattr(settings, "POOL_RECYCLE", 1800),  # 连接存活时间（秒），小于DB/防火墙闲置超时
    pool_pre_ping=True,                                     # 每次取连接先 ping，自动踢掉失效连接
    echo=getattr(settings, "DEBUG", False),

    # psycopg2/psycopg 的连接级参数
    connect_args={
        "connect_timeout": 5,                # 连接超时，避免卡住
        # 如果是 psycopg2：
        "options": "-c statement_timeout=60000",  # 语句超时 60s，防止长时间占用连接
        # TCP keepalive，避免中间网络设备闲置断开（psycopg2）
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 3,
    },
)


# 创建会话工厂
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # 提升读取一致性和性能，提交后对象不立即过期
)

# 创建基础模型类
Base = declarative_base()

def get_db():
    """
    获取数据库会话的依赖注入函数
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """数据库会话上下文管理器"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close() 