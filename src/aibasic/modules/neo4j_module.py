"""
Neo4j Module for AIbasic

This module provides integration with Neo4j, a leading graph database management system
for storing and querying highly connected data using the Cypher query language.

Features:
- Connection management with connection pooling
- Cypher query execution (CREATE, MATCH, MERGE, etc.)
- Node and relationship operations
- Graph algorithms and path finding
- Transaction support
- Batch operations for performance
- Data import/export
- Index and constraint management
- Integration with pandas DataFrame
- Automatic retry logic

Author: AIbasic Team
Version: 1.0
"""

import threading
from typing import Any, Dict, List, Optional, Union
import pandas as pd


class Neo4jModule:
    """
    Neo4j module for AIbasic programs.

    Provides integration with Neo4j graph databases for storing and querying
    highly connected data with complex relationships.

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
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "password",
        database: str = "neo4j",
        encrypted: bool = False,
        trust: str = "TRUST_ALL_CERTIFICATES",
        max_connection_lifetime: int = 3600,
        max_connection_pool_size: int = 50,
        connection_acquisition_timeout: int = 60,
        **kwargs
    ):
        """
        Initialize the Neo4j module.

        Args:
            uri: Neo4j connection URI (bolt://, neo4j://, bolt+s://, neo4j+s://)
            username: Username for authentication
            password: Password for authentication
            database: Database name (default: neo4j)
            encrypted: Use encrypted connection
            trust: Trust strategy for certificates
            max_connection_lifetime: Max connection lifetime in seconds
            max_connection_pool_size: Maximum number of connections in pool
            connection_acquisition_timeout: Timeout for acquiring connection
            **kwargs: Additional driver configuration
        """
        if self._initialized:
            return

        try:
            from neo4j import GraphDatabase
            from neo4j.exceptions import ServiceUnavailable, AuthError
        except ImportError:
            raise ImportError(
                "neo4j package is required. Install with: pip install neo4j"
            )

        self.uri = uri
        self.username = username
        self.password = password
        self.database = database

        # Create driver with connection pooling
        self.driver = GraphDatabase.driver(
            uri,
            auth=(username, password),
            encrypted=encrypted,
            trust=trust,
            max_connection_lifetime=max_connection_lifetime,
            max_connection_pool_size=max_connection_pool_size,
            connection_acquisition_timeout=connection_acquisition_timeout,
            **kwargs
        )

        # Store exceptions for error handling
        self.ServiceUnavailable = ServiceUnavailable
        self.AuthError = AuthError

        # State variables
        self.last_query = None
        self.last_result = None
        self.current_database = database

        self._initialized = True

    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results.

        Args:
            query: Cypher query string
            parameters: Query parameters (key-value dict)
            database: Database to use (overrides default)

        Returns:
            List of result records as dictionaries
        """
        db = database or self.current_database
        params = parameters or {}

        try:
            with self.driver.session(database=db) as session:
                result = session.run(query, params)
                records = [dict(record) for record in result]

                self.last_query = query
                self.last_result = records

                return records

        except self.ServiceUnavailable as e:
            raise Exception(f"Neo4j service unavailable: {str(e)}")
        except self.AuthError as e:
            raise Exception(f"Neo4j authentication failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")

    def execute_write(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a write transaction (CREATE, MERGE, SET, DELETE).

        Args:
            query: Cypher write query
            parameters: Query parameters
            database: Database to use

        Returns:
            Dictionary with execution statistics
        """
        db = database or self.current_database
        params = parameters or {}

        def write_transaction(tx):
            result = tx.run(query, params)
            summary = result.consume()
            return {
                'nodes_created': summary.counters.nodes_created,
                'nodes_deleted': summary.counters.nodes_deleted,
                'relationships_created': summary.counters.relationships_created,
                'relationships_deleted': summary.counters.relationships_deleted,
                'properties_set': summary.counters.properties_set,
                'labels_added': summary.counters.labels_added,
                'labels_removed': summary.counters.labels_removed,
                'indexes_added': summary.counters.indexes_added,
                'indexes_removed': summary.counters.indexes_removed,
                'constraints_added': summary.counters.constraints_added,
                'constraints_removed': summary.counters.constraints_removed
            }

        try:
            with self.driver.session(database=db) as session:
                stats = session.execute_write(write_transaction)
                self.last_query = query
                return stats

        except Exception as e:
            raise Exception(f"Write transaction failed: {str(e)}")

    def create_node(
        self,
        label: str,
        properties: Dict[str, Any],
        database: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a node with label and properties.

        Args:
            label: Node label (e.g., "Person", "Product")
            properties: Node properties as dict
            database: Database to use

        Returns:
            Created node as dictionary
        """
        query = f"CREATE (n:{label} $props) RETURN n"
        result = self.execute_query(query, {'props': properties}, database)
        return result[0]['n'] if result else None

    def create_relationship(
        self,
        from_label: str,
        from_properties: Dict[str, Any],
        rel_type: str,
        to_label: str,
        to_properties: Dict[str, Any],
        rel_properties: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a relationship between two nodes.

        Args:
            from_label: Source node label
            from_properties: Source node match properties
            rel_type: Relationship type (e.g., "KNOWS", "PURCHASED")
            to_label: Target node label
            to_properties: Target node match properties
            rel_properties: Relationship properties (optional)
            database: Database to use

        Returns:
            Created relationship information
        """
        rel_props = rel_properties or {}

        query = f"""
        MATCH (a:{from_label}), (b:{to_label})
        WHERE a = $from_props AND b = $to_props
        CREATE (a)-[r:{rel_type} $rel_props]->(b)
        RETURN a, r, b
        """

        params = {
            'from_props': from_properties,
            'to_props': to_properties,
            'rel_props': rel_props
        }

        return self.execute_query(query, params, database)

    def find_nodes(
        self,
        label: str,
        properties: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find nodes by label and properties.

        Args:
            label: Node label to search
            properties: Properties to match (optional)
            limit: Maximum number of results
            database: Database to use

        Returns:
            List of matching nodes
        """
        where_clause = ""
        params = {}

        if properties:
            conditions = [f"n.{key} = ${key}" for key in properties.keys()]
            where_clause = "WHERE " + " AND ".join(conditions)
            params = properties

        limit_clause = f"LIMIT {limit}" if limit else ""

        query = f"MATCH (n:{label}) {where_clause} RETURN n {limit_clause}"

        result = self.execute_query(query, params, database)
        return [record['n'] for record in result]

    def find_path(
        self,
        from_label: str,
        from_properties: Dict[str, Any],
        to_label: str,
        to_properties: Dict[str, Any],
        max_depth: int = 5,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find shortest path between two nodes.

        Args:
            from_label: Source node label
            from_properties: Source node properties
            to_label: Target node label
            to_properties: Target node properties
            max_depth: Maximum path depth
            database: Database to use

        Returns:
            List of paths found
        """
        query = f"""
        MATCH (start:{from_label}), (end:{to_label})
        WHERE start = $from_props AND end = $to_props
        MATCH path = shortestPath((start)-[*..{max_depth}]-(end))
        RETURN path
        """

        params = {
            'from_props': from_properties,
            'to_props': to_properties
        }

        return self.execute_query(query, params, database)

    def delete_node(
        self,
        label: str,
        properties: Dict[str, Any],
        detach: bool = True,
        database: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete nodes matching label and properties.

        Args:
            label: Node label
            properties: Properties to match
            detach: Also delete relationships (default: True)
            database: Database to use

        Returns:
            Deletion statistics
        """
        conditions = [f"n.{key} = ${key}" for key in properties.keys()]
        where_clause = "WHERE " + " AND ".join(conditions)

        delete_cmd = "DETACH DELETE" if detach else "DELETE"
        query = f"MATCH (n:{label}) {where_clause} {delete_cmd} n"

        return self.execute_write(query, properties, database)

    def update_node(
        self,
        label: str,
        match_properties: Dict[str, Any],
        update_properties: Dict[str, Any],
        database: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update node properties.

        Args:
            label: Node label
            match_properties: Properties to match node
            update_properties: Properties to update
            database: Database to use

        Returns:
            Update statistics
        """
        match_conditions = [f"n.{key} = $match_{key}" for key in match_properties.keys()]
        where_clause = "WHERE " + " AND ".join(match_conditions)

        set_statements = [f"n.{key} = $update_{key}" for key in update_properties.keys()]
        set_clause = "SET " + ", ".join(set_statements)

        query = f"MATCH (n:{label}) {where_clause} {set_clause}"

        params = {}
        params.update({f"match_{k}": v for k, v in match_properties.items()})
        params.update({f"update_{k}": v for k, v in update_properties.items()})

        return self.execute_write(query, params, database)

    def batch_create_nodes(
        self,
        label: str,
        nodes: List[Dict[str, Any]],
        database: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create multiple nodes in a single transaction.

        Args:
            label: Node label
            nodes: List of node properties
            database: Database to use

        Returns:
            Creation statistics
        """
        query = f"""
        UNWIND $nodes AS nodeData
        CREATE (n:{label})
        SET n = nodeData
        """

        return self.execute_write(query, {'nodes': nodes}, database)

    def create_index(
        self,
        label: str,
        property_name: str,
        database: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an index on a node property.

        Args:
            label: Node label
            property_name: Property to index
            database: Database to use

        Returns:
            Index creation statistics
        """
        query = f"CREATE INDEX FOR (n:{label}) ON (n.{property_name})"
        return self.execute_write(query, database=database)

    def create_constraint(
        self,
        label: str,
        property_name: str,
        constraint_type: str = "UNIQUE",
        database: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a constraint on a node property.

        Args:
            label: Node label
            property_name: Property to constrain
            constraint_type: Type of constraint (UNIQUE, EXISTS, etc.)
            database: Database to use

        Returns:
            Constraint creation statistics
        """
        if constraint_type.upper() == "UNIQUE":
            query = f"CREATE CONSTRAINT FOR (n:{label}) REQUIRE n.{property_name} IS UNIQUE"
        elif constraint_type.upper() == "EXISTS":
            query = f"CREATE CONSTRAINT FOR (n:{label}) REQUIRE n.{property_name} IS NOT NULL"
        else:
            raise ValueError(f"Unsupported constraint type: {constraint_type}")

        return self.execute_write(query, database=database)

    def query_to_dataframe(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Execute query and return results as pandas DataFrame.

        Args:
            query: Cypher query
            parameters: Query parameters
            database: Database to use

        Returns:
            pandas DataFrame with query results
        """
        results = self.execute_query(query, parameters, database)
        return pd.DataFrame(results)

    def get_stats(self, database: Optional[str] = None) -> Dict[str, Any]:
        """
        Get database statistics.

        Args:
            database: Database to query

        Returns:
            Dictionary with database statistics
        """
        queries = {
            'node_count': "MATCH (n) RETURN count(n) as count",
            'relationship_count': "MATCH ()-[r]->() RETURN count(r) as count",
            'label_counts': "MATCH (n) RETURN labels(n) as label, count(*) as count",
            'relationship_types': "MATCH ()-[r]->() RETURN type(r) as type, count(*) as count"
        }

        stats = {}

        # Get node count
        result = self.execute_query(queries['node_count'], database=database)
        stats['total_nodes'] = result[0]['count'] if result else 0

        # Get relationship count
        result = self.execute_query(queries['relationship_count'], database=database)
        stats['total_relationships'] = result[0]['count'] if result else 0

        # Get label counts
        result = self.execute_query(queries['label_counts'], database=database)
        stats['labels'] = {str(r['label']): r['count'] for r in result}

        # Get relationship type counts
        result = self.execute_query(queries['relationship_types'], database=database)
        stats['relationship_types'] = {r['type']: r['count'] for r in result}

        return stats

    def clear_database(self, database: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete all nodes and relationships from database.

        ⚠️ WARNING: This operation is irreversible!

        Args:
            database: Database to clear

        Returns:
            Deletion statistics
        """
        query = "MATCH (n) DETACH DELETE n"
        return self.execute_write(query, database=database)

    def verify_connectivity(self) -> bool:
        """
        Verify connection to Neo4j server.

        Returns:
            True if connected, False otherwise
        """
        try:
            self.driver.verify_connectivity()
            return True
        except Exception:
            return False

    def close(self):
        """
        Close the driver and cleanup resources.
        """
        if hasattr(self, 'driver'):
            self.driver.close()


# Singleton instance getter
def get_neo4j_module(**kwargs) -> Neo4jModule:
    """
    Get the singleton Neo4j module instance.

    Args:
        **kwargs: Configuration parameters

    Returns:
        Neo4jModule instance
    """
    return Neo4jModule(**kwargs)
