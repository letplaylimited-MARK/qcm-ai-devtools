"""
数据库连接器模块

提供 PostgreSQL 和 MySQL 统一的数据库连接管理
"""

from typing import Optional, Dict, Any, List, Union
from contextlib import contextmanager
import logging

from qcm_tools.database.config import DatabaseConfig, DatabaseType

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """
    数据库连接器
    
    提供 PostgreSQL 和 MySQL 的统一连接管理，
    支持同步和异步两种连接方式。
    
    Example:
        >>> config = DatabaseConfig(
        ...     db_type=DatabaseType.POSTGRESQL,
        ...     host="localhost",
        ...     database="mydb",
        ...     username="user",
        ...     password="pass"
        ... )
        >>> connector = DatabaseConnector(config)
        >>> 
        >>> # 使用上下文管理器
        >>> with connector.get_connection() as conn:
        ...     result = conn.execute("SELECT * FROM users")
        ...     for row in result:
        ...         print(row)
    """
    
    def __init__(self, config: DatabaseConfig):
        """
        初始化数据库连接器
        
        Args:
            config: 数据库配置对象
        """
        self.config = config
        self._engine = None
        self._session_factory = None
        self._initialized = False
    
    def initialize(self) -> None:
        """
        初始化数据库连接
        
        创建连接池和会话工厂
        """
        if self._initialized:
            return
        
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            
            kwargs = self.config.get_sqlalchemy_engine_kwargs()
            self._engine = create_engine(**kwargs)
            self._session_factory = sessionmaker(bind=self._engine)
            self._initialized = True
            
            logger.info(
                f"数据库连接初始化成功: {self.config.db_type.value} "
                f"@ {self.config.host}:{self.config.port}/{self.config.database}"
            )
        except ImportError:
            logger.warning("SQLAlchemy 未安装，部分功能将不可用")
            self._initialized = False
    
    def get_connection(self):
        """
        获取数据库连接
        
        Returns:
            数据库连接对象
            
        Example:
            >>> with connector.get_connection() as conn:
            ...     conn.execute("INSERT INTO users (name) VALUES ('test')")
        """
        if not self._initialized:
            self.initialize()
        
        return self._engine.connect()
    
    @contextmanager
    def get_session(self):
        """
        获取数据库会话（上下文管理器）
        
        Yields:
            SQLAlchemy Session 对象
            
        Example:
            >>> with connector.get_session() as session:
            ...     user = User(name="test")
            ...     session.add(user)
            ...     session.commit()
        """
        if not self._initialized:
            self.initialize()
        
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库会话错误: {e}")
            raise
        finally:
            session.close()
    
    def execute(self, sql: str, params: Dict[str, Any] = None) -> List[tuple]:
        """
        执行 SQL 语句
        
        Args:
            sql: SQL 语句
            params: 参数字典
            
        Returns:
            查询结果列表
            
        Example:
            >>> results = connector.execute(
            ...     "SELECT * FROM users WHERE age > :age",
            ...     {"age": 18}
            ... )
        """
        with self.get_connection() as conn:
            result = conn.execute(sql, params or {})
            return result.fetchall() if result.returns_rows else []
    
    def execute_many(self, sql: str, params_list: List[Dict[str, Any]]) -> int:
        """
        批量执行 SQL 语句
        
        Args:
            sql: SQL 语句
            params_list: 参数列表
            
        Returns:
            影响的行数
            
        Example:
            >>> rows = connector.execute_many(
            ...     "INSERT INTO users (name, age) VALUES (:name, :age)",
            ...     [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
            ... )
        """
        with self.get_connection() as conn:
            result = conn.execute(sql, params_list)
            return result.rowcount
    
    def test_connection(self) -> bool:
        """
        测试数据库连接
        
        Returns:
            连接是否成功
            
        Example:
            >>> if connector.test_connection():
            ...     print("数据库连接正常")
        """
        try:
            with self.get_connection() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        获取数据库信息
        
        Returns:
            数据库信息字典
        """
        info = {
            "type": self.config.db_type.value,
            "host": self.config.host,
            "port": self.config.port,
            "database": self.config.database,
            "connected": self.test_connection(),
        }
        
        if self.config.db_type == DatabaseType.POSTGRESQL:
            info.update(self._get_postgresql_info())
        elif self.config.db_type == DatabaseType.MYSQL:
            info.update(self._get_mysql_info())
        
        return info
    
    def _get_postgresql_info(self) -> Dict[str, Any]:
        """获取 PostgreSQL 特定信息"""
        try:
            with self.get_connection() as conn:
                version_result = conn.execute("SELECT version()")
                version = version_result.fetchone()[0]
                return {
                    "server_version": version,
                    "features": ["JSON", "JSONB", "ARRAY", "UUID", "FULL_TEXT_SEARCH"]
                }
        except Exception:
            return {}
    
    def _get_mysql_info(self) -> Dict[str, Any]:
        """获取 MySQL 特定信息"""
        try:
            with self.get_connection() as conn:
                version_result = conn.execute("SELECT VERSION()")
                version = version_result.fetchone()[0]
                return {
                    "server_version": version,
                    "features": ["JSON", "FULL_TEXT_SEARCH"]
                }
        except Exception:
            return {}
    
    def close(self) -> None:
        """
        关闭数据库连接
        
        释放连接池资源
        """
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None
            self._initialized = False
            logger.info("数据库连接已关闭")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
        return False


class AsyncDatabaseConnector:
    """
    异步数据库连接器
    
    提供异步的数据库连接管理
    
    Example:
        >>> config = DatabaseConfig(
        ...     db_type=DatabaseType.POSTGRESQL,
        ...     host="localhost",
        ...     database="mydb"
        ... )
        >>> connector = AsyncDatabaseConnector(config)
        >>> 
        >>> async with connector.get_session() as session:
        ...     result = await session.execute("SELECT * FROM users")
        ...     users = result.fetchall()
    """
    
    def __init__(self, config: DatabaseConfig):
        """
        初始化异步数据库连接器
        
        Args:
            config: 数据库配置对象
        """
        self.config = config
        self._engine = None
        self._session_factory = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """初始化异步数据库连接"""
        if self._initialized:
            return
        
        try:
            from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
            
            url = self.config.get_async_connection_url()
            self._engine = create_async_engine(
                url,
                pool_size=self.config.pool_config.pool_size,
                max_overflow=self.config.pool_config.max_overflow,
                echo=self.config.pool_config.echo,
            )
            self._session_factory = async_sessionmaker(self._engine)
            self._initialized = True
            
            logger.info(f"异步数据库连接初始化成功: {self.config.db_type.value}")
        except ImportError:
            logger.warning("SQLAlchemy 异步支持未安装")
    
    async def get_session(self):
        """获取异步会话"""
        if not self._initialized:
            await self.initialize()
        return self._session_factory()
    
    async def close(self) -> None:
        """关闭异步连接"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._initialized = False


__all__ = [
    'DatabaseConnector',
    'AsyncDatabaseConnector',
]
