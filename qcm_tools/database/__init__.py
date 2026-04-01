"""
数据库配置模块

提供 PostgreSQL 和 MySQL 双数据库兼容支持
"""

from qcm_tools.database.config import (
    DatabaseConfig,
    DatabaseType,
    ConnectionPoolConfig,
    create_database_config,
)
from qcm_tools.database.connector import DatabaseConnector, AsyncDatabaseConnector
from qcm_tools.database.adapter import DatabaseAdapter, PostgreSQLAdapter, MySQLAdapter, create_adapter

__all__ = [
    'DatabaseConfig',
    'DatabaseType',
    'ConnectionPoolConfig',
    'create_database_config',
    'DatabaseConnector',
    'AsyncDatabaseConnector',
    'DatabaseAdapter',
    'PostgreSQLAdapter',
    'MySQLAdapter',
    'create_adapter',
]
