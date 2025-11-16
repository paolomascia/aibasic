"""
ScyllaDB Module for AIbasic

This module provides comprehensive ScyllaDB database integration.
ScyllaDB is a high-performance NoSQL database compatible with Apache Cassandra,
written in C++ for better performance and lower latency.

Features:
- Keyspace Management: Create, drop, alter keyspaces
- Table Operations: Create, drop, truncate tables
- Data Operations: Insert, update, delete, select
- Batch Operations: Efficient bulk operations
- Prepared Statements: Performance optimization
- Consistency Levels: Tunable consistency (ONE, QUORUM, ALL, etc.)
- Materialized Views: Query optimization
- Secondary Indexes: Additional query patterns
- User-Defined Types: Complex data structures
- Counter Columns: Distributed counters
- Time-Series Data: Time-based partitioning
- Connection Pooling: Efficient resource management

Author: AIbasic Team
License: MIT
"""

import threading
import os
from typing import Optional, List, Dict, Any, Union
from cassandra.cluster import Cluster, Session, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import (
    DCAwareRoundRobinPolicy, TokenAwarePolicy,
    DowngradingConsistencyRetryPolicy, WhiteListRoundRobinPolicy
)
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement, BatchStatement, BatchType, ConsistencyLevel
from cassandra import ConsistencyLevel as CL


class ScyllaDBModule:
    """
    ScyllaDB module for high-performance NoSQL database operations.

    Provides comprehensive ScyllaDB integration with:
    - Keyspace and table management
    - CRUD operations with tunable consistency
    - Batch operations and prepared statements
    - Materialized views and secondary indexes
    - Time-series data support
    """

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        """Singleton pattern - only one instance allowed."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize ScyllaDB module with configuration."""
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            # Load configuration
            self._load_config()

            # Cluster and session
            self._cluster = None
            self._session = None

            # Prepared statements cache
            self._prepared_statements = {}

            self._initialized = True

    def _load_config(self):
        """Load configuration from environment or config file."""
        # Contact points (comma-separated list)
        contact_points_str = os.getenv('SCYLLADB_CONTACT_POINTS', 'localhost')
        self.contact_points = [cp.strip() for cp in contact_points_str.split(',')]

        # Port
        self.port = int(os.getenv('SCYLLADB_PORT', '9042'))

        # Keyspace
        self.keyspace = os.getenv('SCYLLADB_KEYSPACE', 'aibasic_keyspace')

        # Authentication
        self.username = os.getenv('SCYLLADB_USERNAME', '')
        self.password = os.getenv('SCYLLADB_PASSWORD', '')

        # Connection settings
        self.protocol_version = int(os.getenv('SCYLLADB_PROTOCOL_VERSION', '4'))
        self.compression = os.getenv('SCYLLADB_COMPRESSION', 'true').lower() == 'true'

        # Consistency level
        consistency_str = os.getenv('SCYLLADB_CONSISTENCY_LEVEL', 'LOCAL_QUORUM')
        self.default_consistency_level = getattr(CL, consistency_str, CL.LOCAL_QUORUM)

        # Replication settings
        self.replication_strategy = os.getenv('SCYLLADB_REPLICATION_STRATEGY', 'NetworkTopologyStrategy')
        self.replication_factor = int(os.getenv('SCYLLADB_REPLICATION_FACTOR', '3'))

        # Connection pool
        self.pool_size = int(os.getenv('SCYLLADB_POOL_SIZE', '10'))

        # Timeouts
        self.connect_timeout = int(os.getenv('SCYLLADB_CONNECT_TIMEOUT', '10'))
        self.request_timeout = int(os.getenv('SCYLLADB_REQUEST_TIMEOUT', '10'))

    @property
    def cluster(self):
        """Get ScyllaDB cluster (lazy-loaded)."""
        if self._cluster is None:
            try:
                # Auth provider
                auth_provider = None
                if self.username and self.password:
                    auth_provider = PlainTextAuthProvider(
                        username=self.username,
                        password=self.password
                    )

                # Load balancing policy
                load_balancing_policy = TokenAwarePolicy(
                    DCAwareRoundRobinPolicy()
                )

                # Execution profile
                profile = ExecutionProfile(
                    load_balancing_policy=load_balancing_policy,
                    retry_policy=DowngradingConsistencyRetryPolicy(),
                    consistency_level=self.default_consistency_level,
                    request_timeout=self.request_timeout
                )

                # Create cluster
                self._cluster = Cluster(
                    contact_points=self.contact_points,
                    port=self.port,
                    auth_provider=auth_provider,
                    protocol_version=self.protocol_version,
                    compression=self.compression,
                    execution_profiles={EXEC_PROFILE_DEFAULT: profile},
                    connect_timeout=self.connect_timeout
                )
            except Exception as e:
                raise RuntimeError(f"Failed to create ScyllaDB cluster: {e}")
        return self._cluster

    @property
    def session(self):
        """Get ScyllaDB session (lazy-loaded)."""
        if self._session is None:
            try:
                self._session = self.cluster.connect()
            except Exception as e:
                raise RuntimeError(f"Failed to connect to ScyllaDB: {e}")
        return self._session

    def _parse_consistency_level(self, consistency: Optional[str] = None) -> ConsistencyLevel:
        """Parse consistency level string to ConsistencyLevel enum."""
        if consistency is None:
            return self.default_consistency_level
        return getattr(CL, consistency.upper(), self.default_consistency_level)

    # ============================================================================
    # Keyspace Operations
    # ============================================================================

    def create_keyspace(self, keyspace: str, replication_strategy: Optional[str] = None,
                       replication_factor: Optional[int] = None,
                       durable_writes: bool = True) -> bool:
        """
        Create a keyspace.

        Args:
            keyspace: Keyspace name
            replication_strategy: SimpleStrategy or NetworkTopologyStrategy
            replication_factor: Replication factor for SimpleStrategy
            durable_writes: Enable durable writes

        Returns:
            True if successful
        """
        try:
            strategy = replication_strategy or self.replication_strategy
            factor = replication_factor or self.replication_factor

            if strategy == 'SimpleStrategy':
                replication = f"{{'class': 'SimpleStrategy', 'replication_factor': {factor}}}"
            else:
                # NetworkTopologyStrategy - single DC for simplicity
                replication = f"{{'class': 'NetworkTopologyStrategy', 'datacenter1': {factor}}}"

            cql = f"""
                CREATE KEYSPACE IF NOT EXISTS {keyspace}
                WITH replication = {replication}
                AND durable_writes = {str(durable_writes).lower()}
            """

            self.session.execute(cql)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to create keyspace: {e}")

    def drop_keyspace(self, keyspace: str) -> bool:
        """Drop a keyspace."""
        try:
            cql = f"DROP KEYSPACE IF EXISTS {keyspace}"
            self.session.execute(cql)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to drop keyspace: {e}")

    def use_keyspace(self, keyspace: str) -> bool:
        """Set the current keyspace."""
        try:
            self.session.set_keyspace(keyspace)
            self.keyspace = keyspace
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to use keyspace: {e}")

    def list_keyspaces(self) -> List[str]:
        """List all keyspaces."""
        try:
            result = self.session.execute(
                "SELECT keyspace_name FROM system_schema.keyspaces"
            )
            return [row.keyspace_name for row in result]
        except Exception as e:
            raise RuntimeError(f"Failed to list keyspaces: {e}")

    # ============================================================================
    # Table Operations
    # ============================================================================

    def execute(self, cql: str, consistency: Optional[str] = None) -> Any:
        """
        Execute a CQL statement.

        Args:
            cql: CQL statement
            consistency: Consistency level (ONE, QUORUM, ALL, etc.)

        Returns:
            Query result
        """
        try:
            consistency_level = self._parse_consistency_level(consistency)
            statement = SimpleStatement(cql, consistency_level=consistency_level)
            result = self.session.execute(statement)
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to execute CQL: {e}")

    def create_table(self, table: str, schema: str, if_not_exists: bool = True) -> bool:
        """
        Create a table.

        Args:
            table: Table name
            schema: Table schema (columns and primary key)
            if_not_exists: Add IF NOT EXISTS clause

        Returns:
            True if successful
        """
        try:
            if_clause = "IF NOT EXISTS" if if_not_exists else ""
            cql = f"CREATE TABLE {if_clause} {self.keyspace}.{table} ({schema})"
            self.session.execute(cql)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to create table: {e}")

    def drop_table(self, table: str, if_exists: bool = True) -> bool:
        """Drop a table."""
        try:
            if_clause = "IF EXISTS" if if_exists else ""
            cql = f"DROP TABLE {if_clause} {self.keyspace}.{table}"
            self.session.execute(cql)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to drop table: {e}")

    def truncate_table(self, table: str) -> bool:
        """Truncate a table (remove all data)."""
        try:
            cql = f"TRUNCATE {self.keyspace}.{table}"
            self.session.execute(cql)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to truncate table: {e}")

    def list_tables(self, keyspace: Optional[str] = None) -> List[str]:
        """List all tables in a keyspace."""
        try:
            ks = keyspace or self.keyspace
            result = self.session.execute(
                f"SELECT table_name FROM system_schema.tables WHERE keyspace_name = '{ks}'"
            )
            return [row.table_name for row in result]
        except Exception as e:
            raise RuntimeError(f"Failed to list tables: {e}")

    # ============================================================================
    # Data Operations
    # ============================================================================

    def insert(self, table: str, data: Dict[str, Any],
              consistency: Optional[str] = None, ttl: Optional[int] = None) -> bool:
        """
        Insert data into a table.

        Args:
            table: Table name
            data: Dictionary of column:value pairs
            consistency: Consistency level
            ttl: Time to live in seconds

        Returns:
            True if successful
        """
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            values = list(data.values())

            cql = f"INSERT INTO {self.keyspace}.{table} ({columns}) VALUES ({placeholders})"

            if ttl:
                cql += f" USING TTL {ttl}"

            consistency_level = self._parse_consistency_level(consistency)
            statement = SimpleStatement(cql, consistency_level=consistency_level)

            self.session.execute(statement, values)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to insert data: {e}")

    def update(self, table: str, set_values: Dict[str, Any], where: Dict[str, Any],
              consistency: Optional[str] = None, ttl: Optional[int] = None) -> bool:
        """
        Update data in a table.

        Args:
            table: Table name
            set_values: Dictionary of columns to update
            where: Dictionary of WHERE clause conditions
            consistency: Consistency level
            ttl: Time to live in seconds

        Returns:
            True if successful
        """
        try:
            set_clause = ', '.join([f"{k} = %s" for k in set_values.keys()])
            where_clause = ' AND '.join([f"{k} = %s" for k in where.keys()])

            cql = f"UPDATE {self.keyspace}.{table}"

            if ttl:
                cql += f" USING TTL {ttl}"

            cql += f" SET {set_clause} WHERE {where_clause}"

            values = list(set_values.values()) + list(where.values())

            consistency_level = self._parse_consistency_level(consistency)
            statement = SimpleStatement(cql, consistency_level=consistency_level)

            self.session.execute(statement, values)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to update data: {e}")

    def delete(self, table: str, where: Dict[str, Any],
              consistency: Optional[str] = None) -> bool:
        """
        Delete data from a table.

        Args:
            table: Table name
            where: Dictionary of WHERE clause conditions
            consistency: Consistency level

        Returns:
            True if successful
        """
        try:
            where_clause = ' AND '.join([f"{k} = %s" for k in where.keys()])
            cql = f"DELETE FROM {self.keyspace}.{table} WHERE {where_clause}"

            values = list(where.values())

            consistency_level = self._parse_consistency_level(consistency)
            statement = SimpleStatement(cql, consistency_level=consistency_level)

            self.session.execute(statement, values)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete data: {e}")

    def select(self, table: str, columns: str = '*', where: Optional[Dict[str, Any]] = None,
              limit: Optional[int] = None, consistency: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Select data from a table.

        Args:
            table: Table name
            columns: Columns to select (comma-separated or *)
            where: Dictionary of WHERE clause conditions
            limit: Maximum number of rows
            consistency: Consistency level

        Returns:
            List of rows as dictionaries
        """
        try:
            cql = f"SELECT {columns} FROM {self.keyspace}.{table}"

            values = []
            if where:
                where_clause = ' AND '.join([f"{k} = %s" for k in where.keys()])
                cql += f" WHERE {where_clause}"
                values = list(where.values())

            if limit:
                cql += f" LIMIT {limit}"

            consistency_level = self._parse_consistency_level(consistency)
            statement = SimpleStatement(cql, consistency_level=consistency_level)

            result = self.session.execute(statement, values)

            # Convert to list of dictionaries
            rows = []
            for row in result:
                rows.append(dict(row._asdict()))

            return rows
        except Exception as e:
            raise RuntimeError(f"Failed to select data: {e}")

    # ============================================================================
    # Batch Operations
    # ============================================================================

    def batch_insert(self, table: str, data_list: List[Dict[str, Any]],
                    batch_type: str = 'LOGGED', consistency: Optional[str] = None) -> bool:
        """
        Batch insert multiple rows.

        Args:
            table: Table name
            data_list: List of dictionaries (rows to insert)
            batch_type: LOGGED, UNLOGGED, or COUNTER
            consistency: Consistency level

        Returns:
            True if successful
        """
        try:
            if not data_list:
                return True

            # Determine batch type
            if batch_type.upper() == 'UNLOGGED':
                batch = BatchStatement(batch_type=BatchType.UNLOGGED)
            elif batch_type.upper() == 'COUNTER':
                batch = BatchStatement(batch_type=BatchType.COUNTER)
            else:
                batch = BatchStatement(batch_type=BatchType.LOGGED)

            # Set consistency level
            consistency_level = self._parse_consistency_level(consistency)
            batch.consistency_level = consistency_level

            # Get columns from first row
            columns = ', '.join(data_list[0].keys())
            placeholders = ', '.join(['%s'] * len(data_list[0]))

            cql = f"INSERT INTO {self.keyspace}.{table} ({columns}) VALUES ({placeholders})"
            prepared = self.session.prepare(cql)

            # Add all inserts to batch
            for data in data_list:
                batch.add(prepared, list(data.values()))

            self.session.execute(batch)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to batch insert: {e}")

    # ============================================================================
    # Prepared Statements
    # ============================================================================

    def prepare(self, cql: str) -> str:
        """
        Prepare a CQL statement for reuse.

        Args:
            cql: CQL statement to prepare

        Returns:
            Statement ID (hash of CQL)
        """
        try:
            stmt_id = str(hash(cql))
            if stmt_id not in self._prepared_statements:
                self._prepared_statements[stmt_id] = self.session.prepare(cql)
            return stmt_id
        except Exception as e:
            raise RuntimeError(f"Failed to prepare statement: {e}")

    def execute_prepared(self, stmt_id: str, values: List[Any],
                        consistency: Optional[str] = None) -> Any:
        """
        Execute a prepared statement.

        Args:
            stmt_id: Statement ID from prepare()
            values: Parameter values
            consistency: Consistency level

        Returns:
            Query result
        """
        try:
            if stmt_id not in self._prepared_statements:
                raise ValueError(f"Statement ID '{stmt_id}' not found")

            prepared = self._prepared_statements[stmt_id]
            consistency_level = self._parse_consistency_level(consistency)
            bound = prepared.bind(values)
            bound.consistency_level = consistency_level

            result = self.session.execute(bound)
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to execute prepared statement: {e}")

    # ============================================================================
    # Secondary Indexes
    # ============================================================================

    def create_index(self, index_name: str, table: str, column: str,
                    if_not_exists: bool = True) -> bool:
        """Create a secondary index."""
        try:
            if_clause = "IF NOT EXISTS" if if_not_exists else ""
            cql = f"CREATE INDEX {if_clause} {index_name} ON {self.keyspace}.{table} ({column})"
            self.session.execute(cql)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to create index: {e}")

    def drop_index(self, index_name: str, if_exists: bool = True) -> bool:
        """Drop a secondary index."""
        try:
            if_clause = "IF EXISTS" if if_exists else ""
            cql = f"DROP INDEX {if_clause} {self.keyspace}.{index_name}"
            self.session.execute(cql)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to drop index: {e}")

    # ============================================================================
    # Materialized Views
    # ============================================================================

    def create_materialized_view(self, view_name: str, table: str, select_columns: str,
                                 where_clause: str, primary_key: str,
                                 if_not_exists: bool = True) -> bool:
        """Create a materialized view."""
        try:
            if_clause = "IF NOT EXISTS" if if_not_exists else ""
            cql = f"""
                CREATE MATERIALIZED VIEW {if_clause} {self.keyspace}.{view_name} AS
                SELECT {select_columns}
                FROM {self.keyspace}.{table}
                WHERE {where_clause}
                PRIMARY KEY ({primary_key})
            """
            self.session.execute(cql)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to create materialized view: {e}")

    def drop_materialized_view(self, view_name: str, if_exists: bool = True) -> bool:
        """Drop a materialized view."""
        try:
            if_clause = "IF EXISTS" if if_exists else ""
            cql = f"DROP MATERIALIZED VIEW {if_clause} {self.keyspace}.{view_name}"
            self.session.execute(cql)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to drop materialized view: {e}")

    # ============================================================================
    # Counter Operations
    # ============================================================================

    def increment_counter(self, table: str, counter_column: str, increment: int,
                         where: Dict[str, Any], consistency: Optional[str] = None) -> bool:
        """
        Increment a counter column.

        Args:
            table: Table name
            counter_column: Counter column name
            increment: Value to increment by
            where: Dictionary of WHERE clause conditions
            consistency: Consistency level

        Returns:
            True if successful
        """
        try:
            where_clause = ' AND '.join([f"{k} = %s" for k in where.keys()])
            cql = f"UPDATE {self.keyspace}.{table} SET {counter_column} = {counter_column} + %s WHERE {where_clause}"

            values = [increment] + list(where.values())

            consistency_level = self._parse_consistency_level(consistency)
            statement = SimpleStatement(cql, consistency_level=consistency_level)

            self.session.execute(statement, values)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to increment counter: {e}")

    # ============================================================================
    # Utility Methods
    # ============================================================================

    def close(self):
        """Close the connection to ScyllaDB."""
        try:
            if self._session:
                self._session.shutdown()
                self._session = None
            if self._cluster:
                self._cluster.shutdown()
                self._cluster = None
            self._prepared_statements.clear()
        except Exception as e:
            raise RuntimeError(f"Failed to close connection: {e}")

    def get_cluster_metadata(self) -> Dict[str, Any]:
        """Get cluster metadata."""
        try:
            metadata = self.cluster.metadata
            return {
                'cluster_name': metadata.cluster_name,
                'partitioner': metadata.partitioner,
                'hosts': [str(host) for host in metadata.all_hosts()],
                'keyspaces': list(metadata.keyspaces.keys())
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get cluster metadata: {e}")
