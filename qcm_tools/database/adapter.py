"""
数据库适配器模块

提供 PostgreSQL 和 MySQL 的数据库操作适配器，
实现统一的数据库操作接口
"""

from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
import logging

from qcm_tools.database.config import DatabaseConfig, DatabaseType
from qcm_tools.database.connector import DatabaseConnector

logger = logging.getLogger(__name__)


class DatabaseAdapter(ABC):
    """
    数据库适配器抽象基类
    
    定义统一的数据库操作接口
    """
    
    @abstractmethod
    def create_table(self, table_name: str, columns: Dict[str, str], **options) -> bool:
        """创建表"""
        pass
    
    @abstractmethod
    def drop_table(self, table_name: str, if_exists: bool = True) -> bool:
        """删除表"""
        pass
    
    @abstractmethod
    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        """插入数据"""
        pass
    
    @abstractmethod
    def insert_many(self, table_name: str, data_list: List[Dict[str, Any]]) -> int:
        """批量插入数据"""
        pass
    
    @abstractmethod
    def select(self, table_name: str, columns: List[str] = None, 
               where: Dict[str, Any] = None, limit: int = None) -> List[Dict[str, Any]]:
        """查询数据"""
        pass
    
    @abstractmethod
    def update(self, table_name: str, data: Dict[str, Any], 
               where: Dict[str, Any]) -> int:
        """更新数据"""
        pass
    
    @abstractmethod
    def delete(self, table_name: str, where: Dict[str, Any]) -> int:
        """删除数据"""
        pass
    
    @abstractmethod
    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        pass
    
    @abstractmethod
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """获取表结构"""
        pass


class PostgreSQLAdapter(DatabaseAdapter):
    """
    PostgreSQL 数据库适配器
    
    实现 PostgreSQL 特定的数据库操作
    
    Example:
        >>> config = DatabaseConfig(
        ...     db_type=DatabaseType.POSTGRESQL,
        ...     host="localhost",
        ...     database="mydb"
        ... )
        >>> adapter = PostgreSQLAdapter(config)
        >>> adapter.create_table("users", {"id": "SERIAL PRIMARY KEY", "name": "VARCHAR(100)"})
    """
    
    def __init__(self, config: DatabaseConfig):
        if config.db_type != DatabaseType.POSTGRESQL:
            raise ValueError("PostgreSQLAdapter 只支持 PostgreSQL 数据库")
        self.config = config
        self.connector = DatabaseConnector(config)
    
    def create_table(self, table_name: str, columns: Dict[str, str], 
                     primary_key: str = None, **options) -> bool:
        """
        创建 PostgreSQL 表
        
        Args:
            table_name: 表名
            columns: 列定义字典，key 为列名，value 为数据类型
            primary_key: 主键列名
            **options: 额外选项（如 IF NOT EXISTS）
            
        Returns:
            是否成功
        """
        if_not_exists = "IF NOT EXISTS" if options.get("if_not_exists", True) else ""
        
        columns_def = []
        for col_name, col_type in columns.items():
            columns_def.append(f"{col_name} {col_type}")
        
        if primary_key:
            columns_def.append(f"PRIMARY KEY ({primary_key})")
        
        sql = f"CREATE TABLE {if_not_exists} {table_name} ({', '.join(columns_def)})"
        
        try:
            self.connector.execute(sql)
            logger.info(f"PostgreSQL 表创建成功: {table_name}")
            return True
        except Exception as e:
            logger.error(f"创建表失败: {e}")
            return False
    
    def drop_table(self, table_name: str, if_exists: bool = True, 
                   cascade: bool = False) -> bool:
        """删除 PostgreSQL 表"""
        if_exists_clause = "IF EXISTS" if if_exists else ""
        cascade_clause = "CASCADE" if cascade else ""
        
        sql = f"DROP TABLE {if_exists_clause} {table_name} {cascade_clause}"
        
        try:
            self.connector.execute(sql)
            return True
        except Exception as e:
            logger.error(f"删除表失败: {e}")
            return False
    
    def insert(self, table_name: str, data: Dict[str, Any], 
               returning: str = None) -> Union[int, Dict[str, Any]]:
        """
        插入数据到 PostgreSQL
        
        Args:
            table_name: 表名
            data: 数据字典
            returning: RETURNING 子句的列名
            
        Returns:
            插入的行 ID 或返回的数据
        """
        columns = list(data.keys())
        placeholders = [f":{col}" for col in columns]
        
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        
        if returning:
            sql += f" RETURNING {returning}"
        
        with self.connector.get_connection() as conn:
            result = conn.execute(sql, data)
            if returning:
                row = result.fetchone()
                return dict(row._mapping) if row else None
            return result.rowcount
    
    def insert_many(self, table_name: str, data_list: List[Dict[str, Any]]) -> int:
        """批量插入数据到 PostgreSQL"""
        if not data_list:
            return 0
        
        columns = list(data_list[0].keys())
        placeholders = [f":{col}" for col in columns]
        
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        
        return self.connector.execute_many(sql, data_list)
    
    def select(self, table_name: str, columns: List[str] = None,
               where: Dict[str, Any] = None, order_by: str = None,
               limit: int = None, offset: int = None) -> List[Dict[str, Any]]:
        """
        从 PostgreSQL 查询数据
        
        Args:
            table_name: 表名
            columns: 要查询的列名列表
            where: WHERE 条件字典
            order_by: 排序字段
            limit: 限制返回行数
            offset: 偏移量
            
        Returns:
            查询结果列表
        """
        cols = ", ".join(columns) if columns else "*"
        sql = f"SELECT {cols} FROM {table_name}"
        
        params = {}
        if where:
            conditions = []
            for key, value in where.items():
                conditions.append(f"{key} = :{key}")
                params[key] = value
            sql += " WHERE " + " AND ".join(conditions)
        
        if order_by:
            sql += f" ORDER BY {order_by}"
        
        if limit:
            sql += f" LIMIT {limit}"
        
        if offset:
            sql += f" OFFSET {offset}"
        
        with self.connector.get_connection() as conn:
            result = conn.execute(sql, params)
            return [dict(row._mapping) for row in result.fetchall()]
    
    def update(self, table_name: str, data: Dict[str, Any], 
               where: Dict[str, Any]) -> int:
        """更新 PostgreSQL 数据"""
        set_clause = ", ".join([f"{k} = :set_{k}" for k in data.keys()])
        where_clause = " AND ".join([f"{k} = :where_{k}" for k in where.keys()])
        
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        
        params = {f"set_{k}": v for k, v in data.items()}
        params.update({f"where_{k}": v for k, v in where.items()})
        
        return self.connector.execute(sql, params)
    
    def delete(self, table_name: str, where: Dict[str, Any]) -> int:
        """删除 PostgreSQL 数据"""
        where_clause = " AND ".join([f"{k} = :{k}" for k in where.keys()])
        sql = f"DELETE FROM {table_name} WHERE {where_clause}"
        
        return self.connector.execute(sql, where)
    
    def table_exists(self, table_name: str) -> bool:
        """检查 PostgreSQL 表是否存在"""
        sql = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = :table_name
            )
        """
        with self.connector.get_connection() as conn:
            result = conn.execute(sql, {"table_name": table_name})
            return result.fetchone()[0]
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """获取 PostgreSQL 表结构"""
        sql = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = :table_name
            ORDER BY ordinal_position
        """
        with self.connector.get_connection() as conn:
            result = conn.execute(sql, {"table_name": table_name})
            return {
                row["column_name"]: {
                    "type": row["data_type"],
                    "nullable": row["is_nullable"] == "YES",
                    "default": row["column_default"]
                }
                for row in [dict(r._mapping) for r in result.fetchall()]
            }
    
    def upsert(self, table_name: str, data: Dict[str, Any], 
               conflict_columns: List[str]) -> int:
        """
        PostgreSQL UPSERT 操作（INSERT ON CONFLICT UPDATE）
        
        Args:
            table_name: 表名
            data: 数据字典
            conflict_columns: 冲突检测列
            
        Returns:
            影响的行数
        """
        columns = list(data.keys())
        placeholders = [f":{col}" for col in columns]
        update_clause = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns])
        
        sql = f"""
            INSERT INTO {table_name} ({', '.join(columns)}) 
            VALUES ({', '.join(placeholders)})
            ON CONFLICT ({', '.join(conflict_columns)})
            DO UPDATE SET {update_clause}
        """
        
        return self.connector.execute(sql, data)


class MySQLAdapter(DatabaseAdapter):
    """
    MySQL 数据库适配器
    
    实现 MySQL 特定的数据库操作
    
    Example:
        >>> config = DatabaseConfig(
        ...     db_type=DatabaseType.MYSQL,
        ...     host="localhost",
        ...     database="mydb"
        ... )
        >>> adapter = MySQLAdapter(config)
        >>> adapter.create_table("users", {"id": "INT AUTO_INCREMENT PRIMARY KEY", "name": "VARCHAR(100)"})
    """
    
    def __init__(self, config: DatabaseConfig):
        if config.db_type != DatabaseType.MYSQL:
            raise ValueError("MySQLAdapter 只支持 MySQL 数据库")
        self.config = config
        self.connector = DatabaseConnector(config)
    
    def create_table(self, table_name: str, columns: Dict[str, str],
                     primary_key: str = None, engine: str = "InnoDB",
                     charset: str = "utf8mb4", **options) -> bool:
        """
        创建 MySQL 表
        
        Args:
            table_name: 表名
            columns: 列定义字典
            primary_key: 主键列名
            engine: 存储引擎
            charset: 字符集
            
        Returns:
            是否成功
        """
        if_not_exists = "IF NOT EXISTS" if options.get("if_not_exists", True) else ""
        
        columns_def = []
        for col_name, col_type in columns.items():
            columns_def.append(f"{col_name} {col_type}")
        
        if primary_key:
            columns_def.append(f"PRIMARY KEY ({primary_key})")
        
        sql = f"""
            CREATE TABLE {if_not_exists} {table_name} (
                {', '.join(columns_def)}
            ) ENGINE={engine} DEFAULT CHARSET={charset}
        """
        
        try:
            self.connector.execute(sql)
            logger.info(f"MySQL 表创建成功: {table_name}")
            return True
        except Exception as e:
            logger.error(f"创建表失败: {e}")
            return False
    
    def drop_table(self, table_name: str, if_exists: bool = True) -> bool:
        """删除 MySQL 表"""
        if_exists_clause = "IF EXISTS" if if_exists else ""
        sql = f"DROP TABLE {if_exists_clause} {table_name}"
        
        try:
            self.connector.execute(sql)
            return True
        except Exception as e:
            logger.error(f"删除表失败: {e}")
            return False
    
    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        """插入数据到 MySQL"""
        columns = list(data.keys())
        placeholders = [f":{col}" for col in columns]
        
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        
        with self.connector.get_connection() as conn:
            result = conn.execute(sql, data)
            return result.lastrowid
    
    def insert_many(self, table_name: str, data_list: List[Dict[str, Any]]) -> int:
        """批量插入数据到 MySQL"""
        if not data_list:
            return 0
        
        columns = list(data_list[0].keys())
        placeholders = [f":{col}" for col in columns]
        
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        
        return self.connector.execute_many(sql, data_list)
    
    def select(self, table_name: str, columns: List[str] = None,
               where: Dict[str, Any] = None, order_by: str = None,
               limit: int = None, offset: int = None) -> List[Dict[str, Any]]:
        """从 MySQL 查询数据"""
        cols = ", ".join(columns) if columns else "*"
        sql = f"SELECT {cols} FROM {table_name}"
        
        params = {}
        if where:
            conditions = []
            for key, value in where.items():
                conditions.append(f"{key} = :{key}")
                params[key] = value
            sql += " WHERE " + " AND ".join(conditions)
        
        if order_by:
            sql += f" ORDER BY {order_by}"
        
        if limit:
            sql += f" LIMIT {limit}"
        
        if offset:
            sql += f" OFFSET {offset}"
        
        with self.connector.get_connection() as conn:
            result = conn.execute(sql, params)
            return [dict(row._mapping) for row in result.fetchall()]
    
    def update(self, table_name: str, data: Dict[str, Any],
               where: Dict[str, Any]) -> int:
        """更新 MySQL 数据"""
        set_clause = ", ".join([f"{k} = :set_{k}" for k in data.keys()])
        where_clause = " AND ".join([f"{k} = :where_{k}" for k in where.keys()])
        
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        
        params = {f"set_{k}": v for k, v in data.items()}
        params.update({f"where_{k}": v for k, v in where.items()})
        
        return self.connector.execute(sql, params)
    
    def delete(self, table_name: str, where: Dict[str, Any]) -> int:
        """删除 MySQL 数据"""
        where_clause = " AND ".join([f"{k} = :{k}" for k in where.keys()])
        sql = f"DELETE FROM {table_name} WHERE {where_clause}"
        
        return self.connector.execute(sql, where)
    
    def table_exists(self, table_name: str) -> bool:
        """检查 MySQL 表是否存在"""
        sql = """
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = DATABASE() AND table_name = :table_name
        """
        with self.connector.get_connection() as conn:
            result = conn.execute(sql, {"table_name": table_name})
            return result.fetchone()[0] > 0
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """获取 MySQL 表结构"""
        sql = f"DESCRIBE {table_name}"
        with self.connector.get_connection() as conn:
            result = conn.execute(sql)
            return {
                row["Field"]: {
                    "type": row["Type"],
                    "nullable": row["Null"] == "YES",
                    "default": row["Default"],
                    "key": row["Key"]
                }
                for row in [dict(r._mapping) for r in result.fetchall()]
            }
    
    def upsert(self, table_name: str, data: Dict[str, Any],
               duplicate_columns: List[str]) -> int:
        """
        MySQL UPSERT 操作（INSERT ON DUPLICATE KEY UPDATE）
        
        Args:
            table_name: 表名
            data: 数据字典
            duplicate_columns: 重复时更新的列
            
        Returns:
            影响的行数
        """
        columns = list(data.keys())
        placeholders = [f":{col}" for col in columns]
        update_clause = ", ".join([f"{col} = VALUES({col})" for col in duplicate_columns])
        
        sql = f"""
            INSERT INTO {table_name} ({', '.join(columns)}) 
            VALUES ({', '.join(placeholders)})
            ON DUPLICATE KEY UPDATE {update_clause}
        """
        
        return self.connector.execute(sql, data)


def create_adapter(config: DatabaseConfig) -> DatabaseAdapter:
    """
    创建数据库适配器的工厂函数
    
    Args:
        config: 数据库配置
        
    Returns:
        对应类型的数据库适配器
        
    Example:
        >>> config = DatabaseConfig(
        ...     db_type=DatabaseType.POSTGRESQL,
        ...     host="localhost",
        ...     database="mydb"
        ... )
        >>> adapter = create_adapter(config)
    """
    if config.db_type == DatabaseType.POSTGRESQL:
        return PostgreSQLAdapter(config)
    elif config.db_type == DatabaseType.MYSQL:
        return MySQLAdapter(config)
    else:
        raise ValueError(f"不支持的数据库类型: {config.db_type}")


__all__ = [
    'DatabaseAdapter',
    'PostgreSQLAdapter',
    'MySQLAdapter',
    'create_adapter',
]
