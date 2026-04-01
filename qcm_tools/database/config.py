"""
数据库配置模块

支持 PostgreSQL 和 MySQL 双数据库配置
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


class DatabaseType(Enum):
    """
    支持的数据库类型枚举
    
    Attributes:
        POSTGRESQL: PostgreSQL 数据库
        MYSQL: MySQL 数据库
        SQLITE: SQLite 数据库（用于开发测试）
    """
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"


@dataclass
class ConnectionPoolConfig:
    """
    数据库连接池配置
    
    Attributes:
        pool_size: 连接池大小
        max_overflow: 最大溢出连接数
        pool_timeout: 获取连接超时时间（秒）
        pool_recycle: 连接回收时间（秒）
        echo: 是否打印 SQL 语句
    """
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False


@dataclass
class DatabaseConfig:
    """
    数据库配置类
    
    支持 PostgreSQL 和 MySQL 双数据库配置，
    提供统一的配置接口和连接字符串生成。
    
    Attributes:
        db_type: 数据库类型
        host: 主机地址
        port: 端口号
        database: 数据库名
        username: 用户名
        password: 密码
        pool_config: 连接池配置
        ssl_mode: SSL 模式
        charset: 字符集（MySQL 适用）
        
    Example:
        >>> # PostgreSQL 配置
        >>> pg_config = DatabaseConfig(
        ...     db_type=DatabaseType.POSTGRESQL,
        ...     host="localhost",
        ...     database="mydb",
        ...     username="user",
        ...     password="pass"
        ... )
        >>> print(pg_config.get_connection_url())
        postgresql://user:pass@localhost:5432/mydb
        
        >>> # MySQL 配置
        >>> mysql_config = DatabaseConfig(
        ...     db_type=DatabaseType.MYSQL,
        ...     host="localhost",
        ...     database="mydb",
        ...     username="user",
        ...     password="pass",
        ...     charset="utf8mb4"
        ... )
        >>> print(mysql_config.get_connection_url())
        mysql+pymysql://user:pass@localhost:3306/mydb?charset=utf8mb4
    """
    
    db_type: DatabaseType
    host: str = "localhost"
    port: Optional[int] = None  # None 时使用默认端口
    database: str = ""
    username: str = ""
    password: str = ""
    pool_config: ConnectionPoolConfig = field(default_factory=ConnectionPoolConfig)
    ssl_mode: str = "prefer"
    charset: str = "utf8mb4"  # MySQL 默认字符集
    
    # 额外参数
    extra_params: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理，设置默认端口"""
        if self.port is None:
            self.port = self._get_default_port()
    
    def _get_default_port(self) -> int:
        """获取数据库默认端口"""
        default_ports = {
            DatabaseType.POSTGRESQL: 5432,
            DatabaseType.MYSQL: 3306,
            DatabaseType.SQLITE: 0,  # SQLite 不使用端口
        }
        return default_ports.get(self.db_type, 5432)
    
    def get_connection_url(self, include_password: bool = True) -> str:
        """
        生成数据库连接 URL
        
        Args:
            include_password: 是否包含密码
            
        Returns:
            数据库连接 URL 字符串
            
        Example:
            >>> config = DatabaseConfig(
            ...     db_type=DatabaseType.POSTGRESQL,
            ...     host="localhost",
            ...     database="mydb",
            ...     username="user",
            ...     password="secret"
            ... )
            >>> config.get_connection_url()
            'postgresql://user:secret@localhost:5432/mydb'
            >>> config.get_connection_url(include_password=False)
            'postgresql://user:***@localhost:5432/mydb'
        """
        password_part = f":{self.password}" if include_password else ":***"
        
        if self.db_type == DatabaseType.POSTGRESQL:
            return self._build_postgresql_url(password_part)
        elif self.db_type == DatabaseType.MYSQL:
            return self._build_mysql_url(password_part)
        elif self.db_type == DatabaseType.SQLITE:
            return f"sqlite:///{self.database}"
        else:
            raise ValueError(f"不支持的数据库类型: {self.db_type}")
    
    def _build_postgresql_url(self, password_part: str) -> str:
        """构建 PostgreSQL 连接 URL"""
        base_url = f"postgresql://{self.username}{password_part}@{self.host}:{self.port}/{self.database}"
        
        # 添加 SSL 参数
        params = {"sslmode": self.ssl_mode}
        params.update(self.extra_params)
        
        if params:
            param_str = "&".join(f"{k}={v}" for k, v in params.items())
            base_url += f"?{param_str}"
        
        return base_url
    
    def _build_mysql_url(self, password_part: str) -> str:
        """构建 MySQL 连接 URL"""
        base_url = f"mysql+pymysql://{self.username}{password_part}@{self.host}:{self.port}/{self.database}"
        
        # 添加字符集和其他参数
        params = {"charset": self.charset}
        params.update(self.extra_params)
        
        param_str = "&".join(f"{k}={v}" for k, v in params.items())
        base_url += f"?{param_str}"
        
        return base_url
    
    def get_async_connection_url(self) -> str:
        """
        生成异步数据库连接 URL
        
        Returns:
            异步数据库连接 URL
            
        Example:
            >>> config = DatabaseConfig(
            ...     db_type=DatabaseType.POSTGRESQL,
            ...     host="localhost",
            ...     database="mydb",
            ...     username="user",
            ...     password="secret"
            ... )
            >>> config.get_async_connection_url()
            'postgresql+asyncpg://user:secret@localhost:5432/mydb'
        """
        if self.db_type == DatabaseType.POSTGRESQL:
            return self.get_connection_url().replace(
                "postgresql://", "postgresql+asyncpg://"
            )
        elif self.db_type == DatabaseType.MYSQL:
            return self.get_connection_url().replace(
                "mysql+pymysql://", "mysql+aiomysql://"
            )
        else:
            return self.get_connection_url()
    
    def get_sqlalchemy_engine_kwargs(self) -> Dict[str, Any]:
        """
        获取 SQLAlchemy Engine 创建参数
        
        Returns:
            SQLAlchemy Engine 参数字典
        """
        kwargs = {
            "url": self.get_connection_url(),
            "pool_size": self.pool_config.pool_size,
            "max_overflow": self.pool_config.max_overflow,
            "pool_timeout": self.pool_config.pool_timeout,
            "pool_recycle": self.pool_config.pool_recycle,
            "echo": self.pool_config.echo,
        }
        return kwargs
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "DatabaseConfig":
        """
        从字典创建配置对象
        
        Args:
            config_dict: 配置字典
            
        Returns:
            DatabaseConfig 实例
            
        Example:
            >>> config = DatabaseConfig.from_dict({
            ...     "db_type": "postgresql",
            ...     "host": "localhost",
            ...     "database": "mydb",
            ...     "username": "user",
            ...     "password": "pass"
            ... })
        """
        db_type_str = config_dict.pop("db_type", "postgresql")
        db_type = DatabaseType(db_type_str.lower())
        
        pool_dict = config_dict.pop("pool_config", {})
        pool_config = ConnectionPoolConfig(**pool_dict) if pool_dict else ConnectionPoolConfig()
        
        return cls(
            db_type=db_type,
            pool_config=pool_config,
            **config_dict
        )
    
    @classmethod
    def from_env(cls, prefix: str = "DB") -> "DatabaseConfig":
        """
        从环境变量创建配置对象
        
        Args:
            prefix: 环境变量前缀，默认为 "DB"
            
        Returns:
            DatabaseConfig 实例
            
        环境变量:
            DB_TYPE: 数据库类型 (postgresql/mysql)
            DB_HOST: 主机地址
            DB_PORT: 端口号
            DB_DATABASE: 数据库名
            DB_USERNAME: 用户名
            DB_PASSWORD: 密码
            
        Example:
            >>> import os
            >>> os.environ["DB_TYPE"] = "postgresql"
            >>> os.environ["DB_HOST"] = "localhost"
            >>> os.environ["DB_DATABASE"] = "mydb"
            >>> config = DatabaseConfig.from_env()
        """
        import os
        
        db_type_str = os.getenv(f"{prefix}_TYPE", "postgresql")
        db_type = DatabaseType(db_type_str.lower())
        
        return cls(
            db_type=db_type,
            host=os.getenv(f"{prefix}_HOST", "localhost"),
            port=int(os.getenv(f"{prefix}_PORT", "0")) or None,
            database=os.getenv(f"{prefix}_DATABASE", ""),
            username=os.getenv(f"{prefix}_USERNAME", ""),
            password=os.getenv(f"{prefix}_PASSWORD", ""),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            配置字典
        """
        return {
            "db_type": self.db_type.value,
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "username": self.username,
            "password": "***",  # 不暴露密码
            "ssl_mode": self.ssl_mode,
            "charset": self.charset,
            "pool_config": {
                "pool_size": self.pool_config.pool_size,
                "max_overflow": self.pool_config.max_overflow,
                "pool_timeout": self.pool_config.pool_timeout,
                "pool_recycle": self.pool_config.pool_recycle,
                "echo": self.pool_config.echo,
            }
        }


@dataclass
class DatabaseMigrationConfig:
    """
    数据库迁移配置
    
    Attributes:
        migration_dir: 迁移脚本目录
        version_table: 版本控制表名
        auto_migrate: 是否自动执行迁移
    """
    migration_dir: str = "migrations"
    version_table: str = "schema_version"
    auto_migrate: bool = False


# 预定义的数据库模板配置
DATABASE_TEMPLATES = {
    "postgresql_production": {
        "db_type": DatabaseType.POSTGRESQL,
        "ssl_mode": "require",
        "pool_size": 10,
        "max_overflow": 20,
    },
    "postgresql_development": {
        "db_type": DatabaseType.POSTGRESQL,
        "ssl_mode": "prefer",
        "pool_size": 5,
        "echo": True,
    },
    "mysql_production": {
        "db_type": DatabaseType.MYSQL,
        "charset": "utf8mb4",
        "pool_size": 10,
        "max_overflow": 20,
    },
    "mysql_development": {
        "db_type": DatabaseType.MYSQL,
        "charset": "utf8mb4",
        "pool_size": 5,
        "echo": True,
    },
}


def create_database_config(
    db_type: str = "postgresql",
    template: Optional[str] = None,
    **kwargs
) -> DatabaseConfig:
    """
    创建数据库配置的便捷函数
    
    Args:
        db_type: 数据库类型
        template: 配置模板名称
        **kwargs: 其他配置参数
        
    Returns:
        DatabaseConfig 实例
        
    Example:
        >>> # 使用模板
        >>> config = create_database_config(
        ...     template="postgresql_production",
        ...     host="db.example.com",
        ...     database="myapp",
        ...     username="admin",
        ...     password="secret"
        ... )
        
        >>> # 不使用模板
        >>> config = create_database_config(
        ...     db_type="mysql",
        ...     host="localhost",
        ...     database="mydb",
        ...     username="root",
        ...     password=""
        ... )
    """
    if template and template in DATABASE_TEMPLATES:
        template_config = DATABASE_TEMPLATES[template].copy()
        
        # 提取连接池配置
        pool_size = template_config.pop("pool_size", 5)
        max_overflow = template_config.pop("max_overflow", 10)
        echo = template_config.pop("echo", False)
        
        # 创建连接池配置
        pool_config = ConnectionPoolConfig(
            pool_size=pool_size,
            max_overflow=max_overflow,
            echo=echo
        )
        
        # 合并用户参数
        template_config.update(kwargs)
        template_config["db_type"] = template_config.get("db_type", DatabaseType(db_type))
        if isinstance(template_config["db_type"], str):
            template_config["db_type"] = DatabaseType(template_config["db_type"])
        
        # 设置连接池配置
        if "pool_config" not in template_config:
            template_config["pool_config"] = pool_config
        
        return DatabaseConfig(**template_config)
    
    return DatabaseConfig(db_type=DatabaseType(db_type), **kwargs)


__all__ = [
    'DatabaseType',
    'ConnectionPoolConfig',
    'DatabaseConfig',
    'DatabaseMigrationConfig',
    'DATABASE_TEMPLATES',
    'create_database_config',
]
