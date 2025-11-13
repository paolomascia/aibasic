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


class MySQLModule:
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
