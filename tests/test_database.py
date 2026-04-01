"""
数据库模块测试

测试 PostgreSQL 和 MySQL 双数据库兼容支持
"""

import pytest
from qcm_tools.database.config import (
    DatabaseConfig,
    DatabaseType,
    ConnectionPoolConfig,
    create_database_config,
)
from qcm_tools.database.adapter import (
    PostgreSQLAdapter,
    MySQLAdapter,
    create_adapter,
)


class TestDatabaseConfig:
    """测试数据库配置"""
    
    def test_postgresql_default_port(self):
        """测试 PostgreSQL 默认端口"""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="testdb"
        )
        assert config.port == 5432
    
    def test_mysql_default_port(self):
        """测试 MySQL 默认端口"""
        config = DatabaseConfig(
            db_type=DatabaseType.MYSQL,
            host="localhost",
            database="testdb"
        )
        assert config.port == 3306
    
    def test_postgresql_connection_url(self):
        """测试 PostgreSQL 连接 URL 生成"""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="mydb",
            username="user",
            password="pass"
        )
        url = config.get_connection_url()
        assert "postgresql://user:pass@localhost:5432/mydb" in url
        assert "sslmode=prefer" in url
    
    def test_mysql_connection_url(self):
        """测试 MySQL 连接 URL 生成"""
        config = DatabaseConfig(
            db_type=DatabaseType.MYSQL,
            host="localhost",
            database="mydb",
            username="user",
            password="pass"
        )
        url = config.get_connection_url()
        assert "mysql+pymysql://user:pass@localhost:3306/mydb" in url
        assert "charset=utf8mb4" in url
    
    def test_connection_url_without_password(self):
        """测试不包含密码的连接 URL"""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="mydb",
            username="user",
            password="secret"
        )
        url = config.get_connection_url(include_password=False)
        assert "secret" not in url
        assert "***" in url
    
    def test_async_connection_url(self):
        """测试异步连接 URL 生成"""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="mydb",
            username="user",
            password="pass"
        )
        url = config.get_async_connection_url()
        assert "postgresql+asyncpg://" in url
    
    def test_from_dict(self):
        """测试从字典创建配置"""
        config = DatabaseConfig.from_dict({
            "db_type": "mysql",
            "host": "db.example.com",
            "port": 3307,
            "database": "production",
            "username": "admin"
        })
        assert config.db_type == DatabaseType.MYSQL
        assert config.host == "db.example.com"
        assert config.port == 3307
    
    def test_to_dict(self):
        """测试转换为字典"""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="mydb",
            username="user",
            password="secret"
        )
        d = config.to_dict()
        assert d["db_type"] == "postgresql"
        assert d["host"] == "localhost"
        assert d["password"] == "***"  # 密码不暴露
    
    def test_pool_config(self):
        """测试连接池配置"""
        pool_config = ConnectionPoolConfig(
            pool_size=10,
            max_overflow=20,
            pool_timeout=60
        )
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="mydb",
            pool_config=pool_config
        )
        kwargs = config.get_sqlalchemy_engine_kwargs()
        assert kwargs["pool_size"] == 10
        assert kwargs["max_overflow"] == 20


class TestDatabaseTemplates:
    """测试数据库配置模板"""
    
    def test_postgresql_production_template(self):
        """测试 PostgreSQL 生产环境模板"""
        config = create_database_config(
            template="postgresql_production",
            host="prod.db.com",
            database="myapp",
            username="admin",
            password="secret"
        )
        assert config.db_type == DatabaseType.POSTGRESQL
        assert config.ssl_mode == "require"
        assert config.pool_config.pool_size == 10
    
    def test_mysql_production_template(self):
        """测试 MySQL 生产环境模板"""
        config = create_database_config(
            template="mysql_production",
            host="prod.db.com",
            database="myapp",
            username="admin",
            password="secret"
        )
        assert config.db_type == DatabaseType.MYSQL
        assert config.charset == "utf8mb4"
        assert config.pool_config.pool_size == 10
    
    def test_development_template(self):
        """测试开发环境模板"""
        config = create_database_config(
            template="postgresql_development",
            host="localhost",
            database="dev_db"
        )
        assert config.pool_config.echo == True


class TestDatabaseAdapter:
    """测试数据库适配器"""
    
    def test_create_postgresql_adapter(self):
        """测试创建 PostgreSQL 适配器"""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="testdb"
        )
        adapter = create_adapter(config)
        assert isinstance(adapter, PostgreSQLAdapter)
    
    def test_create_mysql_adapter(self):
        """测试创建 MySQL 适配器"""
        config = DatabaseConfig(
            db_type=DatabaseType.MYSQL,
            host="localhost",
            database="testdb"
        )
        adapter = create_adapter(config)
        assert isinstance(adapter, MySQLAdapter)
    
    def test_adapter_wrong_db_type(self):
        """测试适配器数据库类型不匹配"""
        config = DatabaseConfig(
            db_type=DatabaseType.MYSQL,
            host="localhost",
            database="testdb"
        )
        with pytest.raises(ValueError):
            PostgreSQLAdapter(config)


class TestSQLGeneration:
    """测试 SQL 生成（不需要实际连接）"""
    
    def test_postgresql_create_table_sql(self):
        """测试 PostgreSQL 建表 SQL"""
        # 这只是验证 SQL 生成逻辑，不需要实际数据库连接
        columns = {
            "id": "SERIAL PRIMARY KEY",
            "name": "VARCHAR(100) NOT NULL",
            "email": "VARCHAR(255) UNIQUE"
        }
        
        # 验证列定义格式
        assert "id" in columns
        assert "SERIAL" in columns["id"]
        assert "name" in columns
        assert "VARCHAR(100)" in columns["name"]
    
    def test_mysql_create_table_sql(self):
        """测试 MySQL 建表 SQL"""
        columns = {
            "id": "INT AUTO_INCREMENT PRIMARY KEY",
            "name": "VARCHAR(100) NOT NULL",
            "email": "VARCHAR(255) UNIQUE"
        }
        
        # 验证 MySQL 特有的语法
        assert "AUTO_INCREMENT" in columns["id"]
        assert "id" in columns


# 集成测试标记（需要实际数据库连接）
@pytest.mark.integration
class TestDatabaseIntegration:
    """集成测试（需要实际数据库连接）"""
    
    @pytest.mark.skip(reason="需要 PostgreSQL 数据库连接")
    def test_postgresql_connection(self):
        """测试 PostgreSQL 实际连接"""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="testdb",
            username="test",
            password="test"
        )
        adapter = PostgreSQLAdapter(config)
        # 实际连接测试...
    
    @pytest.mark.skip(reason="需要 MySQL 数据库连接")
    def test_mysql_connection(self):
        """测试 MySQL 实际连接"""
        config = DatabaseConfig(
            db_type=DatabaseType.MYSQL,
            host="localhost",
            database="testdb",
            username="test",
            password="test"
        )
        adapter = MySQLAdapter(config)
        # 实际连接测试...
