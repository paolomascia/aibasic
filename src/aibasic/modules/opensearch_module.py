"""
OpenSearch Module for Search and Analytics

This module provides connection management for OpenSearch (AWS OpenSearch Service / Elasticsearch fork).
Configuration is loaded from aibasic.conf under the [opensearch] section.

Supports:
- No authentication (default)
- Basic authentication (username/password)
- AWS IAM authentication (for AWS OpenSearch Service)
- SSL/TLS connections
- SSL/TLS without certificate verification (for development)
- Full-text search, indexing, and analytics
- Bulk operations
- Index management
- Aggregations

Example configuration in aibasic.conf:
    [opensearch]
    HOST=localhost
    PORT=9200
    USE_SSL=false
    VERIFY_CERTS=true

    # Basic Authentication
    USERNAME=admin
    PASSWORD=admin

    # AWS IAM Authentication (for AWS OpenSearch Service)
    USE_AWS_AUTH=false
    AWS_REGION=us-east-1

    # SSL/TLS Settings (optional)
    CA_CERTS=/path/to/ca.pem
    CLIENT_CERT=/path/to/client-cert.pem
    CLIENT_KEY=/path/to/client-key.pem

    # Connection Settings
    TIMEOUT=30
    MAX_RETRIES=3
    POOL_MAXSIZE=10

Usage in generated code:
    from aibasic.modules import OpenSearchModule

    # Initialize module (happens once per program)
    os_client = OpenSearchModule.from_config(config_path="aibasic.conf")

    # Index operations
    os_client.index_document('products', {'name': 'Widget', 'price': 29.99}, doc_id='123')

    # Search operations
    results = os_client.search('products', query={'match': {'name': 'widget'}})

    # Bulk operations
    os_client.bulk_index('products', [{'name': 'Item1'}, {'name': 'Item2'}])

    # Get document
    doc = os_client.get_document('products', '123')
"""

import configparser
import json
import ssl
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List, Union

try:
    from opensearchpy import OpenSearch, helpers
    from opensearchpy.exceptions import NotFoundError, RequestError
except ImportError:
    OpenSearch = None
    helpers = None
    NotFoundError = Exception
    RequestError = Exception

from .module_base import AIbasicModuleBase


class OpenSearchModule(AIbasicModuleBase):
    """
    OpenSearch connection manager with full authentication and SSL/TLS support.

    Supports search, indexing, bulk operations, and analytics.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 9200,
        use_ssl: bool = False,
        verify_certs: bool = True,
        ca_certs: Optional[str] = None,
        client_cert: Optional[str] = None,
        client_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_aws_auth: bool = False,
        aws_region: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        pool_maxsize: int = 10
    ):
        """
        Initialize the OpenSearch module.

        Args:
            host: OpenSearch host
            port: OpenSearch port (default 9200, 9243 for AWS)
            use_ssl: Enable SSL/TLS connection
            verify_certs: Verify SSL certificates (set False for self-signed)
            ca_certs: Path to CA certificate file
            client_cert: Path to client certificate file
            client_key: Path to client key file
            username: Username for basic authentication
            password: Password for basic authentication
            use_aws_auth: Use AWS IAM authentication
            aws_region: AWS region (required if use_aws_auth=True)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            pool_maxsize: Maximum connection pool size
        """
        if OpenSearch is None:
            raise ImportError(
                "opensearch-py is required. Install it with: pip install opensearch-py"
            )

        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.verify_certs = verify_certs
        self.use_aws_auth = use_aws_auth

        # Build connection parameters
        hosts = [{'host': host, 'port': port}]

        connection_params = {
            'hosts': hosts,
            'timeout': timeout,
            'max_retries': max_retries,
            'pool_maxsize': pool_maxsize,
        }

        # SSL/TLS configuration
        if use_ssl:
            connection_params['use_ssl'] = True
            connection_params['verify_certs'] = verify_certs

            if not verify_certs:
                # Skip certificate verification
                connection_params['ssl_show_warn'] = False
                print("[OpenSearchModule] ⚠️  SSL certificate verification DISABLED")

            if ca_certs:
                connection_params['ca_certs'] = ca_certs
            if client_cert:
                connection_params['client_cert'] = client_cert
            if client_key:
                connection_params['client_key'] = client_key

        # Authentication
        if use_aws_auth:
            # AWS IAM authentication
            try:
                from opensearchpy import RequestsHttpConnection
                from requests_aws4auth import AWS4Auth
                import boto3

                credentials = boto3.Session().get_credentials()
                awsauth = AWS4Auth(
                    credentials.access_key,
                    credentials.secret_key,
                    aws_region or 'us-east-1',
                    'es',
                    session_token=credentials.token
                )
                connection_params['http_auth'] = awsauth
                connection_params['connection_class'] = RequestsHttpConnection
                print(f"[OpenSearchModule] Using AWS IAM authentication for region {aws_region}")
            except ImportError:
                raise ImportError(
                    "AWS authentication requires: pip install boto3 requests-aws4auth"
                )
        elif username and password:
            # Basic authentication
            connection_params['http_auth'] = (username, password)
            print(f"[OpenSearchModule] Using basic authentication as {username}")

        # Create OpenSearch client
        self.client = OpenSearch(**connection_params)

        # Test connection
        try:
            info = self.client.info()
            cluster_name = info.get('cluster_name', 'unknown')
            version = info.get('version', {}).get('number', 'unknown')
            print(f"[OpenSearchModule] Connected to OpenSearch cluster: {cluster_name} (v{version})")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to OpenSearch: {e}")

    @classmethod
    def from_config(cls, config_path: str = "aibasic.conf") -> 'OpenSearchModule':
        """
        Create an OpenSearchModule from configuration file.
        Uses singleton pattern to ensure only one instance exists.

        Args:
            config_path: Path to aibasic.conf file

        Returns:
            OpenSearchModule instance

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

                if 'opensearch' not in config:
                    raise KeyError("Missing [opensearch] section in aibasic.conf")

                os_config = config['opensearch']

                # Connection
                host = os_config.get('HOST', 'localhost')
                port = os_config.getint('PORT', 9200)

                # SSL/TLS
                use_ssl = os_config.getboolean('USE_SSL', False)
                verify_certs = os_config.getboolean('VERIFY_CERTS', True)
                ca_certs = os_config.get('CA_CERTS', None)
                client_cert = os_config.get('CLIENT_CERT', None)
                client_key = os_config.get('CLIENT_KEY', None)

                # Authentication
                username = os_config.get('USERNAME', None)
                password = os_config.get('PASSWORD', None)
                use_aws_auth = os_config.getboolean('USE_AWS_AUTH', False)
                aws_region = os_config.get('AWS_REGION', None)

                # Connection settings
                timeout = os_config.getint('TIMEOUT', 30)
                max_retries = os_config.getint('MAX_RETRIES', 3)
                pool_maxsize = os_config.getint('POOL_MAXSIZE', 10)

                cls._instance = cls(
                    host=host,
                    port=port,
                    use_ssl=use_ssl,
                    verify_certs=verify_certs,
                    ca_certs=ca_certs,
                    client_cert=client_cert,
                    client_key=client_key,
                    username=username,
                    password=password,
                    use_aws_auth=use_aws_auth,
                    aws_region=aws_region,
                    timeout=timeout,
                    max_retries=max_retries,
                    pool_maxsize=pool_maxsize
                )

            return cls._instance

    # ==================== Index Management ====================

    def create_index(self, index_name: str, body: Optional[Dict] = None) -> Dict:
        """
        Create a new index.

        Args:
            index_name: Name of the index
            body: Index settings and mappings

        Returns:
            Response dict
        """
        try:
            return self.client.indices.create(index=index_name, body=body or {})
        except RequestError as e:
            print(f"[OpenSearchModule] Index creation failed: {e}")
            raise

    def delete_index(self, index_name: str) -> Dict:
        """Delete an index."""
        return self.client.indices.delete(index=index_name)

    def index_exists(self, index_name: str) -> bool:
        """Check if index exists."""
        return self.client.indices.exists(index=index_name)

    def get_index_info(self, index_name: str) -> Dict:
        """Get index information."""
        return self.client.indices.get(index=index_name)

    def refresh_index(self, index_name: str) -> Dict:
        """Refresh an index (make recent changes searchable)."""
        return self.client.indices.refresh(index=index_name)

    # ==================== Document Operations ====================

    def index_document(
        self,
        index_name: str,
        document: Dict,
        doc_id: Optional[str] = None,
        refresh: bool = False
    ) -> Dict:
        """
        Index a single document.

        Args:
            index_name: Index name
            document: Document to index
            doc_id: Optional document ID (auto-generated if not provided)
            refresh: Refresh index after operation

        Returns:
            Response dict with _id, _index, result
        """
        params = {'refresh': refresh} if refresh else {}

        if doc_id:
            return self.client.index(
                index=index_name,
                body=document,
                id=doc_id,
                params=params
            )
        else:
            return self.client.index(
                index=index_name,
                body=document,
                params=params
            )

    def get_document(self, index_name: str, doc_id: str) -> Optional[Dict]:
        """
        Get a document by ID.

        Returns:
            Document dict or None if not found
        """
        try:
            response = self.client.get(index=index_name, id=doc_id)
            return response.get('_source')
        except NotFoundError:
            return None

    def update_document(
        self,
        index_name: str,
        doc_id: str,
        document: Dict,
        refresh: bool = False
    ) -> Dict:
        """
        Update a document.

        Args:
            index_name: Index name
            doc_id: Document ID
            document: Partial document or full document
            refresh: Refresh index after operation

        Returns:
            Response dict
        """
        params = {'refresh': refresh} if refresh else {}
        return self.client.update(
            index=index_name,
            id=doc_id,
            body={'doc': document},
            params=params
        )

    def delete_document(self, index_name: str, doc_id: str, refresh: bool = False) -> Dict:
        """Delete a document by ID."""
        params = {'refresh': refresh} if refresh else {}
        return self.client.delete(index=index_name, id=doc_id, params=params)

    # ==================== Search Operations ====================

    def search(
        self,
        index_name: str,
        query: Optional[Dict] = None,
        size: int = 10,
        from_: int = 0,
        sort: Optional[List] = None,
        source: Optional[Union[bool, List[str]]] = None
    ) -> Dict:
        """
        Search documents.

        Args:
            index_name: Index name or pattern (e.g., "logs-*")
            query: Query DSL (if None, returns all documents)
            size: Number of results to return
            from_: Starting offset for pagination
            sort: Sort order
            source: Fields to return (True=all, False=none, list=specific fields)

        Returns:
            Search response with hits
        """
        body = {}

        if query:
            body['query'] = query
        else:
            body['query'] = {'match_all': {}}

        if sort:
            body['sort'] = sort

        return self.client.search(
            index=index_name,
            body=body,
            size=size,
            from_=from_,
            _source=source
        )

    def search_simple(self, index_name: str, field: str, value: str, size: int = 10) -> List[Dict]:
        """
        Simple search for a value in a specific field.

        Args:
            index_name: Index name
            field: Field to search
            value: Value to search for
            size: Number of results

        Returns:
            List of matching documents
        """
        query = {
            'match': {field: value}
        }
        response = self.search(index_name, query=query, size=size)
        return [hit['_source'] for hit in response['hits']['hits']]

    def count(self, index_name: str, query: Optional[Dict] = None) -> int:
        """
        Count documents matching query.

        Args:
            index_name: Index name
            query: Query DSL (if None, counts all documents)

        Returns:
            Document count
        """
        body = {'query': query} if query else {'query': {'match_all': {}}}
        response = self.client.count(index=index_name, body=body)
        return response['count']

    # ==================== Bulk Operations ====================

    def bulk_index(
        self,
        index_name: str,
        documents: List[Dict],
        doc_ids: Optional[List[str]] = None,
        refresh: bool = False
    ) -> Dict:
        """
        Bulk index multiple documents.

        Args:
            index_name: Index name
            documents: List of documents to index
            doc_ids: Optional list of document IDs (same length as documents)
            refresh: Refresh index after operation

        Returns:
            Bulk response with success/error information
        """
        actions = []

        for i, doc in enumerate(documents):
            action = {
                '_index': index_name,
                '_source': doc
            }
            if doc_ids and i < len(doc_ids):
                action['_id'] = doc_ids[i]
            actions.append(action)

        return helpers.bulk(self.client, actions, refresh=refresh)

    def bulk_update(
        self,
        index_name: str,
        doc_ids: List[str],
        documents: List[Dict],
        refresh: bool = False
    ) -> Dict:
        """Bulk update multiple documents."""
        actions = []

        for doc_id, doc in zip(doc_ids, documents):
            actions.append({
                '_op_type': 'update',
                '_index': index_name,
                '_id': doc_id,
                'doc': doc
            })

        return helpers.bulk(self.client, actions, refresh=refresh)

    def bulk_delete(
        self,
        index_name: str,
        doc_ids: List[str],
        refresh: bool = False
    ) -> Dict:
        """Bulk delete multiple documents."""
        actions = []

        for doc_id in doc_ids:
            actions.append({
                '_op_type': 'delete',
                '_index': index_name,
                '_id': doc_id
            })

        return helpers.bulk(self.client, actions, refresh=refresh)

    # ==================== Aggregations ====================

    def aggregate(
        self,
        index_name: str,
        aggregations: Dict,
        query: Optional[Dict] = None,
        size: int = 0
    ) -> Dict:
        """
        Perform aggregations.

        Args:
            index_name: Index name
            aggregations: Aggregation DSL
            query: Optional query to filter documents
            size: Number of documents to return (0 = only aggregations)

        Returns:
            Aggregation results
        """
        body = {
            'aggs': aggregations,
            'size': size
        }

        if query:
            body['query'] = query

        return self.client.search(index=index_name, body=body)

    # ==================== Utility Operations ====================

    def ping(self) -> bool:
        """Ping OpenSearch cluster."""
        return self.client.ping()

    def cluster_health(self) -> Dict:
        """Get cluster health information."""
        return self.client.cluster.health()

    def cluster_stats(self) -> Dict:
        """Get cluster statistics."""
        return self.client.cluster.stats()

    def indices_stats(self, index_name: Optional[str] = None) -> Dict:
        """Get indices statistics."""
        if index_name:
            return self.client.indices.stats(index=index_name)
        return self.client.indices.stats()

    def close(self):
        """Close connection."""
        if self.client:
            self.client.close()
            print("[OpenSearchModule] Connection closed")

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get current connection information.

        Returns:
            dict: Connection details
        """
        return {
            "host": self.host,
            "port": self.port,
            "use_ssl": self.use_ssl,
            "verify_certs": self.verify_certs,
            "use_aws_auth": self.use_aws_auth
        }

    def __del__(self):
        """Destructor to ensure connection is closed."""
        try:
            self.close()
        except:
            pass

    @classmethod
    def get_metadata(cls):
        """Get module metadata for compiler prompt generation."""
        from aibasic.modules.module_base import ModuleMetadata
        return ModuleMetadata(
            name="OpenSearch",
            task_type="opensearch",
            description="OpenSearch search and analytics engine with full-text search, indexing, aggregations, and AWS support",
            version="1.0.0",
            keywords=[
                "opensearch", "elasticsearch", "search", "analytics", "full-text",
                "indexing", "aggregations", "aws", "iam", "bulk-operations"
            ],
            dependencies=["opensearch-py>=2.0.0"]
        )

    @classmethod
    def get_usage_notes(cls):
        """Get detailed usage notes for this module."""
        return [
            "Module uses singleton pattern - one client instance per application",
            "Supports basic authentication (username/password)",
            "Supports AWS IAM authentication for AWS OpenSearch Service",
            "SSL/TLS connections supported with optional certificate verification",
            "Set VERIFY_CERTS=false for self-signed certificates (development only)",
            "Default port is 9200 (9243 for AWS OpenSearch)",
            "Documents auto-generate ID if not specified",
            "refresh=True makes documents immediately searchable (slower)",
            "Index patterns supported (e.g., 'logs-*' searches multiple indices)",
            "Query DSL used for complex searches (match, term, bool, range, etc.)",
            "Aggregations provide analytics (terms, stats, histogram, date_histogram)",
            "Bulk operations significantly faster for multiple documents",
            "size=0 in aggregations returns only aggregation results",
            "from_ and size parameters used for pagination",
            "_source parameter controls which fields are returned",
            "refresh_index() makes recent changes searchable",
            "count() returns document count without retrieving documents",
            "Timeout defaults to 30 seconds, configurable via TIMEOUT",
            "Connection pool size defaults to 10, configurable via POOL_MAXSIZE",
            "AWS authentication requires boto3 and requests-aws4auth packages"
        ]

    @classmethod
    def get_methods_info(cls):
        """Get information about all methods in this module."""
        from aibasic.modules.module_base import MethodInfo
        return [
            MethodInfo(
                name="index_document",
                description="Index a single document with optional ID",
                parameters={
                    "index_name": "str (required) - Index name",
                    "document": "dict (required) - Document to index",
                    "doc_id": "str (optional) - Document ID (auto-generated if not provided)",
                    "refresh": "bool (optional) - Refresh index after operation (default False)"
                },
                returns="dict - Response with _id, _index, result",
                examples=['index {"name": "Widget", "price": 29.99} into "products"', 'index {"name": "Item"} into "products" with id "123"']
            ),
            MethodInfo(
                name="get_document",
                description="Get a document by ID from an index",
                parameters={
                    "index_name": "str (required) - Index name",
                    "doc_id": "str (required) - Document ID"
                },
                returns="dict/None - Document source or None if not found",
                examples=['get document "123" from "products"']
            ),
            MethodInfo(
                name="search",
                description="Search documents using Query DSL",
                parameters={
                    "index_name": "str (required) - Index name or pattern",
                    "query": "dict (optional) - Query DSL (None = match_all)",
                    "size": "int (optional) - Number of results (default 10)",
                    "from_": "int (optional) - Starting offset for pagination (default 0)",
                    "sort": "list (optional) - Sort order",
                    "source": "bool/list (optional) - Fields to return"
                },
                returns="dict - Search response with hits",
                examples=['search "products" for {"match": {"name": "widget"}}', 'search "logs-*" size 100']
            ),
            MethodInfo(
                name="search_simple",
                description="Simple search for a value in a specific field",
                parameters={
                    "index_name": "str (required) - Index name",
                    "field": "str (required) - Field to search",
                    "value": "str (required) - Value to search for",
                    "size": "int (optional) - Number of results (default 10)"
                },
                returns="list - List of matching documents",
                examples=['search "products" field "name" value "widget"']
            ),
            MethodInfo(
                name="bulk_index",
                description="Bulk index multiple documents at once",
                parameters={
                    "index_name": "str (required) - Index name",
                    "documents": "list (required) - List of documents to index",
                    "doc_ids": "list (optional) - List of document IDs",
                    "refresh": "bool (optional) - Refresh index after operation"
                },
                returns="dict - Bulk response with success/error information",
                examples=['bulk index [{"name": "Item1"}, {"name": "Item2"}] into "products"']
            ),
            MethodInfo(
                name="update_document",
                description="Update an existing document by ID",
                parameters={
                    "index_name": "str (required) - Index name",
                    "doc_id": "str (required) - Document ID",
                    "document": "dict (required) - Partial or full document update",
                    "refresh": "bool (optional) - Refresh index after operation"
                },
                returns="dict - Response",
                examples=['update document "123" in "products" with {"price": 39.99}']
            ),
            MethodInfo(
                name="delete_document",
                description="Delete a document by ID",
                parameters={
                    "index_name": "str (required) - Index name",
                    "doc_id": "str (required) - Document ID",
                    "refresh": "bool (optional) - Refresh index after operation"
                },
                returns="dict - Response",
                examples=['delete document "123" from "products"']
            ),
            MethodInfo(
                name="create_index",
                description="Create a new index with optional settings and mappings",
                parameters={
                    "index_name": "str (required) - Index name",
                    "body": "dict (optional) - Index settings and mappings"
                },
                returns="dict - Response",
                examples=['create index "products"', 'create index "logs" with settings {...}']
            ),
            MethodInfo(
                name="delete_index",
                description="Delete an index",
                parameters={"index_name": "str (required) - Index name"},
                returns="dict - Response",
                examples=['delete index "old_products"']
            ),
            MethodInfo(
                name="count",
                description="Count documents matching a query",
                parameters={
                    "index_name": "str (required) - Index name",
                    "query": "dict (optional) - Query DSL (None = count all)"
                },
                returns="int - Document count",
                examples=['count documents in "products"', 'count "products" where {"match": {"category": "electronics"}}']
            ),
            MethodInfo(
                name="aggregate",
                description="Perform aggregations for analytics",
                parameters={
                    "index_name": "str (required) - Index name",
                    "aggregations": "dict (required) - Aggregation DSL",
                    "query": "dict (optional) - Filter query",
                    "size": "int (optional) - Number of documents to return (default 0)"
                },
                returns="dict - Aggregation results",
                examples=['aggregate "sales" by {"by_category": {"terms": {"field": "category"}}}']
            ),
            MethodInfo(
                name="cluster_health",
                description="Get OpenSearch cluster health status",
                parameters={},
                returns="dict - Cluster health information",
                examples=['get cluster health']
            )
        ]

    @classmethod
    def get_examples(cls):
        """Get example AIbasic code snippets."""
        return [
            '10 (opensearch) create index "products"',
            '20 (opensearch) index {"name": "Widget", "price": 29.99, "category": "tools"} into "products" with id "123"',
            '30 (opensearch) index {"name": "Gadget", "price": 49.99} into "products"',
            '40 (opensearch) doc = get document "123" from "products"',
            '50 (opensearch) results = search "products" for {"match": {"name": "widget"}}',
            '60 (opensearch) results = search "products" field "category" value "tools"',
            '70 (opensearch) update document "123" in "products" with {"price": 39.99}',
            '80 (opensearch) bulk index [{"name": "Item1"}, {"name": "Item2"}, {"name": "Item3"}] into "products"',
            '90 (opensearch) count = count documents in "products"',
            '100 (opensearch) agg = aggregate "products" by {"avg_price": {"avg": {"field": "price"}}}',
            '110 (opensearch) delete document "123" from "products"'
        ]
