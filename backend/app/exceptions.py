"""全局异常处理"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
import logging
import traceback
import os

# 配置日志
logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求参数验证错误"""
    errors = []
    for error in exc.errors():
        field = '.'.join(str(x) for x in error['loc'][1:])  # 跳过 'body'
        message = error['msg']
        errors.append(f"{field}: {message}" if field else message)
    
    logger.warning(f"请求参数验证失败: {request.url.path} - {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "请求参数验证失败",
            "errors": errors,
            "path": request.url.path
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """处理数据库异常"""
    error_msg = str(exc)
    
    # 记录详细错误
    logger.error(f"数据库错误: {request.url.path}")
    logger.error(f"错误详情: {error_msg}")
    logger.error(traceback.format_exc())
    
    # 判断是否是完整性约束错误
    if isinstance(exc, IntegrityError):
        if "UNIQUE constraint failed" in error_msg:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "detail": "数据已存在，违反唯一性约束",
                    "error_type": "integrity_error",
                    "path": request.url.path
                }
            )
        elif "FOREIGN KEY constraint failed" in error_msg:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": "关联数据不存在，违反外键约束",
                    "error_type": "foreign_key_error",
                    "path": request.url.path
                }
            )
    
    # 通用数据库错误
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "数据库操作失败，请稍后重试",
            "error_type": "database_error",
            "path": request.url.path
        }
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """处理 Pydantic 模型验证错误"""
    errors = []
    for error in exc.errors():
        field = '.'.join(str(x) for x in error['loc'])
        message = error['msg']
        errors.append(f"{field}: {message}")
    
    logger.warning(f"数据验证失败: {request.url.path} - {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "数据验证失败",
            "errors": errors,
            "path": request.url.path
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    error_msg = str(exc)
    error_type = type(exc).__name__
    
    # 记录详细错误信息
    logger.error(f"未处理的异常: {request.url.path}")
    logger.error(f"异常类型: {error_type}")
    logger.error(f"错误信息: {error_msg}")
    logger.error(traceback.format_exc())
    
    # 开发环境返回详细错误，生产环境返回通用错误
    debug_str = os.getenv("DEBUG")
    if debug_str is None:
        raise ValueError("DEBUG 环境变量未设置，请在 .env 文件中配置")
    debug_mode = debug_str.lower() == "true"
    
    if debug_mode:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "服务器内部错误",
                "error_type": error_type,
                "error_message": error_msg,
                "path": request.url.path,
                "traceback": traceback.format_exc().split('\n')
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "服务器内部错误，请稍后重试",
                "error_type": "internal_error",
                "path": request.url.path
            }
        )


# 自定义业务异常
class BusinessException(Exception):
    """业务逻辑异常"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


async def business_exception_handler(request: Request, exc: BusinessException):
    """处理业务逻辑异常"""
    logger.warning(f"业务异常: {request.url.path} - {exc.message}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_type": "business_error",
            "path": request.url.path
        }
    )

