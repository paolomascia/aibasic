"""
Elasticsearch Module for AIbasic

This module provides integration with Elasticsearch, a distributed search and analytics engine
for full-text search, log analytics, and real-time data processing.

Features:
- Index management (create, delete, update settings)
- Document operations (index, update, delete, get)
- Search with Query DSL
- Bulk operations for high performance
- Aggregations and analytics
- Mapping management
- Alias management
- DataFrame integration
- Template management
- Snapshot and restore

Author: AIbasic Team
Version: 1.0
"""

import threading
from typing import Any, Dict, List, Optional, Union
import pandas as pd
import json
from .module_base import AIbasicModuleBase


class ElasticsearchModule(AIbasicModuleBase):
    """
    Elasticsearch module for AIbasic programs.

    Provides integration with Elasticsearch for full-text search,
    log analytics, and real-time data processing.

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
        hosts: Union[str, List[str]] = "http://localhost:9200",
        username: str = None,
        password: str = None,
        api_key: str = None,
        verify_certs: bool = True,
        ca_certs: str = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_on_timeout: bool = True,
        **kwargs
    ):
        """
        Initialize the Elasticsearch module.

        Args:
            hosts: Elasticsearch host(s) URL(s)
            username: Username for authentication
            password: Password for authentication
            api_key: API key for authentication (alternative to username/password)
            verify_certs: Verify SSL certificates
            ca_certs: Path to CA certificate bundle
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            retry_on_timeout: Retry on timeout
            **kwargs: Additional Elasticsearch client parameters
        """
        if self._initialized:
            return

        try:
            from elasticsearch import Elasticsearch
            from elasticsearch.exceptions import (
                ConnectionError,
                AuthenticationException,
                NotFoundError
            )
        except ImportError:
            raise ImportError(
                "elasticsearch package is required. Install with: pip install elasticsearch"
            )

        # Store exception classes
        self.ConnectionError = ConnectionError
        self.AuthenticationException = AuthenticationException
        self.NotFoundError = NotFoundError

        # Parse hosts
        if isinstance(hosts, str):
            hosts = [hosts]

        # Setup authentication
        auth_params = {}
        if api_key:
            auth_params['api_key'] = api_key
        elif username and password:
            auth_params['basic_auth'] = (username, password)

        # Create Elasticsearch client
        self.client = Elasticsearch(
            hosts=hosts,
            verify_certs=verify_certs,
            ca_certs=ca_certs,
            timeout=timeout,
            max_retries=max_retries,
            retry_on_timeout=retry_on_timeout,
            **auth_params,
            **kwargs
        )

        # State variables
        self.last_query = None
        self.last_result = None

        self._initialized = True

    def ping(self) -> bool:
        """
        Check if Elasticsearch cluster is accessible.

        Returns:
            True if cluster responds, False otherwise
        """
        try:
            return self.client.ping()
        except Exception:
            return False

    def info(self) -> Dict[str, Any]:
        """
        Get cluster information.

        Returns:
            Dictionary with cluster info
        """
        try:
            return self.client.info()
        except Exception as e:
            return {'error': str(e)}

    def create_index(
        self,
        index: str,
        mappings: Optional[Dict[str, Any]] = None,
        settings: Optional[Dict[str, Any]] = None,
        aliases: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an index.

        Args:
            index: Index name
            mappings: Index mappings (field types)
            settings: Index settings (shards, replicas, etc.)
            aliases: Index aliases

        Returns:
            Dictionary with creation result
        """
        try:
            body = {}
            if mappings:
                body['mappings'] = mappings
            if settings:
                body['settings'] = settings
            if aliases:
                body['aliases'] = aliases

            result = self.client.indices.create(index=index, body=body if body else None)
            return {'success': True, 'acknowledged': result.get('acknowledged', False)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete_index(self, index: str) -> Dict[str, Any]:
        """
        Delete an index.

        Args:
            index: Index name (supports wildcards)

        Returns:
            Dictionary with deletion result
        """
        try:
            result = self.client.indices.delete(index=index)
            return {'success': True, 'acknowledged': result.get('acknowledged', False)}
        except self.NotFoundError:
            return {'success': False, 'error': f'Index {index} not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def index_exists(self, index: str) -> bool:
        """
        Check if an index exists.

        Args:
            index: Index name

        Returns:
            True if exists, False otherwise
        """
        try:
            return self.client.indices.exists(index=index)
        except Exception:
            return False

    def index_document(
        self,
        index: str,
        document: Dict[str, Any],
        doc_id: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Index a document.

        Args:
            index: Index name
            document: Document to index
            doc_id: Document ID (auto-generated if None)
            refresh: Refresh index after operation

        Returns:
            Dictionary with index result
        """
        try:
            result = self.client.index(
                index=index,
                document=document,
                id=doc_id,
                refresh=refresh
            )
            return {
                'success': True,
                'id': result['_id'],
                'version': result['_version'],
                'result': result['result']
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def bulk_index(
        self,
        index: str,
        documents: List[Dict[str, Any]],
        id_field: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Bulk index multiple documents.

        Args:
            index: Index name
            documents: List of documents
            id_field: Field to use as document ID (optional)
            refresh: Refresh index after operation

        Returns:
            Dictionary with bulk result
        """
        try:
            from elasticsearch.helpers import bulk

            actions = []
            for doc in documents:
                action = {
                    '_index': index,
                    '_source': doc
                }
                if id_field and id_field in doc:
                    action['_id'] = doc[id_field]

                actions.append(action)

            success, failed = bulk(
                self.client,
                actions,
                refresh=refresh,
                raise_on_error=False
            )

            return {
                'success': True,
                'successful': success,
                'failed': failed,
                'total': len(documents)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_document(
        self,
        index: str,
        doc_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.

        Args:
            index: Index name
            doc_id: Document ID

        Returns:
            Document if found, None otherwise
        """
        try:
            result = self.client.get(index=index, id=doc_id)
            return result['_source']
        except self.NotFoundError:
            return None
        except Exception as e:
            return {'error': str(e)}

    def update_document(
        self,
        index: str,
        doc_id: str,
        document: Dict[str, Any],
        refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Update a document.

        Args:
            index: Index name
            doc_id: Document ID
            document: Fields to update
            refresh: Refresh index after operation

        Returns:
            Dictionary with update result
        """
        try:
            result = self.client.update(
                index=index,
                id=doc_id,
                doc=document,
                refresh=refresh
            )
            return {
                'success': True,
                'version': result['_version'],
                'result': result['result']
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete_document(
        self,
        index: str,
        doc_id: str,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Delete a document.

        Args:
            index: Index name
            doc_id: Document ID
            refresh: Refresh index after operation

        Returns:
            Dictionary with deletion result
        """
        try:
            result = self.client.delete(
                index=index,
                id=doc_id,
                refresh=refresh
            )
            return {
                'success': True,
                'result': result['result']
            }
        except self.NotFoundError:
            return {'success': False, 'error': 'Document not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def search(
        self,
        index: str,
        query: Optional[Dict[str, Any]] = None,
        size: int = 10,
        from_: int = 0,
        sort: Optional[List] = None,
        source: Optional[Union[bool, List[str]]] = None,
        aggs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search documents.

        Args:
            index: Index name (supports wildcards)
            query: Query DSL (match_all if None)
            size: Number of results to return
            from_: Offset for pagination
            sort: Sort specification
            source: Fields to return
            aggs: Aggregations

        Returns:
            Dictionary with search results
        """
        try:
            body = {}

            if query:
                body['query'] = query
            else:
                body['query'] = {'match_all': {}}

            if aggs:
                body['aggs'] = aggs

            result = self.client.search(
                index=index,
                body=body,
                size=size,
                from_=from_,
                sort=sort,
                _source=source
            )

            self.last_query = body
            self.last_result = result

            hits = [hit['_source'] for hit in result['hits']['hits']]

            response = {
                'success': True,
                'hits': hits,
                'total': result['hits']['total']['value'],
                'max_score': result['hits'].get('max_score')
            }

            if aggs:
                response['aggregations'] = result.get('aggregations', {})

            return response

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def search_df(
        self,
        index: str,
        query: Optional[Dict[str, Any]] = None,
        size: int = 10000
    ) -> pd.DataFrame:
        """
        Search and return results as DataFrame.

        Args:
            index: Index name
            query: Query DSL
            size: Maximum number of results

        Returns:
            pandas DataFrame with results
        """
        result = self.search(index, query, size=size)
        if result.get('success'):
            return pd.DataFrame(result['hits'])
        else:
            return pd.DataFrame()

    def count(
        self,
        index: str,
        query: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count documents matching query.

        Args:
            index: Index name
            query: Query DSL (all documents if None)

        Returns:
            Number of matching documents
        """
        try:
            body = {}
            if query:
                body['query'] = query

            result = self.client.count(index=index, body=body if body else None)
            return result['count']
        except Exception:
            return 0

    def delete_by_query(
        self,
        index: str,
        query: Dict[str, Any],
        refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Delete documents matching query.

        Args:
            index: Index name
            query: Query DSL
            refresh: Refresh index after operation

        Returns:
            Dictionary with deletion result
        """
        try:
            result = self.client.delete_by_query(
                index=index,
                body={'query': query},
                refresh=refresh
            )
            return {
                'success': True,
                'deleted': result['deleted'],
                'total': result['total']
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_by_query(
        self,
        index: str,
        query: Dict[str, Any],
        script: Dict[str, Any],
        refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Update documents matching query.

        Args:
            index: Index name
            query: Query DSL
            script: Update script
            refresh: Refresh index after operation

        Returns:
            Dictionary with update result
        """
        try:
            result = self.client.update_by_query(
                index=index,
                body={
                    'query': query,
                    'script': script
                },
                refresh=refresh
            )
            return {
                'success': True,
                'updated': result['updated'],
                'total': result['total']
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def put_mapping(
        self,
        index: str,
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update index mapping.

        Args:
            index: Index name
            properties: Field mappings

        Returns:
            Dictionary with result
        """
        try:
            result = self.client.indices.put_mapping(
                index=index,
                body={'properties': properties}
            )
            return {'success': True, 'acknowledged': result.get('acknowledged', False)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def refresh_index(self, index: str) -> Dict[str, Any]:
        """
        Refresh an index to make recent changes searchable.

        Args:
            index: Index name

        Returns:
            Dictionary with refresh result
        """
        try:
            self.client.indices.refresh(index=index)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def create_alias(
        self,
        index: str,
        alias: str
    ) -> Dict[str, Any]:
        """
        Create an alias for an index.

        Args:
            index: Index name
            alias: Alias name

        Returns:
            Dictionary with result
        """
        try:
            result = self.client.indices.put_alias(index=index, name=alias)
            return {'success': True, 'acknowledged': result.get('acknowledged', False)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_cluster_health(self) -> Dict[str, Any]:
        """
        Get cluster health status.

        Returns:
            Dictionary with cluster health information
        """
        try:
            return self.client.cluster.health()
        except Exception as e:
            return {'error': str(e)}

    def get_index_stats(self, index: str) -> Dict[str, Any]:
        """
        Get index statistics.

        Args:
            index: Index name

        Returns:
            Dictionary with index stats
        """
        try:
            return self.client.indices.stats(index=index)
        except Exception as e:
            return {'error': str(e)}

    def close(self):
        """
        Close the Elasticsearch client connection.
        """
        if hasattr(self, 'client'):
            self.client.close()

    @classmethod
    def get_metadata(cls):
        """Get module metadata."""
        from aibasic.modules.module_base import ModuleMetadata
        return ModuleMetadata(
            name="Elasticsearch",
            task_type="elasticsearch",
            description="Distributed search and analytics engine for full-text search, log analytics, and real-time data processing with Query DSL support",
            version="1.0.0",
            keywords=["elasticsearch", "search", "analytics", "fulltext", "logs", "query-dsl", "aggregations", "index", "document", "bulk"],
            dependencies=[
                "elasticsearch>=8.0.0",
                "pandas>=1.3.0"
            ]
        )

    @classmethod
    def get_usage_notes(cls):
        """Get detailed usage notes."""
        return [
            "Module uses singleton pattern - one instance shared across operations",
            "Supports multiple authentication methods: basic auth (username/password) or API key",
            "Can connect to single node or cluster with multiple hosts for high availability",
            "All document operations support optional 'refresh' parameter to make changes immediately searchable",
            "Index names support wildcards (e.g., 'logs-*') for multi-index operations",
            "Query DSL uses nested dictionaries matching Elasticsearch JSON syntax",
            "Bulk operations are highly efficient - use for indexing large numbers of documents",
            "Aggregations run alongside search queries to compute metrics, statistics, and analytics",
            "Document IDs are auto-generated if not provided during indexing",
            "The 'size' parameter controls pagination - max recommended is 10,000 per request",
            "Use 'from_' parameter for pagination offset (0-based)",
            "SSL certificate verification can be disabled for development but should be enabled in production",
            "Mappings define field types (text, keyword, integer, date, etc.) and cannot be changed for existing fields",
            "Aliases provide abstraction over index names - useful for zero-downtime reindexing",
            "Use search_df() method to get results as pandas DataFrame for data analysis",
            "The module stores last_query and last_result for debugging and inspection",
            "Refresh operation makes recent changes searchable but has performance cost - use sparingly",
            "Count operations are faster than search when you only need document counts"
        ]

    @classmethod
    def get_methods_info(cls):
        """Get information about module methods."""
        from aibasic.modules.module_base import MethodInfo
        return [
            MethodInfo(
                name="ping",
                description="Check if Elasticsearch cluster is accessible and responding",
                parameters={},
                returns="Boolean: True if cluster responds, False otherwise",
                examples=[
                    '(elasticsearch) ping cluster',
                    '(elasticsearch) check if elasticsearch is available'
                ]
            ),
            MethodInfo(
                name="info",
                description="Get detailed cluster information including version, name, and configuration",
                parameters={},
                returns="Dictionary with cluster information",
                examples=[
                    '(elasticsearch) get cluster info',
                    '(elasticsearch) show elasticsearch version and details'
                ]
            ),
            MethodInfo(
                name="create_index",
                description="Create a new index with optional mappings, settings, and aliases",
                parameters={
                    "index": "Index name to create",
                    "mappings": "Field type definitions (optional, dict with 'properties' defining field types)",
                    "settings": "Index settings like number of shards and replicas (optional, dict)",
                    "aliases": "Index aliases (optional, dict)"
                },
                returns="Dictionary with success status and acknowledgement",
                examples=[
                    '(elasticsearch) create index "products"',
                    '(elasticsearch) create index "logs" with mappings {"properties": {"timestamp": {"type": "date"}, "message": {"type": "text"}}}',
                    '(elasticsearch) create index "users" with settings {"number_of_shards": 3, "number_of_replicas": 2}',
                    '(elasticsearch) create index "events" with mappings {"properties": {"level": {"type": "keyword"}}} and aliases {"current": {}}'
                ]
            ),
            MethodInfo(
                name="delete_index",
                description="Delete an index (supports wildcards for deleting multiple indices)",
                parameters={
                    "index": "Index name to delete (supports wildcards like 'logs-*')"
                },
                returns="Dictionary with success status and acknowledgement",
                examples=[
                    '(elasticsearch) delete index "old-logs"',
                    '(elasticsearch) delete index "test-*"',
                    '(elasticsearch) remove index "temporary"'
                ]
            ),
            MethodInfo(
                name="index_exists",
                description="Check if an index exists in the cluster",
                parameters={
                    "index": "Index name to check"
                },
                returns="Boolean: True if index exists, False otherwise",
                examples=[
                    '(elasticsearch) check if index "products" exists',
                    '(elasticsearch) does index "users" exist'
                ]
            ),
            MethodInfo(
                name="index_document",
                description="Index a single document into an index (create or update)",
                parameters={
                    "index": "Index name",
                    "document": "Document data as dictionary",
                    "doc_id": "Document ID (optional, auto-generated if not provided)",
                    "refresh": "Refresh index immediately to make document searchable (default: False)"
                },
                returns="Dictionary with document ID, version, and result (created/updated)",
                examples=[
                    '(elasticsearch) index document {"name": "John", "age": 30} into index "users"',
                    '(elasticsearch) index document {"product": "laptop", "price": 999} with id "prod-123" into index "products"',
                    '(elasticsearch) index document {"message": "error occurred", "level": "ERROR"} into index "logs" with refresh True'
                ]
            ),
            MethodInfo(
                name="bulk_index",
                description="Bulk index multiple documents efficiently in a single request",
                parameters={
                    "index": "Index name",
                    "documents": "List of document dictionaries to index",
                    "id_field": "Field name to use as document ID (optional)",
                    "refresh": "Refresh index after bulk operation (default: False)"
                },
                returns="Dictionary with successful count, failed count, and total",
                examples=[
                    '(elasticsearch) bulk index documents [{"name": "Alice"}, {"name": "Bob"}] into index "users"',
                    '(elasticsearch) bulk index documents from list with id_field "user_id" into index "accounts"',
                    '(elasticsearch) index 1000 documents into index "logs" with refresh True'
                ]
            ),
            MethodInfo(
                name="get_document",
                description="Retrieve a document by its ID from an index",
                parameters={
                    "index": "Index name",
                    "doc_id": "Document ID to retrieve"
                },
                returns="Document dictionary if found, None if not found, or error dict",
                examples=[
                    '(elasticsearch) get document "user-123" from index "users"',
                    '(elasticsearch) retrieve document with id "prod-456" from index "products"',
                    '(elasticsearch) fetch document "event-789" from index "events"'
                ]
            ),
            MethodInfo(
                name="update_document",
                description="Update specific fields of an existing document",
                parameters={
                    "index": "Index name",
                    "doc_id": "Document ID to update",
                    "document": "Dictionary with fields to update (partial document)",
                    "refresh": "Refresh index immediately (default: False)"
                },
                returns="Dictionary with version and result status",
                examples=[
                    '(elasticsearch) update document "user-123" in index "users" with {"age": 31}',
                    '(elasticsearch) update document "prod-456" with {"price": 899, "stock": 50} in index "products"',
                    '(elasticsearch) update document "event-789" set {"status": "processed"} with refresh True'
                ]
            ),
            MethodInfo(
                name="delete_document",
                description="Delete a document by its ID from an index",
                parameters={
                    "index": "Index name",
                    "doc_id": "Document ID to delete",
                    "refresh": "Refresh index immediately (default: False)"
                },
                returns="Dictionary with success status and result",
                examples=[
                    '(elasticsearch) delete document "user-123" from index "users"',
                    '(elasticsearch) remove document "old-event" from index "events"',
                    '(elasticsearch) delete document "temp-456" from index "temporary" with refresh True'
                ]
            ),
            MethodInfo(
                name="search",
                description="Search documents using Elasticsearch Query DSL with support for pagination, sorting, and aggregations",
                parameters={
                    "index": "Index name (supports wildcards like 'logs-*')",
                    "query": "Query DSL dictionary (optional, defaults to match_all)",
                    "size": "Number of results to return (default: 10, max recommended: 10000)",
                    "from_": "Offset for pagination (default: 0)",
                    "sort": "Sort specification list (optional)",
                    "source": "Fields to return - True/False or list of field names (optional)",
                    "aggs": "Aggregations dictionary (optional)"
                },
                returns="Dictionary with hits list, total count, max_score, and optional aggregations",
                examples=[
                    '(elasticsearch) search index "products"',
                    '(elasticsearch) search index "users" with query {"match": {"name": "john"}}',
                    '(elasticsearch) search index "logs" with query {"range": {"timestamp": {"gte": "2024-01-01"}}} size 100',
                    '(elasticsearch) search index "events" with query {"term": {"level": "ERROR"}} and aggs {"by_type": {"terms": {"field": "type.keyword"}}}',
                    '(elasticsearch) search index "products" sort [{"price": "asc"}] size 20',
                    '(elasticsearch) search index "users" from 50 size 10 source ["name", "email"]'
                ]
            ),
            MethodInfo(
                name="search_df",
                description="Search documents and return results as pandas DataFrame for data analysis",
                parameters={
                    "index": "Index name",
                    "query": "Query DSL dictionary (optional, defaults to match_all)",
                    "size": "Maximum number of results (default: 10000)"
                },
                returns="pandas DataFrame with search results",
                examples=[
                    '(elasticsearch) search index "products" as dataframe',
                    '(elasticsearch) search index "logs" with query {"match": {"level": "ERROR"}} as dataframe',
                    '(elasticsearch) get all documents from index "users" as dataframe with size 50000'
                ]
            ),
            MethodInfo(
                name="count",
                description="Count documents matching a query (faster than search when only count is needed)",
                parameters={
                    "index": "Index name",
                    "query": "Query DSL dictionary (optional, counts all documents if omitted)"
                },
                returns="Integer: number of matching documents",
                examples=[
                    '(elasticsearch) count documents in index "users"',
                    '(elasticsearch) count documents in index "logs" matching query {"term": {"level": "ERROR"}}',
                    '(elasticsearch) count index "products" where query {"range": {"price": {"lt": 100}}}'
                ]
            ),
            MethodInfo(
                name="delete_by_query",
                description="Delete all documents matching a query",
                parameters={
                    "index": "Index name",
                    "query": "Query DSL dictionary specifying which documents to delete",
                    "refresh": "Refresh index immediately (default: False)"
                },
                returns="Dictionary with deleted count and total processed",
                examples=[
                    '(elasticsearch) delete documents from index "logs" where query {"range": {"timestamp": {"lt": "2023-01-01"}}}',
                    '(elasticsearch) delete from index "users" matching query {"term": {"status": "inactive"}}',
                    '(elasticsearch) delete documents in index "temp" where query {"match_all": {}} with refresh True'
                ]
            ),
            MethodInfo(
                name="update_by_query",
                description="Update all documents matching a query using a script",
                parameters={
                    "index": "Index name",
                    "query": "Query DSL dictionary specifying which documents to update",
                    "script": "Update script dictionary (e.g., {'source': 'ctx._source.field++'})",
                    "refresh": "Refresh index immediately (default: False)"
                },
                returns="Dictionary with updated count and total processed",
                examples=[
                    '(elasticsearch) update documents in index "products" matching query {"term": {"category": "electronics"}} with script {"source": "ctx._source.price *= 1.1"}',
                    '(elasticsearch) update index "users" where query {"match_all": {}} with script {"source": "ctx._source.updated_at = params.now", "params": {"now": "2024-01-01"}}',
                    '(elasticsearch) update documents matching query {"range": {"views": {"lt": 10}}} with script {"source": "ctx._source.views = 0"} and refresh True'
                ]
            ),
            MethodInfo(
                name="put_mapping",
                description="Add new fields to index mapping (cannot modify existing field types)",
                parameters={
                    "index": "Index name",
                    "properties": "Dictionary defining new field mappings"
                },
                returns="Dictionary with success status and acknowledgement",
                examples=[
                    '(elasticsearch) put mapping for index "users" with properties {"phone": {"type": "keyword"}}',
                    '(elasticsearch) add mapping to index "products" properties {"tags": {"type": "keyword"}, "rating": {"type": "float"}}',
                    '(elasticsearch) update mapping for index "logs" add properties {"source_ip": {"type": "ip"}}'
                ]
            ),
            MethodInfo(
                name="refresh_index",
                description="Refresh index to make recent changes immediately searchable (has performance cost)",
                parameters={
                    "index": "Index name to refresh"
                },
                returns="Dictionary with success status",
                examples=[
                    '(elasticsearch) refresh index "products"',
                    '(elasticsearch) refresh index "logs" to make changes searchable',
                    '(elasticsearch) force refresh on index "users"'
                ]
            ),
            MethodInfo(
                name="create_alias",
                description="Create an alias pointing to an index (useful for zero-downtime reindexing)",
                parameters={
                    "index": "Index name",
                    "alias": "Alias name to create"
                },
                returns="Dictionary with success status and acknowledgement",
                examples=[
                    '(elasticsearch) create alias "current_products" for index "products_v2"',
                    '(elasticsearch) add alias "active_logs" to index "logs-2024-01"',
                    '(elasticsearch) create alias "users" pointing to index "users_production"'
                ]
            ),
            MethodInfo(
                name="get_cluster_health",
                description="Get cluster health status including status color (green/yellow/red), node counts, and shard information",
                parameters={},
                returns="Dictionary with cluster health details",
                examples=[
                    '(elasticsearch) get cluster health',
                    '(elasticsearch) check cluster status',
                    '(elasticsearch) show cluster health information'
                ]
            ),
            MethodInfo(
                name="get_index_stats",
                description="Get detailed statistics for an index including document count, storage size, and performance metrics",
                parameters={
                    "index": "Index name"
                },
                returns="Dictionary with comprehensive index statistics",
                examples=[
                    '(elasticsearch) get stats for index "products"',
                    '(elasticsearch) show index statistics for "logs"',
                    '(elasticsearch) get index "users" stats and metrics'
                ]
            )
        ]

    @classmethod
    def get_examples(cls):
        """Get AIbasic usage examples."""
        return [
            # Basic connectivity
            '10 (elasticsearch) ping cluster',
            '20 (elasticsearch) get cluster info',
            '30 (elasticsearch) get cluster health',

            # Index management
            '40 (elasticsearch) create index "products"',
            '50 (elasticsearch) create index "logs" with mappings {"properties": {"timestamp": {"type": "date"}, "message": {"type": "text"}, "level": {"type": "keyword"}}}',
            '60 (elasticsearch) create index "users" with settings {"number_of_shards": 3, "number_of_replicas": 1}',
            '70 (elasticsearch) check if index "products" exists',
            '80 (elasticsearch) delete index "old-logs"',
            '90 (elasticsearch) get stats for index "products"',

            # Document operations
            '100 (elasticsearch) index document {"name": "Laptop", "price": 999, "category": "electronics"} into index "products"',
            '110 (elasticsearch) index document {"user": "john", "email": "john@example.com"} with id "user-123" into index "users"',
            '120 (elasticsearch) get document "user-123" from index "users"',
            '130 (elasticsearch) update document "user-123" in index "users" with {"age": 30, "city": "NYC"}',
            '140 (elasticsearch) delete document "user-456" from index "users"',

            # Bulk operations
            '150 (elasticsearch) bulk index documents [{"name": "Alice"}, {"name": "Bob"}, {"name": "Charlie"}] into index "users"',
            '160 (elasticsearch) bulk index 1000 documents into index "logs" with id_field "event_id" and refresh True',

            # Search operations
            '170 (elasticsearch) search index "products"',
            '180 (elasticsearch) search index "products" with query {"match": {"name": "laptop"}} size 20',
            '190 (elasticsearch) search index "users" with query {"term": {"city.keyword": "NYC"}}',
            '200 (elasticsearch) search index "logs" with query {"range": {"timestamp": {"gte": "2024-01-01", "lt": "2024-02-01"}}} size 100',
            '210 (elasticsearch) search index "products" with query {"bool": {"must": [{"match": {"category": "electronics"}}, {"range": {"price": {"lt": 1000}}}]}}',
            '220 (elasticsearch) search index "products" sort [{"price": "asc"}] size 50',
            '230 (elasticsearch) search index "users" from 100 size 20 source ["name", "email"]',

            # Aggregations
            '240 (elasticsearch) search index "products" with aggs {"avg_price": {"avg": {"field": "price"}}, "by_category": {"terms": {"field": "category.keyword"}}}',
            '250 (elasticsearch) search index "logs" with query {"match_all": {}} and aggs {"errors_per_day": {"date_histogram": {"field": "timestamp", "interval": "day"}}}',

            # DataFrame integration
            '260 (elasticsearch) search index "products" as dataframe',
            '270 (elasticsearch) search index "logs" with query {"term": {"level": "ERROR"}} as dataframe with size 10000',

            # Count operations
            '280 (elasticsearch) count documents in index "users"',
            '290 (elasticsearch) count documents in index "logs" matching query {"term": {"level": "ERROR"}}',

            # Batch updates/deletes
            '300 (elasticsearch) delete documents from index "logs" where query {"range": {"timestamp": {"lt": "2023-01-01"}}}',
            '310 (elasticsearch) update documents in index "products" matching query {"term": {"category": "electronics"}} with script {"source": "ctx._source.price *= 0.9"}',

            # Mapping and aliases
            '320 (elasticsearch) put mapping for index "users" with properties {"phone": {"type": "keyword"}, "age": {"type": "integer"}}',
            '330 (elasticsearch) create alias "current_products" for index "products_v2"',
            '340 (elasticsearch) refresh index "products"'
        ]


# Singleton instance getter
def get_elasticsearch_module(**kwargs) -> ElasticsearchModule:
    """
    Get the singleton Elasticsearch module instance.

    Args:
        **kwargs: Configuration parameters

    Returns:
        ElasticsearchModule instance
    """
    return ElasticsearchModule(**kwargs)
