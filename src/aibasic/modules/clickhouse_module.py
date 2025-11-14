"""
ClickHouse Module for AIbasic

This module provides integration with ClickHouse, a high-performance column-oriented
database management system for online analytical processing (OLAP).

Features:
- Connection management with connection pooling
- Query execution (SELECT, INSERT, CREATE, DROP, etc.)
- Batch inserts for high-performance data loading
- DataFrame integration (query results to DataFrame, DataFrame to ClickHouse)
- Multiple output formats (JSON, CSV, TabSeparated, etc.)
- Async query execution support
- Compression support (LZ4, ZSTD)
- Distributed table support
- Materialized views and aggregations
- Partitioning and indexing support

Author: AIbasic Team
Version: 1.0
"""

import threading
from typing import Any, Dict, List, Optional, Union
import requests
from urllib.parse import urlencode
import json
import pandas as pd
from io import StringIO


class ClickHouseModule:
    """
    ClickHouse module for AIbasic programs.

    Provides integration with ClickHouse databases for high-performance
    analytical queries and data processing.

    This class implements the singleton pattern to ensure only one instance
    exists per process, with thread-safe initialization.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """
        Create or return the singleton instance (thread-safe).
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8123,
        database: str = "default",
        username: str = "default",
        password: str = "",
        use_ssl: bool = False,
        verify_ssl: bool = True,
        timeout: int = 30,
        compression: str = None,  # None, 'lz4', 'zstd'
        **kwargs
    ):
        """
        Initialize the ClickHouse module.

        Args:
            host: ClickHouse server hostname
            port: HTTP port (default: 8123)
            database: Default database name
            username: Username for authentication
            password: Password for authentication
            use_ssl: Use HTTPS instead of HTTP
            verify_ssl: Verify SSL certificates
            timeout: Request timeout in seconds
            compression: Enable compression (lz4, zstd, or None)
            **kwargs: Additional configuration options
        """
        if self._initialized:
            return

        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.compression = compression

        # Build base URL
        protocol = "https" if use_ssl else "http"
        self.base_url = f"{protocol}://{host}:{port}"

        # Session for connection pooling
        self.session = requests.Session()
        self.session.verify = verify_ssl

        # Authentication
        if username and password:
            self.session.auth = (username, password)

        # Compression headers
        if compression:
            if compression.lower() == 'lz4':
                self.session.headers['Accept-Encoding'] = 'lz4'
            elif compression.lower() == 'zstd':
                self.session.headers['Accept-Encoding'] = 'zstd'

        # State variables
        self.last_query = None
        self.last_result = None
        self.last_format = "JSONEachRow"
        self.current_database = database

        self._initialized = True

    def execute(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
        output_format: str = "JSONEachRow",
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a ClickHouse query.

        Args:
            query: SQL query to execute
            params: Query parameters for substitution
            database: Database to use (overrides default)
            output_format: Output format (JSONEachRow, CSV, TabSeparated, etc.)
            settings: Additional ClickHouse settings

        Returns:
            Dictionary with query results and metadata
        """
        try:
            # Use specified database or default
            db = database or self.current_database

            # Build query parameters
            query_params = {
                'database': db,
                'default_format': output_format
            }

            # Add settings
            if settings:
                query_params.update(settings)

            # Parameter substitution if params provided
            if params:
                for key, value in params.items():
                    if isinstance(value, str):
                        query = query.replace(f':{key}', f"'{value}'")
                    else:
                        query = query.replace(f':{key}', str(value))

            # Execute query
            response = self.session.post(
                self.base_url,
                params=query_params,
                data=query,
                timeout=self.timeout
            )

            # Check for errors
            response.raise_for_status()

            # Store query info
            self.last_query = query
            self.last_format = output_format

            # Parse response based on format
            if output_format == "JSONEachRow":
                lines = response.text.strip().split('\n')
                data = [json.loads(line) for line in lines if line]
                self.last_result = data
                return {
                    'success': True,
                    'data': data,
                    'rows': len(data),
                    'format': output_format
                }
            elif output_format == "JSON":
                result = response.json()
                data = result.get('data', [])
                self.last_result = data
                return {
                    'success': True,
                    'data': data,
                    'rows': result.get('rows', 0),
                    'statistics': result.get('statistics', {}),
                    'format': output_format
                }
            else:
                # Raw response for other formats
                self.last_result = response.text
                return {
                    'success': True,
                    'data': response.text,
                    'format': output_format
                }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'query': query
            }

    def query(
        self,
        sql: str,
        params: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as list of dictionaries.

        Args:
            sql: SELECT query
            params: Query parameters
            database: Database to use

        Returns:
            List of dictionaries representing rows
        """
        result = self.execute(sql, params, database, output_format="JSONEachRow")
        if result['success']:
            return result['data']
        else:
            raise Exception(f"Query failed: {result.get('error')}")

    def query_df(
        self,
        sql: str,
        params: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Execute a SELECT query and return results as pandas DataFrame.

        Args:
            sql: SELECT query
            params: Query parameters
            database: Database to use

        Returns:
            pandas DataFrame with query results
        """
        data = self.query(sql, params, database)
        return pd.DataFrame(data)

    def insert(
        self,
        table: str,
        data: Union[List[Dict], pd.DataFrame],
        database: Optional[str] = None,
        columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Insert data into a ClickHouse table.

        Args:
            table: Table name
            data: Data to insert (list of dicts or DataFrame)
            database: Database to use
            columns: Column names (optional, inferred from data)

        Returns:
            Dictionary with insert results
        """
        try:
            db = database or self.current_database

            # Convert DataFrame to list of dicts
            if isinstance(data, pd.DataFrame):
                data = data.to_dict('records')

            if not data:
                return {'success': False, 'error': 'No data to insert'}

            # Get columns
            if columns is None:
                columns = list(data[0].keys())

            # Build INSERT query
            columns_str = ', '.join(columns)
            query = f"INSERT INTO {db}.{table} ({columns_str}) FORMAT JSONEachRow"

            # Convert data to JSONEachRow format
            json_data = '\n'.join([json.dumps(row) for row in data])

            # Execute insert
            response = self.session.post(
                self.base_url,
                params={'database': db},
                data=f"{query}\n{json_data}",
                timeout=self.timeout
            )

            response.raise_for_status()

            return {
                'success': True,
                'rows_inserted': len(data),
                'table': table
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'table': table
            }

    def batch_insert(
        self,
        table: str,
        data: Union[List[Dict], pd.DataFrame],
        database: Optional[str] = None,
        batch_size: int = 10000
    ) -> Dict[str, Any]:
        """
        Insert data in batches for better performance with large datasets.

        Args:
            table: Table name
            data: Data to insert
            database: Database to use
            batch_size: Number of rows per batch

        Returns:
            Dictionary with batch insert results
        """
        if isinstance(data, pd.DataFrame):
            data = data.to_dict('records')

        total_rows = len(data)
        inserted = 0
        errors = []

        for i in range(0, total_rows, batch_size):
            batch = data[i:i + batch_size]
            result = self.insert(table, batch, database)

            if result['success']:
                inserted += result['rows_inserted']
            else:
                errors.append(f"Batch {i//batch_size + 1}: {result['error']}")

        return {
            'success': len(errors) == 0,
            'total_rows': total_rows,
            'rows_inserted': inserted,
            'errors': errors if errors else None
        }

    def create_table(
        self,
        table: str,
        columns: Dict[str, str],
        engine: str = "MergeTree()",
        order_by: Optional[List[str]] = None,
        partition_by: Optional[str] = None,
        database: Optional[str] = None,
        if_not_exists: bool = True
    ) -> Dict[str, Any]:
        """
        Create a ClickHouse table.

        Args:
            table: Table name
            columns: Dictionary of column_name: column_type
            engine: Table engine (default: MergeTree())
            order_by: Columns to order by (required for MergeTree)
            partition_by: Partition expression
            database: Database to use
            if_not_exists: Add IF NOT EXISTS clause

        Returns:
            Dictionary with creation results
        """
        db = database or self.current_database

        # Build columns definition
        cols = ', '.join([f"{name} {dtype}" for name, dtype in columns.items()])

        # Build CREATE TABLE query
        query = f"CREATE TABLE "
        if if_not_exists:
            query += "IF NOT EXISTS "
        query += f"{db}.{table} ({cols}) ENGINE = {engine}"

        # Add ORDER BY for MergeTree engines
        if order_by and "MergeTree" in engine:
            query += f" ORDER BY ({', '.join(order_by)})"

        # Add PARTITION BY
        if partition_by:
            query += f" PARTITION BY {partition_by}"

        return self.execute(query, database=db)

    def drop_table(
        self,
        table: str,
        database: Optional[str] = None,
        if_exists: bool = True
    ) -> Dict[str, Any]:
        """
        Drop a ClickHouse table.

        Args:
            table: Table name
            database: Database to use
            if_exists: Add IF EXISTS clause

        Returns:
            Dictionary with drop results
        """
        db = database or self.current_database

        query = "DROP TABLE "
        if if_exists:
            query += "IF EXISTS "
        query += f"{db}.{table}"

        return self.execute(query, database=db)

    def show_tables(self, database: Optional[str] = None) -> List[str]:
        """
        List all tables in a database.

        Args:
            database: Database to list tables from

        Returns:
            List of table names
        """
        db = database or self.current_database
        result = self.query(f"SHOW TABLES FROM {db}")
        return [row['name'] for row in result]

    def show_databases(self) -> List[str]:
        """
        List all databases.

        Returns:
            List of database names
        """
        result = self.query("SHOW DATABASES")
        return [row['name'] for row in result]

    def describe_table(
        self,
        table: str,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get table schema information.

        Args:
            table: Table name
            database: Database to use

        Returns:
            List of column information dictionaries
        """
        db = database or self.current_database
        return self.query(f"DESCRIBE TABLE {db}.{table}")

    def optimize_table(
        self,
        table: str,
        database: Optional[str] = None,
        partition: Optional[str] = None,
        final: bool = False
    ) -> Dict[str, Any]:
        """
        Optimize a table (merge parts).

        Args:
            table: Table name
            database: Database to use
            partition: Specific partition to optimize
            final: Perform final optimization (force merge)

        Returns:
            Dictionary with optimization results
        """
        db = database or self.current_database

        query = f"OPTIMIZE TABLE {db}.{table}"
        if partition:
            query += f" PARTITION {partition}"
        if final:
            query += " FINAL"

        return self.execute(query, database=db)

    def truncate_table(
        self,
        table: str,
        database: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Truncate a table (remove all data).

        Args:
            table: Table name
            database: Database to use

        Returns:
            Dictionary with truncate results
        """
        db = database or self.current_database
        return self.execute(f"TRUNCATE TABLE {db}.{table}", database=db)

    def create_database(
        self,
        database: str,
        if_not_exists: bool = True,
        engine: str = "Atomic"
    ) -> Dict[str, Any]:
        """
        Create a database.

        Args:
            database: Database name
            if_not_exists: Add IF NOT EXISTS clause
            engine: Database engine (Atomic, MySQL, PostgreSQL, etc.)

        Returns:
            Dictionary with creation results
        """
        query = "CREATE DATABASE "
        if if_not_exists:
            query += "IF NOT EXISTS "
        query += f"{database} ENGINE = {engine}"

        return self.execute(query)

    def drop_database(
        self,
        database: str,
        if_exists: bool = True
    ) -> Dict[str, Any]:
        """
        Drop a database.

        Args:
            database: Database name
            if_exists: Add IF EXISTS clause

        Returns:
            Dictionary with drop results
        """
        query = "DROP DATABASE "
        if if_exists:
            query += "IF EXISTS "
        query += database

        return self.execute(query)

    def use_database(self, database: str):
        """
        Switch current database.

        Args:
            database: Database name to switch to
        """
        self.current_database = database

    def ping(self) -> bool:
        """
        Check if ClickHouse server is accessible.

        Returns:
            True if server responds, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.base_url}/ping",
                timeout=self.timeout
            )
            return response.status_code == 200
        except:
            return False

    def get_version(self) -> str:
        """
        Get ClickHouse server version.

        Returns:
            Version string
        """
        result = self.query("SELECT version()")
        return result[0]['version()'] if result else "Unknown"

    def get_stats(self, table: str, database: Optional[str] = None) -> Dict[str, Any]:
        """
        Get table statistics (row count, size, etc.).

        Args:
            table: Table name
            database: Database to use

        Returns:
            Dictionary with table statistics
        """
        db = database or self.current_database

        query = f"""
        SELECT
            count() as row_count,
            formatReadableSize(sum(bytes)) as total_size,
            formatReadableSize(sum(primary_key_bytes_in_memory)) as primary_key_size,
            sum(rows) as total_rows,
            count(DISTINCT partition) as partitions
        FROM system.parts
        WHERE database = '{db}' AND table = '{table}' AND active = 1
        """

        result = self.query(query)
        return result[0] if result else {}

    def close(self):
        """
        Close the session and cleanup resources.
        """
        if hasattr(self, 'session'):
            self.session.close()


# Singleton instance getter
def get_clickhouse_module(**kwargs) -> ClickHouseModule:
    """
    Get the singleton ClickHouse module instance.

    Args:
        **kwargs: Configuration parameters

    Returns:
        ClickHouseModule instance
    """
    return ClickHouseModule(**kwargs)
