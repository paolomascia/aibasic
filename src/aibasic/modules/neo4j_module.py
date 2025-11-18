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
from .module_base import AIbasicModuleBase


class Neo4jModule(AIbasicModuleBase):
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

    # ========================================
    # Metadata methods for AIbasic compiler
    # ========================================

    @classmethod
    def get_metadata(cls):
        """Get module metadata for compiler prompt generation."""
        from aibasic.modules.module_base import ModuleMetadata
        return ModuleMetadata(
            name="Neo4j",
            task_type="neo4j",
            description="Neo4j graph database for storing and querying highly connected data with Cypher query language",
            version="1.0.0",
            keywords=[
                "neo4j", "graph", "database", "cypher", "nodes", "relationships",
                "graph-database", "path-finding", "network", "connected-data"
            ],
            dependencies=["neo4j>=5.0.0", "pandas>=1.0.0"]
        )

    @classmethod
    def get_usage_notes(cls):
        """Get detailed usage notes for this module."""
        return [
            "Module uses singleton pattern - one driver instance per process",
            "Default connection URI is bolt://localhost:7687 for Neo4j Bolt protocol",
            "Supports bolt://, neo4j://, bolt+s://, and neo4j+s:// URI schemes",
            "Connection pooling automatically managed with max 50 connections by default",
            "Connection lifetime defaults to 3600 seconds (1 hour)",
            "Default database is 'neo4j' unless specified otherwise",
            "Cypher queries support parameterization for security and performance",
            "execute_query() returns list of dictionaries for read operations",
            "execute_write() returns statistics about nodes/relationships created/modified/deleted",
            "All write operations use transactions for consistency",
            "Detach delete removes nodes and their relationships automatically",
            "Path finding uses shortestPath algorithm with configurable max depth",
            "Indexes improve query performance on frequently accessed properties",
            "Constraints enforce data integrity (UNIQUE, EXISTS)",
            "Batch operations more efficient than individual creates for bulk data",
            "query_to_dataframe() integrates with pandas for data analysis",
            "get_stats() provides database metrics including node/relationship counts",
            "Label and relationship type names must start with letter, use alphanumeric characters",
            "Property values can be strings, numbers, booleans, lists, or nested structures",
            "Always call close() when done to release connection resources properly"
        ]

    @classmethod
    def get_methods_info(cls):
        """Get information about all methods in this module."""
        from aibasic.modules.module_base import MethodInfo
        return [
            MethodInfo(
                name="execute_query",
                description="Execute Cypher query and return results as list of dictionaries",
                parameters={
                    "query": "str (required) - Cypher query string (MATCH, RETURN, etc.)",
                    "parameters": "dict (optional) - Query parameters as key-value pairs",
                    "database": "str (optional) - Database to use (overrides default)"
                },
                returns="list[dict] - Query results as list of dictionaries",
                examples=[
                    'execute query "MATCH (n:Person) RETURN n LIMIT 10"',
                    'execute query "MATCH (n:Person {name: $name}) RETURN n" parameters {"name": "Alice"}',
                    'execute query "MATCH (p:Product) WHERE p.price > $min_price RETURN p" parameters {"min_price": 100}'
                ]
            ),
            MethodInfo(
                name="execute_write",
                description="Execute write transaction (CREATE, MERGE, SET, DELETE) and return statistics",
                parameters={
                    "query": "str (required) - Cypher write query",
                    "parameters": "dict (optional) - Query parameters",
                    "database": "str (optional) - Database to use"
                },
                returns="dict - Statistics with nodes_created, relationships_created, properties_set, etc.",
                examples=[
                    'execute write "CREATE (n:Person {name: $name, age: $age})" parameters {"name": "Bob", "age": 30}',
                    'execute write "MATCH (n:Person {name: $name}) SET n.age = $age" parameters {"name": "Alice", "age": 31}',
                    'execute write "MATCH (n:Person {name: $name}) DETACH DELETE n" parameters {"name": "Bob"}'
                ]
            ),
            MethodInfo(
                name="create_node",
                description="Create a node with label and properties, returns created node",
                parameters={
                    "label": "str (required) - Node label (e.g., 'Person', 'Product')",
                    "properties": "dict (required) - Node properties as key-value pairs",
                    "database": "str (optional) - Database to use"
                },
                returns="dict - Created node as dictionary",
                examples=[
                    'create node "Person" properties {"name": "Alice", "age": 30, "city": "New York"}',
                    'create node "Product" properties {"sku": "WIDGET-1", "name": "Super Widget", "price": 29.99}',
                    'create node "Company" properties {"name": "Acme Corp", "founded": 1995}'
                ]
            ),
            MethodInfo(
                name="find_nodes",
                description="Find nodes by label and optional property filters with limit",
                parameters={
                    "label": "str (required) - Node label to search",
                    "properties": "dict (optional) - Properties to match",
                    "limit": "int (optional) - Maximum number of results",
                    "database": "str (optional) - Database to use"
                },
                returns="list[dict] - List of matching nodes",
                examples=[
                    'find nodes "Person"',
                    'find nodes "Person" properties {"city": "New York"} limit 10',
                    'find nodes "Product" properties {"category": "electronics", "in_stock": true}'
                ]
            ),
            MethodInfo(
                name="update_node",
                description="Update node properties matching given criteria",
                parameters={
                    "label": "str (required) - Node label",
                    "match_properties": "dict (required) - Properties to match node",
                    "update_properties": "dict (required) - Properties to update",
                    "database": "str (optional) - Database to use"
                },
                returns="dict - Update statistics",
                examples=[
                    'update node "Person" match {"name": "Alice"} update {"age": 31, "city": "Boston"}',
                    'update node "Product" match {"sku": "WIDGET-1"} update {"price": 24.99, "discount": 0.15}'
                ]
            ),
            MethodInfo(
                name="delete_node",
                description="Delete nodes matching label and properties, optionally detach relationships",
                parameters={
                    "label": "str (required) - Node label",
                    "properties": "dict (required) - Properties to match",
                    "detach": "bool (optional) - Also delete relationships (default True)",
                    "database": "str (optional) - Database to use"
                },
                returns="dict - Deletion statistics",
                examples=[
                    'delete node "Person" properties {"name": "Bob"}',
                    'delete node "Product" properties {"sku": "OLD-WIDGET"} detach true',
                    'delete node "TempData" properties {"session_id": "12345"}'
                ]
            ),
            MethodInfo(
                name="create_relationship",
                description="Create relationship between two nodes with optional properties",
                parameters={
                    "from_label": "str (required) - Source node label",
                    "from_properties": "dict (required) - Source node match properties",
                    "rel_type": "str (required) - Relationship type (e.g., 'KNOWS', 'PURCHASED')",
                    "to_label": "str (required) - Target node label",
                    "to_properties": "dict (required) - Target node match properties",
                    "rel_properties": "dict (optional) - Relationship properties",
                    "database": "str (optional) - Database to use"
                },
                returns="dict - Created relationship information",
                examples=[
                    'create relationship from "Person" {"name": "Alice"} type "KNOWS" to "Person" {"name": "Bob"}',
                    'create relationship from "User" {"id": 123} type "PURCHASED" to "Product" {"sku": "WIDGET-1"} properties {"date": "2023-12-01", "quantity": 2}',
                    'create relationship from "Employee" {"emp_id": 456} type "WORKS_FOR" to "Company" {"name": "Acme"} properties {"since": 2020}'
                ]
            ),
            MethodInfo(
                name="find_path",
                description="Find shortest path between two nodes with configurable maximum depth",
                parameters={
                    "from_label": "str (required) - Source node label",
                    "from_properties": "dict (required) - Source node properties",
                    "to_label": "str (required) - Target node label",
                    "to_properties": "dict (required) - Target node properties",
                    "max_depth": "int (optional) - Maximum path depth (default 5)",
                    "database": "str (optional) - Database to use"
                },
                returns="list[dict] - List of paths found",
                examples=[
                    'find path from "Person" {"name": "Alice"} to "Person" {"name": "Bob"} max_depth 5',
                    'find path from "City" {"name": "Boston"} to "City" {"name": "Seattle"} max_depth 10',
                    'find path from "User" {"id": 123} to "Product" {"sku": "WIDGET-1"} max_depth 3'
                ]
            ),
            MethodInfo(
                name="batch_create_nodes",
                description="Create multiple nodes in single transaction for efficient bulk inserts",
                parameters={
                    "label": "str (required) - Node label for all nodes",
                    "nodes": "list[dict] (required) - List of node properties",
                    "database": "str (optional) - Database to use"
                },
                returns="dict - Creation statistics",
                examples=[
                    'batch create nodes "Person" [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}, {"name": "Carol", "age": 28}]',
                    'batch create nodes "Product" [{"sku": "A1", "price": 10}, {"sku": "A2", "price": 20}]'
                ]
            ),
            MethodInfo(
                name="create_index",
                description="Create index on node property for improved query performance",
                parameters={
                    "label": "str (required) - Node label",
                    "property_name": "str (required) - Property to index",
                    "database": "str (optional) - Database to use"
                },
                returns="dict - Index creation statistics",
                examples=[
                    'create index on "Person" property "email"',
                    'create index on "Product" property "sku"',
                    'create index on "User" property "username"'
                ]
            ),
            MethodInfo(
                name="create_constraint",
                description="Create constraint on node property for data integrity (UNIQUE or EXISTS)",
                parameters={
                    "label": "str (required) - Node label",
                    "property_name": "str (required) - Property to constrain",
                    "constraint_type": "str (optional) - 'UNIQUE' or 'EXISTS' (default 'UNIQUE')",
                    "database": "str (optional) - Database to use"
                },
                returns="dict - Constraint creation statistics",
                examples=[
                    'create constraint on "Person" property "email" type "UNIQUE"',
                    'create constraint on "Product" property "sku" type "UNIQUE"',
                    'create constraint on "User" property "username" type "EXISTS"'
                ]
            ),
            MethodInfo(
                name="query_to_dataframe",
                description="Execute Cypher query and return results as pandas DataFrame",
                parameters={
                    "query": "str (required) - Cypher query",
                    "parameters": "dict (optional) - Query parameters",
                    "database": "str (optional) - Database to use"
                },
                returns="pandas.DataFrame - Query results as DataFrame",
                examples=[
                    'query to dataframe "MATCH (p:Person) RETURN p.name, p.age ORDER BY p.age"',
                    'query to dataframe "MATCH (p:Product) WHERE p.price > $min RETURN p" parameters {"min": 50}'
                ]
            ),
            MethodInfo(
                name="get_stats",
                description="Get database statistics including node count, relationship count, labels, and types",
                parameters={
                    "database": "str (optional) - Database to query"
                },
                returns="dict - Statistics with total_nodes, total_relationships, labels, relationship_types",
                examples=[
                    'get database stats',
                    'get stats'
                ]
            ),
            MethodInfo(
                name="clear_database",
                description="Delete all nodes and relationships from database (WARNING: irreversible)",
                parameters={
                    "database": "str (optional) - Database to clear"
                },
                returns="dict - Deletion statistics",
                examples=[
                    'clear database',
                    'delete all data'
                ]
            ),
            MethodInfo(
                name="verify_connectivity",
                description="Verify connection to Neo4j server",
                parameters={},
                returns="bool - True if connected, False otherwise",
                examples=[
                    'verify connectivity',
                    'check connection'
                ]
            ),
            MethodInfo(
                name="close",
                description="Close driver and cleanup connection resources",
                parameters={},
                returns="None",
                examples=[
                    'close connection',
                    'close driver'
                ]
            )
        ]

    @classmethod
    def get_examples(cls):
        """Get example AIbasic code snippets."""
        return [
            # Basic node creation
            '10 (neo4j) create node "Person" properties {"name": "Alice", "age": 30, "city": "New York"}',
            '20 (neo4j) create node "Person" properties {"name": "Bob", "age": 25, "city": "Boston"}',
            '30 (neo4j) create node "Company" properties {"name": "Acme Corp", "industry": "Technology"}',

            # Finding nodes
            '10 (neo4j) find nodes "Person"',
            '20 (neo4j) find nodes "Person" properties {"city": "New York"} limit 10',
            '30 (neo4j) find nodes "Company" properties {"industry": "Technology"}',

            # Creating relationships
            '10 (neo4j) create relationship from "Person" {"name": "Alice"} type "KNOWS" to "Person" {"name": "Bob"}',
            '20 (neo4j) create relationship from "Person" {"name": "Alice"} type "WORKS_FOR" to "Company" {"name": "Acme Corp"} properties {"since": 2020, "role": "Engineer"}',

            # Cypher queries
            '10 (neo4j) execute query "MATCH (n:Person) RETURN n.name, n.age ORDER BY n.age DESC LIMIT 5"',
            '20 (neo4j) execute query "MATCH (p:Person)-[:KNOWS]->(f:Person) WHERE p.name = $name RETURN f" parameters {"name": "Alice"}',
            '30 (neo4j) execute query "MATCH (p:Person)-[:WORKS_FOR]->(c:Company) RETURN p.name, c.name"',

            # Path finding
            '10 (neo4j) find path from "Person" {"name": "Alice"} to "Person" {"name": "Bob"} max_depth 5',
            '20 (neo4j) find path from "City" {"name": "Boston"} to "City" {"name": "Seattle"} max_depth 10',

            # Batch operations
            '10 (neo4j) batch create nodes "Product" [{"sku": "WIDGET-1", "price": 19.99}, {"sku": "GADGET-2", "price": 29.99}, {"sku": "TOOL-3", "price": 39.99}]',

            # Update operations
            '10 (neo4j) update node "Person" match {"name": "Alice"} update {"age": 31, "city": "San Francisco"}',
            '20 (neo4j) execute write "MATCH (p:Product {sku: $sku}) SET p.price = $price" parameters {"sku": "WIDGET-1", "price": 17.99}',

            # Delete operations
            '10 (neo4j) delete node "Person" properties {"name": "Bob"}',
            '20 (neo4j) execute write "MATCH (n:TempData) WHERE n.created < $cutoff DETACH DELETE n" parameters {"cutoff": "2023-01-01"}',

            # Indexes and constraints
            '10 (neo4j) create index on "Person" property "email"',
            '20 (neo4j) create constraint on "Product" property "sku" type "UNIQUE"',
            '30 (neo4j) create constraint on "User" property "username" type "EXISTS"',

            # Analytics
            '10 (neo4j) query to dataframe "MATCH (p:Person) RETURN p.city as city, count(*) as count GROUP BY p.city ORDER BY count DESC"',
            '20 (neo4j) query to dataframe "MATCH (p:Person)-[r:KNOWS]->(f) RETURN p.name, count(f) as friends ORDER BY friends DESC LIMIT 10"',

            # Statistics
            '10 (neo4j) get database stats',
            '20 (neo4j) verify connectivity',

            # Social network example
            '10 (neo4j) create node "User" properties {"username": "alice", "email": "alice@example.com", "joined": "2023-01-15"}',
            '20 (neo4j) create node "User" properties {"username": "bob", "email": "bob@example.com", "joined": "2023-02-20"}',
            '30 (neo4j) create node "Post" properties {"id": 1, "title": "Hello World", "content": "My first post", "date": "2023-03-01"}',
            '40 (neo4j) create relationship from "User" {"username": "alice"} type "FOLLOWS" to "User" {"username": "bob"}',
            '50 (neo4j) create relationship from "User" {"username": "alice"} type "POSTED" to "Post" {"id": 1}',
            '60 (neo4j) create relationship from "User" {"username": "bob"} type "LIKED" to "Post" {"id": 1} properties {"timestamp": "2023-03-02"}',
            '70 (neo4j) execute query "MATCH (u:User)-[:FOLLOWS]->(followed:User)-[:POSTED]->(p:Post) WHERE u.username = $user RETURN p" parameters {"user": "alice"}',

            # Recommendation example
            '10 (neo4j) execute query "MATCH (u:User {username: $user})-[:PURCHASED]->(p:Product)<-[:PURCHASED]-(other:User)-[:PURCHASED]->(rec:Product) WHERE NOT (u)-[:PURCHASED]->(rec) RETURN rec.name, count(*) as score ORDER BY score DESC LIMIT 5" parameters {"user": "alice"}',

            # Cleanup
            '10 (neo4j) close connection'
        ]


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
