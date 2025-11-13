"""
PostgreSQL Module with Connection Pool

This module provides a connection pool for PostgreSQL databases.
Configuration is loaded from aibasic.conf under the [postgres] section.

Example configuration in aibasic.conf:
    [postgres]
    HOST=localhost
    PORT=5432
    DATABASE=mydb
    USER=postgres
    PASSWORD=secret
    MIN_CONNECTIONS=1
    MAX_CONNECTIONS=10

Usage in generated code:
    from aibasic.modules import PostgresModule

    # Initialize module (happens once per program)
    pg = PostgresModule.from_config(config_path="aibasic.conf")

    # Get a connection from the pool
    conn = pg.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers")
        results = cursor.fetchall()
    finally:
        pg.release_connection(conn)
"""

import configparser
import psycopg2
from psycopg2 import pool
from pathlib import Path
from typing import Optional
import threading


class PostgresModule:
    """
    PostgreSQL connection pool manager.

    This class manages a pool of connections to a PostgreSQL database,
    allowing efficient reuse of connections across multiple operations.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self, host: str, port: int, database: str, user: str,
                 password: str, min_connections: int = 1, max_connections: int = 10):
        """
        Initialize the PostgreSQL connection pool.

        Args:
            host: Database host address
            port: Database port (typically 5432)
            database: Database name
            user: Username for authentication
            password: Password for authentication
            min_connections: Minimum number of connections in pool
            max_connections: Maximum number of connections in pool
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.min_connections = min_connections
        self.max_connections = max_connections

        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                min_connections,
                max_connections,
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            print(f"[PostgresModule] Connection pool created: {database}@{host}:{port}")
        except psycopg2.Error as e:
            raise RuntimeError(f"Failed to create PostgreSQL connection pool: {e}")

    @classmethod
    def from_config(cls, config_path: str = "aibasic.conf") -> 'PostgresModule':
        """
        Create a PostgresModule from configuration file.
        Uses singleton pattern to ensure only one pool exists.

        Args:
            config_path: Path to aibasic.conf file

        Returns:
            PostgresModule instance

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

                if 'postgres' not in config:
                    raise KeyError("Missing [postgres] section in aibasic.conf")

                pg_config = config['postgres']

                # Required fields
                host = pg_config.get('HOST')
                port = pg_config.getint('PORT', 5432)
                database = pg_config.get('DATABASE')
                user = pg_config.get('USER')
                password = pg_config.get('PASSWORD')

                # Optional fields
                min_conn = pg_config.getint('MIN_CONNECTIONS', 1)
                max_conn = pg_config.getint('MAX_CONNECTIONS', 10)

                if not all([host, database, user, password]):
                    raise KeyError("Missing required postgres configuration: HOST, DATABASE, USER, PASSWORD")

                cls._instance = cls(
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=password,
                    min_connections=min_conn,
                    max_connections=max_conn
                )

            return cls._instance

    def get_connection(self):
        """
        Get a connection from the pool.

        Returns:
            psycopg2.connection: A database connection

        Raises:
            RuntimeError: If unable to get connection from pool
        """
        try:
            conn = self.connection_pool.getconn()
            if conn:
                return conn
            else:
                raise RuntimeError("Unable to get connection from pool")
        except psycopg2.Error as e:
            raise RuntimeError(f"Error getting connection: {e}")

    def release_connection(self, conn):
        """
        Release a connection back to the pool.

        Args:
            conn: The connection to release
        """
        if conn:
            self.connection_pool.putconn(conn)

    def execute_query(self, query: str, params: tuple = None, fetch: bool = True):
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
            results = pg.execute_query("SELECT * FROM users WHERE age > %s", (25,))
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)

            if fetch:
                results = cursor.fetchall()
                return results
            else:
                conn.commit()
                return None
        except psycopg2.Error as e:
            conn.rollback()
            raise RuntimeError(f"Query execution failed: {e}")
        finally:
            cursor.close()
            self.release_connection(conn)

    def execute_many(self, query: str, params_list: list):
        """
        Execute the same query multiple times with different parameters.
        Useful for batch inserts.

        Args:
            query: SQL query to execute
            params_list: List of parameter tuples

        Example:
            pg.execute_many(
                "INSERT INTO users (name, age) VALUES (%s, %s)",
                [("Alice", 30), ("Bob", 25), ("Charlie", 35)]
            )
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            raise RuntimeError(f"Batch execution failed: {e}")
        finally:
            cursor.close()
            self.release_connection(conn)

    def close_all_connections(self):
        """
        Close all connections in the pool.
        Should be called when the program terminates.
        """
        if self.connection_pool:
            self.connection_pool.closeall()
            print("[PostgresModule] All connections closed")

    def __del__(self):
        """Destructor to ensure connections are closed."""
        self.close_all_connections()

    def get_pool_status(self) -> dict:
        """
        Get current status of the connection pool.

        Returns:
            dict: Pool statistics
        """
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "min_connections": self.min_connections,
            "max_connections": self.max_connections
        }
