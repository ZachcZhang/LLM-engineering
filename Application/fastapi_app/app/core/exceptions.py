"""
统一错误处理模块
"""
from typing import Optional, Any, Dict, List, Union
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import traceback
import logging

logger = logging.getLogger(__name__)


class ErrorDetail(BaseModel):
    """错误详情"""
    type: str
    message: str
    field: Optional[str] = None
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """标准错误响应格式"""
    success: bool = False
    error: str
    message: str
    details: Optional[List[ErrorDetail]] = None
    status_code: int
    timestamp: str
    path: Optional[str] = None
    request_id: Optional[str] = None


class BusinessException(HTTPException):
    """业务异常"""
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = "业务处理异常",
        error_code: Optional[str] = None,
        field: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code
        self.field = field


class ValidationException(BusinessException):
    """验证异常"""
    def __init__(
        self,
        detail: str = "数据验证失败",
        field: Optional[str] = None,
        error_code: str = "VALIDATION_ERROR",
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code,
            field=field,
        )


class AuthenticationException(BusinessException):
    """认证异常"""
    def __init__(
        self,
        detail: str = "认证失败",
        error_code: str = "AUTHENTICATION_ERROR",
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationException(BusinessException):
    """授权异常"""
    def __init__(
        self,
        detail: str = "权限不足",
        error_code: str = "AUTHORIZATION_ERROR",
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code,
        )


class NotFoundException(BusinessException):
    """资源不存在异常"""
    def __init__(
        self,
        detail: str = "资源不存在",
        error_code: str = "NOT_FOUND",
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code,
        )


class ConflictException(BusinessException):
    """资源冲突异常"""
    def __init__(
        self,
        detail: str = "资源冲突",
        error_code: str = "CONFLICT",
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code,
        )


def create_error_response(
    request: Request,
    status_code: int,
    error: str,
    message: str,
    details: Optional[List[ErrorDetail]] = None,
    request_id: Optional[str] = None,
) -> ErrorResponse:
    """创建标准错误响应"""
    from datetime import datetime
    
    return ErrorResponse(
        success=False,
        error=error,
        message=message,
        details=details or [],
        status_code=status_code,
        timestamp=datetime.utcnow().isoformat() + "Z",
        path=str(request.url.path) if request else None,
        request_id=request_id,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP异常处理器"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    
    # 处理业务异常
    if isinstance(exc, BusinessException):
        details = []
        if exc.field or exc.error_code:
            details.append(ErrorDetail(
                type="business_error",
                message=exc.detail,
                field=exc.field,
                code=exc.error_code,
            ))
        
        error_response = create_error_response(
            request=request,
            status_code=exc.status_code,
            error=exc.error_code or "BUSINESS_ERROR",
            message=exc.detail,
            details=details,
        )
    else:
        # 处理标准HTTP异常
        error_type_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            422: "UNPROCESSABLE_ENTITY",
            500: "INTERNAL_SERVER_ERROR",
        }
        
        error_response = create_error_response(
            request=request,
            status_code=exc.status_code,
            error=error_type_map.get(exc.status_code, "HTTP_ERROR"),
            message=exc.detail,
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
    )


async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """验证异常处理器"""
    logger.error(f"Validation Error: {exc.errors()}")
    
    # 转换验证错误为标准格式
    details = []
    for error in exc.errors():
        field_name = ".".join(str(loc) for loc in error["loc"][1:]) if len(error["loc"]) > 1 else None
        details.append(ErrorDetail(
            type="validation_error",
            message=error["msg"],
            field=field_name,
            code=error["type"],
        ))
    
    error_response = create_error_response(
        request=request,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error="VALIDATION_ERROR",
        message="请求数据验证失败",
        details=details,
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器"""
    logger.error(f"Unhandled Exception: {type(exc).__name__}: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # 在生产环境中不暴露详细错误信息
    import os
    is_development = os.getenv("ENVIRONMENT", "development") == "development"
    
    if is_development:
        message = f"{type(exc).__name__}: {str(exc)}"
        details = [ErrorDetail(
            type="system_error",
            message=str(exc),
            code=type(exc).__name__,
        )]
    else:
        message = "服务器内部错误，请稍后重试"
        details = []
    
    error_response = create_error_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error="INTERNAL_SERVER_ERROR",
        message=message,
        details=details,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(),
    )


# 常用异常快速创建函数
def not_found_error(resource: str = "资源") -> NotFoundException:
    """资源不存在错误"""
    return NotFoundException(detail=f"{resource}不存在")


def validation_error(message: str, field: Optional[str] = None) -> ValidationException:
    """验证错误"""
    return ValidationException(detail=message, field=field)


def unauthorized_error(message: str = "请先登录") -> AuthenticationException:
    """未授权错误"""
    return AuthenticationException(detail=message)


def forbidden_error(message: str = "权限不足") -> AuthorizationException:
    """禁止访问错误"""
    return AuthorizationException(detail=message)


def conflict_error(message: str) -> ConflictException:
    """冲突错误"""
    return ConflictException(detail=message) 