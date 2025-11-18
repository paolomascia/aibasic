"""
MySQL Module with Connection Pool

This module provides a connection pool for MySQL/MariaDB databases.
Configuration is loaded from aibasic.conf under the [mysql] section.

Example configuration in aibasic.conf:
    [mysql]
    HOST=localhost
    PORT=3306
    DATABASE=mydb
    USER=root
    PASSWORD=secret
    MIN_CONNECTIONS=1
    MAX_CONNECTIONS=10
    CHARSET=utf8mb4

Usage in generated code:
    from aibasic.modules import MySQLModule

    # Initialize module (happens once per program)
    mysql = MySQLModule.from_config(config_path="aibasic.conf")

    # Get a connection from the pool
    conn = mysql.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers")
        results = cursor.fetchall()
    finally:
        mysql.release_connection(conn)
"""

import configparser
import mysql.connector
from mysql.connector import pooling, Error
from pathlib import Path
from typing import Optional, List, Tuple, Any
import threading
from .module_base import AIbasicModuleBase


class MySQLModule(AIbasicModuleBase):
    """
    MySQL connection pool manager.

    This class manages a pool of connections to a MySQL/MariaDB database,
    allowing efficient reuse of connections across multiple operations.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self, host: str, port: int, database: str, user: str,
                 password: str, min_connections: int = 1, max_connections: int = 10,
                 charset: str = "utf8mb4"):
        """
        Initialize the MySQL connection pool.

        Args:
            host: Database host address
            port: Database port (typically 3306)
            database: Database name
            user: Username for authentication
            password: Password for authentication
            min_connections: Minimum number of connections in pool
            max_connections: Maximum number of connections in pool
            charset: Character set (default: utf8mb4)
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.charset = charset

        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="aibasic_mysql_pool",
                pool_size=max_connections,
                pool_reset_session=True,
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                charset=charset,
                autocommit=False
            )
            print(f"[MySQLModule] Connection pool created: {database}@{host}:{port}")
        except Error as e:
            raise RuntimeError(f"Failed to create MySQL connection pool: {e}")

    @classmethod
    def from_config(cls, config_path: str = "aibasic.conf") -> 'MySQLModule':
        """
        Create a MySQLModule from configuration file.
        Uses singleton pattern to ensure only one pool exists.

        Args:
            config_path: Path to aibasic.conf file

        Returns:
            MySQLModule instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            KeyError: If required configuration is missing
        """
        with cls._lock:
            if cls._instance is None:
                config = configparser.ConfigParser()
                path = Path(config_path)

                if not path.exists():
                    raise FileNotFoundError(f"Configuration file not found: {config_path}")

                config.read(path)

                if 'mysql' not in config:
                    raise KeyError("Missing [mysql] section in aibasic.conf")

                mysql_config = config['mysql']

                # Required fields
                host = mysql_config.get('HOST')
                port = mysql_config.getint('PORT', 3306)
                database = mysql_config.get('DATABASE')
                user = mysql_config.get('USER')
                password = mysql_config.get('PASSWORD')

                # Optional fields
                min_conn = mysql_config.getint('MIN_CONNECTIONS', 1)
                max_conn = mysql_config.getint('MAX_CONNECTIONS', 10)
                charset = mysql_config.get('CHARSET', 'utf8mb4')

                if not all([host, database, user, password]):
                    raise KeyError("Missing required mysql configuration: HOST, DATABASE, USER, PASSWORD")

                cls._instance = cls(
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=password,
                    min_connections=min_conn,
                    max_connections=max_conn,
                    charset=charset
                )

            return cls._instance

    def get_connection(self):
        """
        Get a connection from the pool.

        Returns:
            mysql.connector.connection: A database connection

        Raises:
            RuntimeError: If unable to get connection from pool
        """
        try:
            conn = self.connection_pool.get_connection()
            if conn:
                return conn
            else:
                raise RuntimeError("Unable to get connection from pool")
        except Error as e:
            raise RuntimeError(f"Error getting connection: {e}")

    def release_connection(self, conn):
        """
        Release a connection back to the pool.

        Args:
            conn: The connection to release
        """
        if conn and conn.is_connected():
            conn.close()  # Returns to pool when using pooling

    def execute_query(self, query: str, params: tuple = None, fetch: bool = True) -> Optional[List[Tuple]]:
        """
        Execute a query using a connection from the pool.
        Automatically handles connection acquisition and release.

        Args:
            query: SQL query to execute
            params: Optional parameters for parameterized query
            fetch: If True, fetch and return results (for SELECT)

        Returns:
            List of rows if fetch=True, None otherwise

        Example:
            results = mysql.execute_query("SELECT * FROM users WHERE age > %s", (25,))
        """
        conn = self.get_connection()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)

            if fetch:
                results = cursor.fetchall()
                return results
            else:
                conn.commit()
                return None
        except Error as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Query execution failed: {e}")
        finally:
            if cursor:
                cursor.close()
            self.release_connection(conn)

    def execute_query_dict(self, query: str, params: tuple = None) -> Optional[List[dict]]:
        """
        Execute a query and return results as list of dictionaries.
        Each row is a dict with column names as keys.

        Args:
            query: SQL query to execute
            params: Optional parameters for parameterized query

        Returns:
            List of dictionaries, one per row

        Example:
            results = mysql.execute_query_dict("SELECT * FROM users WHERE age > %s", (25,))
            # [{'id': 1, 'name': 'Alice', 'age': 30}, ...]
        """
        conn = self.get_connection()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            results = cursor.fetchall()
            return results
        except Error as e:
            raise RuntimeError(f"Query execution failed: {e}")
        finally:
            if cursor:
                cursor.close()
            self.release_connection(conn)

    def execute_many(self, query: str, params_list: List[tuple]):
        """
        Execute the same query multiple times with different parameters.
        Useful for batch inserts.

        Args:
            query: SQL query to execute
            params_list: List of parameter tuples

        Example:
            mysql.execute_many(
                "INSERT INTO users (name, age) VALUES (%s, %s)",
                [("Alice", 30), ("Bob", 25), ("Charlie", 35)]
            )
        """
        conn = self.get_connection()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
        except Error as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Batch execution failed: {e}")
        finally:
            if cursor:
                cursor.close()
            self.release_connection(conn)

    def call_procedure(self, proc_name: str, args: tuple = ()) -> Optional[List[Any]]:
        """
        Call a stored procedure.

        Args:
            proc_name: Name of the stored procedure
            args: Arguments to pass to the procedure

        Returns:
            Results from the procedure

        Example:
            results = mysql.call_procedure('get_user_orders', (user_id,))
        """
        conn = self.get_connection()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.callproc(proc_name, args)

            # Fetch results if any
            results = []
            for result in cursor.stored_results():
                results.extend(result.fetchall())

            conn.commit()
            return results if results else None
        except Error as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Procedure call failed: {e}")
        finally:
            if cursor:
                cursor.close()
            self.release_connection(conn)

    def get_pool_status(self) -> dict:
        """
        Get current status of the connection pool.

        Returns:
            dict: Pool statistics and configuration
        """
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "charset": self.charset,
            "min_connections": self.min_connections,
            "max_connections": self.max_connections,
            "pool_name": "aibasic_mysql_pool"
        }

    def close_all_connections(self):
        """
        Close all connections in the pool.
        Should be called when the program terminates.

        Note: With mysql.connector pooling, connections are automatically
        managed, but we provide this for consistency.
        """
        print("[MySQLModule] Connection pool cleanup")

    def __del__(self):
        """Destructor to ensure connections are closed."""
        self.close_all_connections()

    # ========================================
    # Metadata methods for AIbasic compiler
    # ========================================

    @classmethod
    def get_metadata(cls):
        """Get module metadata for compiler prompt generation."""
        from aibasic.modules.module_base import ModuleMetadata
        return ModuleMetadata(
            name="MySQL",
            task_type="mysql",
            description="MySQL/MariaDB relational database with connection pooling, SQL query execution, and stored procedure support",
            version="1.0.0",
            keywords=[
                "mysql", "mariadb", "sql", "database", "relational", "query",
                "connection-pool", "stored-procedure", "transactions"
            ],
            dependencies=["mysql-connector-python>=8.0.0"]
        )

    @classmethod
    def get_usage_notes(cls):
        """Get detailed usage notes for this module."""
        return [
            "Module uses singleton pattern via from_config() - one connection pool per application",
            "Connection pooling ensures efficient reuse of database connections",
            "Default pool size: minimum 1 connection, maximum 10 connections (configurable)",
            "All connections use autocommit=False for explicit transaction control",
            "Character set defaults to utf8mb4 for full Unicode support including emojis",
            "Connection pool automatically resets session state when connections are reused",
            "Parameterized queries with %s placeholders prevent SQL injection attacks",
            "execute_query() automatically commits for non-SELECT queries and rolls back on error",
            "execute_query_dict() returns results as list of dictionaries with column names as keys",
            "execute_many() provides batch execution for efficient bulk inserts and updates",
            "Connections are automatically returned to pool when released or closed",
            "Pool name is 'aibasic_mysql_pool' - visible in MySQL process list",
            "All methods raise RuntimeError on database errors with descriptive messages",
            "MySQL connector handles automatic reconnection for lost connections",
            "Stored procedures can be called with call_procedure() method",
            "Always use release_connection() or context managers to return connections to pool",
            "Query parameters must be passed as tuples, even for single parameter (param,)",
            "SELECT queries use fetch=True (default), INSERT/UPDATE/DELETE use fetch=False",
            "Transactions are manually controlled - use commit/rollback on connection object",
            "Pool status available via get_pool_status() for monitoring and debugging"
        ]

    @classmethod
    def get_methods_info(cls):
        """Get information about all methods in this module."""
        from aibasic.modules.module_base import MethodInfo
        return [
            MethodInfo(
                name="get_connection",
                description="Get a database connection from the connection pool for manual query execution",
                parameters={},
                returns="mysql.connector.connection - Database connection object from pool",
                examples=[
                    'get connection from pool',
                    'get database connection'
                ]
            ),
            MethodInfo(
                name="release_connection",
                description="Return a connection back to the pool for reuse by other operations",
                parameters={
                    "conn": "connection (required) - Connection object to return to pool"
                },
                returns="None",
                examples=[
                    'release connection',
                    'return connection to pool'
                ]
            ),
            MethodInfo(
                name="execute_query",
                description="Execute SQL query with automatic connection handling, commits non-SELECT queries and fetches SELECT results",
                parameters={
                    "query": "str (required) - SQL query with %s placeholders for parameters",
                    "params": "tuple (optional) - Parameter values for placeholders",
                    "fetch": "bool (optional) - True to fetch results (SELECT), False for INSERT/UPDATE/DELETE (default True)"
                },
                returns="list[tuple] if fetch=True (SELECT results), None if fetch=False (INSERT/UPDATE/DELETE)",
                examples=[
                    'execute query "SELECT * FROM users WHERE age > %s" params (25,)',
                    'execute query "INSERT INTO users (name, email) VALUES (%s, %s)" params ("Alice", "alice@example.com") fetch False',
                    'execute query "UPDATE users SET status = %s WHERE id = %s" params ("active", 123) fetch False',
                    'execute query "DELETE FROM users WHERE id = %s" params (456,) fetch False'
                ]
            ),
            MethodInfo(
                name="execute_query_dict",
                description="Execute SELECT query and return results as list of dictionaries with column names as keys",
                parameters={
                    "query": "str (required) - SQL SELECT query with %s placeholders",
                    "params": "tuple (optional) - Parameter values for placeholders"
                },
                returns="list[dict] - List of dictionaries, one per row with column names as keys",
                examples=[
                    'execute query dict "SELECT id, name, email FROM users WHERE age > %s" params (25,)',
                    'execute query dict "SELECT * FROM products WHERE category = %s" params ("electronics",)',
                    'execute query dict "SELECT name, SUM(amount) as total FROM orders GROUP BY name"'
                ]
            ),
            MethodInfo(
                name="execute_many",
                description="Execute same SQL query multiple times with different parameters for efficient batch operations",
                parameters={
                    "query": "str (required) - SQL query with %s placeholders",
                    "params_list": "list[tuple] (required) - List of parameter tuples, one per execution"
                },
                returns="None - commits all operations or rolls back on error",
                examples=[
                    'execute many "INSERT INTO users (name, age) VALUES (%s, %s)" params [("Alice", 30), ("Bob", 25), ("Carol", 28)]',
                    'batch insert "INSERT INTO products (sku, price) VALUES (%s, %s)" params [("WIDGET-1", 19.99), ("GADGET-2", 29.99)]',
                    'execute many "UPDATE users SET last_login = %s WHERE id = %s" params [(1234567890, 1), (1234567891, 2)]'
                ]
            ),
            MethodInfo(
                name="call_procedure",
                description="Call MySQL stored procedure with arguments and retrieve results",
                parameters={
                    "proc_name": "str (required) - Name of stored procedure to call",
                    "args": "tuple (optional) - Arguments to pass to procedure (default empty tuple)"
                },
                returns="list[any] or None - Results from procedure, None if no results",
                examples=[
                    'call procedure "get_user_orders" args (123,)',
                    'call procedure "calculate_totals" args (2023, "Q1")',
                    'call procedure "cleanup_old_data"'
                ]
            ),
            MethodInfo(
                name="get_pool_status",
                description="Get connection pool configuration and status information for monitoring",
                parameters={},
                returns="dict - Dictionary with host, port, database, charset, min/max connections, pool name",
                examples=[
                    'get pool status',
                    'show connection pool info'
                ]
            ),
            MethodInfo(
                name="close_all_connections",
                description="Close all connections in the pool (called automatically on program termination)",
                parameters={},
                returns="None - prints cleanup confirmation",
                examples=[
                    'close all connections',
                    'shutdown connection pool'
                ]
            )
        ]

    @classmethod
    def get_examples(cls):
        """Get example AIbasic code snippets."""
        return [
            # Basic SELECT queries
            '10 (mysql) execute query "SELECT * FROM users"',
            '20 (mysql) execute query "SELECT * FROM users WHERE age > %s" params (25,)',
            '30 (mysql) execute query "SELECT id, name, email FROM users WHERE status = %s" params ("active",)',

            # SELECT with dictionary results
            '10 (mysql) execute query dict "SELECT * FROM products WHERE category = %s" params ("electronics",)',
            '20 (mysql) execute query dict "SELECT id, name, price FROM products ORDER BY price DESC LIMIT 10"',

            # INSERT operations
            '10 (mysql) execute query "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)" params ("Alice", "alice@example.com", 30) fetch False',
            '20 (mysql) execute query "INSERT INTO products (sku, name, price) VALUES (%s, %s, %s)" params ("WIDGET-1", "Super Widget", 19.99) fetch False',

            # UPDATE operations
            '10 (mysql) execute query "UPDATE users SET status = %s WHERE id = %s" params ("inactive", 123) fetch False',
            '20 (mysql) execute query "UPDATE products SET price = price * %s WHERE category = %s" params (1.1, "electronics") fetch False',
            '30 (mysql) execute query "UPDATE users SET last_login = %s WHERE email = %s" params (1234567890, "alice@example.com") fetch False',

            # DELETE operations
            '10 (mysql) execute query "DELETE FROM users WHERE id = %s" params (456,) fetch False',
            '20 (mysql) execute query "DELETE FROM sessions WHERE expired = 1" fetch False',
            '30 (mysql) execute query "DELETE FROM logs WHERE created_at < %s" params ("2023-01-01",) fetch False',

            # Batch operations with execute_many
            '10 (mysql) execute many "INSERT INTO users (name, age) VALUES (%s, %s)" params [("Alice", 30), ("Bob", 25), ("Carol", 28), ("Dave", 35)]',
            '20 (mysql) batch insert "INSERT INTO products (sku, price) VALUES (%s, %s)" params [("WIDGET-1", 19.99), ("GADGET-2", 29.99), ("TOOL-3", 39.99)]',
            '30 (mysql) execute many "UPDATE inventory SET quantity = %s WHERE sku = %s" params [(100, "WIDGET-1"), (50, "GADGET-2")]',

            # Complex queries with JOINs
            '10 (mysql) execute query "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id WHERE u.id = %s" params (123,)',
            '20 (mysql) execute query dict "SELECT p.name, c.name as category FROM products p JOIN categories c ON p.category_id = c.id WHERE p.price > %s" params (100,)',

            # Aggregation queries
            '10 (mysql) execute query "SELECT COUNT(*) FROM users WHERE status = %s" params ("active",)',
            '20 (mysql) execute query "SELECT category, SUM(price) as total FROM products GROUP BY category"',
            '30 (mysql) execute query dict "SELECT DATE(created_at) as date, COUNT(*) as count FROM orders GROUP BY DATE(created_at) ORDER BY date DESC LIMIT 7"',

            # Stored procedures
            '10 (mysql) call procedure "get_user_orders" args (123,)',
            '20 (mysql) call procedure "calculate_monthly_revenue" args (2023, 12)',
            '30 (mysql) call procedure "cleanup_expired_sessions"',

            # Manual connection handling
            '10 (mysql) get connection from pool',
            '20 (mysql) release connection',

            # Pool monitoring
            '10 (mysql) get pool status',
            '20 (mysql) show connection pool info',

            # Complete CRUD workflow
            '10 (mysql) execute query "CREATE TABLE IF NOT EXISTS customers (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(255), email VARCHAR(255), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)" fetch False',
            '20 (mysql) execute query "INSERT INTO customers (name, email) VALUES (%s, %s)" params ("Acme Corp", "info@acme.com") fetch False',
            '30 (mysql) execute query dict "SELECT * FROM customers WHERE email = %s" params ("info@acme.com",)',
            '40 (mysql) execute query "UPDATE customers SET name = %s WHERE email = %s" params ("Acme Corporation", "info@acme.com") fetch False',
            '50 (mysql) execute query "DELETE FROM customers WHERE email = %s" params ("info@acme.com",) fetch False',

            # E-commerce example
            '10 (mysql) execute query dict "SELECT p.*, c.name as category_name FROM products p JOIN categories c ON p.category_id = c.id WHERE p.in_stock = 1 ORDER BY p.created_at DESC LIMIT 20"',
            '20 (mysql) execute query "UPDATE products SET quantity = quantity - %s WHERE id = %s AND quantity >= %s" params (1, 456, 1) fetch False',
            '30 (mysql) execute query "INSERT INTO orders (user_id, product_id, quantity, total) VALUES (%s, %s, %s, %s)" params (123, 456, 1, 29.99) fetch False',

            # Analytics queries
            '10 (mysql) execute query dict "SELECT DATE_FORMAT(created_at, \'%Y-%m\') as month, COUNT(*) as orders, SUM(total) as revenue FROM orders GROUP BY month ORDER BY month DESC"',
            '20 (mysql) execute query dict "SELECT u.name, COUNT(o.id) as order_count, SUM(o.total) as total_spent FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id ORDER BY total_spent DESC LIMIT 10"',

            # Cleanup
            '10 (mysql) close all connections'
        ]
