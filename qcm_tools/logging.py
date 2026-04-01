"""
QCM-AI-DevTools 日志系统

提供结构化日志记录和追踪功能
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json


# 日志格式
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DETAILED_FORMAT = """================================================================================
时间: %(asctime)s
模块: %(name)s
级别: %(levelname)s
消息: %(message)s
================================================================================"""

# 日志颜色代码（终端输出）
COLORS = {
    'DEBUG': '\033[36m',    # 青色
    'INFO': '\033[32m',     # 绿色
    'WARNING': '\033[33m',  # 黄色
    'ERROR': '\033[31m',    # 红色
    'CRITICAL': '\033[35m', # 紫色
    'RESET': '\033[0m'      # 重置
}


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""

    def format(self, record):
        # 添加颜色
        if record.levelname in COLORS:
            record.levelname = (
                f"{COLORS[record.levelname]}{record.levelname}{COLORS['RESET']}"
            )
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON 格式日志格式化器"""

    def format(self, record):
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'logger': record.name,
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # 添加额外字段
        if hasattr(record, 'context'):
            log_obj['context'] = record.context
        if hasattr(record, 'extra_data'):
            log_obj['extra_data'] = record.extra_data

        # 添加异常信息
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_obj, ensure_ascii=False, indent=2)


class QCMLogger:
    """
    QCM 工具日志器

    提供统一的日志记录接口，支持多种输出格式和目标

    Example:
        >>> from qcm_tools.logging import get_logger
        >>> logger = get_logger('my_module')
        >>> logger.info("操作成功")
        >>> logger.error("操作失败", extra={'context': {'user': 'admin'}})
    """

    _loggers: Dict[str, logging.Logger] = {}
    _global_config = {
        'level': logging.INFO,
        'format': 'default',
        'output': 'console',
        'file_path': None
    }

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        获取或创建日志器

        Args:
            name: 日志器名称

        Returns:
            配置好的 Logger 实例
        """
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(cls._global_config['level'])

        # 清除现有 handlers
        logger.handlers = []

        # 添加 handler
        if cls._global_config['output'] == 'console':
            handler = cls._create_console_handler()
        elif cls._global_config['output'] == 'file':
            handler = cls._create_file_handler()
        elif cls._global_config['output'] == 'both':
            logger.addHandler(cls._create_console_handler())
            handler = cls._create_file_handler()
        else:
            handler = cls._create_console_handler()

        logger.addHandler(handler)
        cls._loggers[name] = logger

        return logger

    @classmethod
    def configure(
        cls,
        level: int = logging.INFO,
        format_type: str = 'default',
        output: str = 'console',
        file_path: Optional[str] = None
    ):
        """
        全局配置日志系统

        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format_type: 格式类型 ('default', 'detailed', 'json')
            output: 输出目标 ('console', 'file', 'both')
            file_path: 日志文件路径（当 output 为 'file' 或 'both' 时必需）
        """
        cls._global_config = {
            'level': level,
            'format': format_type,
            'output': output,
            'file_path': file_path
        }

        # 更新所有现有日志器
        for name, logger in cls._loggers.items():
            logger.setLevel(level)
            # 重新配置 handlers
            logger.handlers = []
            if output == 'console':
                logger.addHandler(cls._create_console_handler())
            elif output == 'file':
                logger.addHandler(cls._create_file_handler())
            elif output == 'both':
                logger.addHandler(cls._create_console_handler())
                logger.addHandler(cls._create_file_handler())

    @classmethod
    def _create_console_handler(cls) -> logging.Handler:
        """创建控制台 handler"""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(cls._global_config['level'])

        # 选择格式化器
        if cls._global_config['format'] == 'json':
            formatter = JSONFormatter()
        elif cls._global_config['format'] == 'detailed':
            formatter = ColoredFormatter(DETAILED_FORMAT)
        else:
            formatter = ColoredFormatter(DEFAULT_FORMAT)

        handler.setFormatter(formatter)
        return handler

    @classmethod
    def _create_file_handler(cls) -> logging.Handler:
        """创建文件 handler"""
        file_path = cls._global_config.get('file_path')
        if not file_path:
            file_path = f"qcm_tools_{datetime.now().strftime('%Y%m%d')}.log"

        # 确保目录存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        handler = logging.FileHandler(file_path, encoding='utf-8')
        handler.setLevel(cls._global_config['level'])

        # 选择格式化器（文件不使用彩色）
        if cls._global_config['format'] == 'json':
            formatter = JSONFormatter()
        elif cls._global_config['format'] == 'detailed':
            formatter = logging.Formatter(DETAILED_FORMAT)
        else:
            formatter = logging.Formatter(DEFAULT_FORMAT)

        handler.setFormatter(formatter)
        return handler


def get_logger(name: str) -> logging.Logger:
    """
    获取日志器（便捷函数）

    Args:
        name: 日志器名称

    Returns:
        配置好的 Logger 实例

    Example:
        >>> logger = get_logger('my_module')
        >>> logger.info("操作成功")
    """
    return QCMLogger.get_logger(name)


def configure_logging(
    level: int = logging.INFO,
    format_type: str = 'default',
    output: str = 'console',
    file_path: Optional[str] = None
):
    """
    配置日志系统（便捷函数）

    Args:
        level: 日志级别
        format_type: 格式类型
        output: 输出目标
        file_path: 日志文件路径

    Example:
        >>> configure_logging(level=logging.DEBUG, format_type='json', output='both', file_path='logs/app.log')
    """
    QCMLogger.configure(
        level=level,
        format_type=format_type,
        output=output,
        file_path=file_path
    )


# 预定义的日志器
workflow_logger = get_logger('qcm_tools.workflow')
config_logger = get_logger('qcm_tools.config')
template_logger = get_logger('qcm_tools.template')
quality_logger = get_logger('qcm_tools.quality')
confidence_logger = get_logger('qcm_tools.confidence')
handoff_logger = get_logger('qcm_tools.handoff')
navigator_logger = get_logger('qcm_tools.navigator')


class LogContext:
    """
    日志上下文管理器

    用于记录函数执行时间和结果

    Example:
        >>> with LogContext('create_project', logger):
        ...     # 执行操作
        ...     pass
    """

    def __init__(
        self,
        operation: str,
        logger: logging.Logger,
        level: int = logging.INFO,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        self.operation = operation
        self.logger = logger
        self.level = level
        self.extra_data = extra_data or {}
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.log(
            self.level,
            f"开始执行: {self.operation}",
            extra={'extra_data': self.extra_data}
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()

        if exc_type is None:
            self.logger.log(
                self.level,
                f"完成执行: {self.operation} (耗时: {duration:.2f}s)",
                extra={'extra_data': {**self.extra_data, 'duration': duration}}
            )
        else:
            self.logger.error(
                f"执行失败: {self.operation} (耗时: {duration:.2f}s) - {exc_val}",
                extra={
                    'extra_data': {
                        **self.extra_data,
                        'duration': duration,
                        'error_type': exc_type.__name__
                    }
                },
                exc_info=True
            )

        return False  # 不抑制异常


def log_function_call(logger: logging.Logger, level: int = logging.DEBUG):
    """
    函数调用日志装饰器

    Args:
        logger: 日志器
        level: 日志级别

    Returns:
        装饰器函数

    Example:
        >>> @log_function_call(logger)
        ... def my_function(arg1, arg2):
        ...     return arg1 + arg2
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.log(
                level,
                f"调用函数: {func.__name__}(args={args}, kwargs={kwargs})"
            )
            try:
                result = func(*args, **kwargs)
                logger.log(level, f"函数返回: {func.__name__} -> {result}")
                return result
            except Exception as e:
                logger.error(
                    f"函数异常: {func.__name__} -> {e}",
                    exc_info=True
                )
                raise
        return wrapper
    return decorator
