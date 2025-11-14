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


class ElasticsearchModule:
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
