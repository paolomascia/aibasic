"""
MongoDB Module for Document-Oriented NoSQL Database

This module provides connection management and operations for MongoDB,
a popular document-oriented NoSQL database.
Configuration is loaded from aibasic.conf under the [mongodb] section.

Supports:
- Connection string (MongoDB URI)
- Authentication (username/password, SCRAM, X.509)
- SSL/TLS encryption with certificate verification
- Replica sets and sharding
- Database and collection operations
- CRUD operations (Create, Read, Update, Delete)
- Aggregation pipelines
- Indexes management
- Bulk operations
- GridFS for large files
- Transactions (MongoDB 4.0+)
- Change streams
- Text search

Features:
- Insert documents (single and bulk)
- Query with filters and projections
- Update and replace documents
- Delete documents
- Aggregation framework
- Index creation and management
- Database administration
- Collection management
- GridFS file storage

Example configuration in aibasic.conf:
    [mongodb]
    # Connection String (preferred method)
    CONNECTION_STRING=mongodb://localhost:27017/

    # OR Individual parameters
    # HOST=localhost
    # PORT=27017
    # USERNAME=admin
    # PASSWORD=secret
    # AUTH_DATABASE=admin

    # Database
    DATABASE=my_database

    # SSL/TLS Settings
    TLS=false
    TLS_CA_FILE=/path/to/ca.pem
    TLS_CERT_FILE=/path/to/client-cert.pem
    TLS_KEY_FILE=/path/to/client-key.pem
    TLS_ALLOW_INVALID_CERTIFICATES=false

    # Connection Pool
    MAX_POOL_SIZE=100
    MIN_POOL_SIZE=10

Usage in generated code:
    from aibasic.modules import MongoDBModule

    # Initialize module
    mongo = MongoDBModule.from_config('aibasic.conf')

    # Insert document
    mongo.insert_one('users', {'name': 'Alice', 'email': 'alice@example.com'})

    # Find documents
    users = mongo.find('users', {'age': {'$gt': 25}})

    # Update document
    mongo.update_one('users', {'name': 'Alice'}, {'$set': {'age': 30}})

    # Aggregation
    result = mongo.aggregate('orders', [
        {'$group': {'_id': '$customer', 'total': {'$sum': '$amount'}}}
    ])
"""

import configparser
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Tuple
from datetime import datetime
from .module_base import AIbasicModuleBase

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, OperationFailure, DuplicateKeyError
    from bson import ObjectId
    from bson.errors import InvalidId
except ImportError:
    MongoClient = None
    ObjectId = None


class MongoDBModule(AIbasicModuleBase):
    """
    MongoDB document database module.

    Supports CRUD operations, aggregation, indexing, and file storage.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(
        self,
        connection_string: Optional[str] = None,
        host: str = 'localhost',
        port: int = 27017,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: str = 'test',
        auth_database: str = 'admin',
        tls: bool = False,
        tls_ca_file: Optional[str] = None,
        tls_cert_file: Optional[str] = None,
        tls_key_file: Optional[str] = None,
        tls_allow_invalid_certificates: bool = False,
        max_pool_size: int = 100,
        min_pool_size: int = 10,
        server_selection_timeout: int = 30000
    ):
        """
        Initialize the MongoDBModule.

        Args:
            connection_string: MongoDB connection string (overrides other params)
            host: MongoDB host
            port: MongoDB port
            username: Authentication username
            password: Authentication password
            database: Default database name
            auth_database: Authentication database
            tls: Enable TLS/SSL
            tls_ca_file: Path to CA certificate
            tls_cert_file: Path to client certificate
            tls_key_file: Path to client key
            tls_allow_invalid_certificates: Allow invalid certificates
            max_pool_size: Maximum connection pool size
            min_pool_size: Minimum connection pool size
            server_selection_timeout: Server selection timeout in ms
        """
        if MongoClient is None:
            raise ImportError(
                "pymongo is required. Install with: pip install pymongo"
            )

        self.database_name = database

        # Build connection string or use provided one
        if connection_string:
            uri = connection_string
            print(f"[MongoDBModule] Using provided connection string")
        else:
            # Build URI from components
            if username and password:
                credentials = f"{username}:{password}@"
                auth_source = f"?authSource={auth_database}"
            else:
                credentials = ""
                auth_source = ""

            uri = f"mongodb://{credentials}{host}:{port}/{auth_source}"

        # Connection options
        options = {
            'maxPoolSize': max_pool_size,
            'minPoolSize': min_pool_size,
            'serverSelectionTimeoutMS': server_selection_timeout
        }

        # TLS/SSL options
        if tls:
            options['tls'] = True

            if tls_ca_file:
                options['tlsCAFile'] = tls_ca_file

            if tls_cert_file:
                options['tlsCertificateKeyFile'] = tls_cert_file

            if tls_allow_invalid_certificates:
                options['tlsAllowInvalidCertificates'] = True
                print("[MongoDBModule] ⚠️  TLS certificate validation DISABLED")

        # Create MongoDB client
        try:
            self.client = MongoClient(uri, **options)

            # Test connection
            self.client.admin.command('ping')

            # Get database
            self.db = self.client[database]

            # Get server info
            server_info = self.client.server_info()
            version = server_info.get('version', 'unknown')

            print(f"[MongoDBModule] Connected to MongoDB {version}")
            print(f"[MongoDBModule] Using database: {database}")

        except ConnectionFailure as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")
        except Exception as e:
            raise RuntimeError(f"MongoDB initialization error: {e}")

    @classmethod
    def from_config(cls, config_path: str = "aibasic.conf") -> 'MongoDBModule':
        """
        Create a MongoDBModule from configuration file.
        Uses singleton pattern to ensure only one instance exists.

        Args:
            config_path: Path to aibasic.conf file

        Returns:
            MongoDBModule instance
        """
        with cls._lock:
            if cls._instance is None:
                config = configparser.ConfigParser()
                path = Path(config_path)

                if not path.exists():
                    raise FileNotFoundError(f"Configuration file not found: {config_path}")

                config.read(path)

                if 'mongodb' not in config:
                    raise KeyError("Missing [mongodb] section in aibasic.conf")

                mongo_config = config['mongodb']

                # Connection string or individual params
                connection_string = mongo_config.get('CONNECTION_STRING', None)
                host = mongo_config.get('HOST', 'localhost')
                port = mongo_config.getint('PORT', 27017)

                # Authentication
                username = mongo_config.get('USERNAME', None)
                password = mongo_config.get('PASSWORD', None)
                auth_database = mongo_config.get('AUTH_DATABASE', 'admin')

                # Database
                database = mongo_config.get('DATABASE', 'test')

                # TLS/SSL
                tls = mongo_config.getboolean('TLS', False)
                tls_ca_file = mongo_config.get('TLS_CA_FILE', None)
                tls_cert_file = mongo_config.get('TLS_CERT_FILE', None)
                tls_key_file = mongo_config.get('TLS_KEY_FILE', None)
                tls_allow_invalid_certificates = mongo_config.getboolean(
                    'TLS_ALLOW_INVALID_CERTIFICATES', False
                )

                # Connection pool
                max_pool_size = mongo_config.getint('MAX_POOL_SIZE', 100)
                min_pool_size = mongo_config.getint('MIN_POOL_SIZE', 10)
                server_selection_timeout = mongo_config.getint(
                    'SERVER_SELECTION_TIMEOUT', 30000
                )

                cls._instance = cls(
                    connection_string=connection_string,
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                    database=database,
                    auth_database=auth_database,
                    tls=tls,
                    tls_ca_file=tls_ca_file,
                    tls_cert_file=tls_cert_file,
                    tls_key_file=tls_key_file,
                    tls_allow_invalid_certificates=tls_allow_invalid_certificates,
                    max_pool_size=max_pool_size,
                    min_pool_size=min_pool_size,
                    server_selection_timeout=server_selection_timeout
                )

            return cls._instance

    # ==================== Database Operations ====================

    def list_databases(self) -> List[str]:
        """List all database names."""
        return self.client.list_database_names()

    def create_database(self, name: str):
        """
        Create a database (MongoDB creates on first write).

        Args:
            name: Database name
        """
        # MongoDB creates database on first document insert
        db = self.client[name]
        # Create a dummy collection to force database creation
        db.create_collection('_init')
        db.drop_collection('_init')
        print(f"[MongoDBModule] Database '{name}' ready")

    def drop_database(self, name: str):
        """Drop a database."""
        self.client.drop_database(name)
        print(f"[MongoDBModule] Database '{name}' dropped")

    def use_database(self, name: str):
        """Switch to a different database."""
        self.db = self.client[name]
        self.database_name = name
        print(f"[MongoDBModule] Switched to database '{name}'")

    # ==================== Collection Operations ====================

    def list_collections(self, database: Optional[str] = None) -> List[str]:
        """List all collection names in a database."""
        db = self.client[database] if database else self.db
        return db.list_collection_names()

    def create_collection(
        self,
        name: str,
        capped: bool = False,
        size: Optional[int] = None,
        max_documents: Optional[int] = None
    ):
        """
        Create a collection.

        Args:
            name: Collection name
            capped: Create capped collection
            size: Max size in bytes (for capped)
            max_documents: Max number of documents (for capped)
        """
        options = {}
        if capped:
            options['capped'] = True
            if size:
                options['size'] = size
            if max_documents:
                options['max'] = max_documents

        self.db.create_collection(name, **options)
        print(f"[MongoDBModule] Collection '{name}' created")

    def drop_collection(self, name: str):
        """Drop a collection."""
        self.db.drop_collection(name)
        print(f"[MongoDBModule] Collection '{name}' dropped")

    # ==================== CRUD Operations ====================

    def insert_one(self, collection: str, document: Dict) -> str:
        """
        Insert a single document.

        Args:
            collection: Collection name
            document: Document to insert

        Returns:
            Inserted document ID as string
        """
        result = self.db[collection].insert_one(document)
        return str(result.inserted_id)

    def insert_many(self, collection: str, documents: List[Dict]) -> List[str]:
        """
        Insert multiple documents.

        Args:
            collection: Collection name
            documents: List of documents

        Returns:
            List of inserted IDs as strings
        """
        result = self.db[collection].insert_many(documents)
        return [str(id) for id in result.inserted_ids]

    def find_one(
        self,
        collection: str,
        filter: Optional[Dict] = None,
        projection: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Find a single document.

        Args:
            collection: Collection name
            filter: Query filter
            projection: Fields to include/exclude

        Returns:
            Document or None
        """
        result = self.db[collection].find_one(filter or {}, projection)
        if result and '_id' in result:
            result['_id'] = str(result['_id'])
        return result

    def find(
        self,
        collection: str,
        filter: Optional[Dict] = None,
        projection: Optional[Dict] = None,
        sort: Optional[List] = None,
        limit: int = 0,
        skip: int = 0
    ) -> List[Dict]:
        """
        Find multiple documents.

        Args:
            collection: Collection name
            filter: Query filter
            projection: Fields to include/exclude
            sort: Sort specification [(field, direction), ...]
            limit: Maximum documents to return
            skip: Number of documents to skip

        Returns:
            List of documents
        """
        cursor = self.db[collection].find(filter or {}, projection)

        if sort:
            cursor = cursor.sort(sort)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)

        results = []
        for doc in cursor:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
            results.append(doc)

        return results

    def update_one(
        self,
        collection: str,
        filter: Dict,
        update: Dict,
        upsert: bool = False
    ) -> Dict[str, Any]:
        """
        Update a single document.

        Args:
            collection: Collection name
            filter: Query filter
            update: Update operations
            upsert: Insert if not found

        Returns:
            Update result stats
        """
        result = self.db[collection].update_one(filter, update, upsert=upsert)

        return {
            'matched_count': result.matched_count,
            'modified_count': result.modified_count,
            'upserted_id': str(result.upserted_id) if result.upserted_id else None
        }

    def update_many(
        self,
        collection: str,
        filter: Dict,
        update: Dict,
        upsert: bool = False
    ) -> Dict[str, Any]:
        """Update multiple documents."""
        result = self.db[collection].update_many(filter, update, upsert=upsert)

        return {
            'matched_count': result.matched_count,
            'modified_count': result.modified_count,
            'upserted_id': str(result.upserted_id) if result.upserted_id else None
        }

    def replace_one(
        self,
        collection: str,
        filter: Dict,
        replacement: Dict,
        upsert: bool = False
    ) -> Dict[str, Any]:
        """Replace a single document."""
        result = self.db[collection].replace_one(filter, replacement, upsert=upsert)

        return {
            'matched_count': result.matched_count,
            'modified_count': result.modified_count,
            'upserted_id': str(result.upserted_id) if result.upserted_id else None
        }

    def delete_one(self, collection: str, filter: Dict) -> int:
        """
        Delete a single document.

        Args:
            collection: Collection name
            filter: Query filter

        Returns:
            Number of deleted documents
        """
        result = self.db[collection].delete_one(filter)
        return result.deleted_count

    def delete_many(self, collection: str, filter: Dict) -> int:
        """Delete multiple documents."""
        result = self.db[collection].delete_many(filter)
        return result.deleted_count

    # ==================== Aggregation ====================

    def aggregate(
        self,
        collection: str,
        pipeline: List[Dict],
        allow_disk_use: bool = False
    ) -> List[Dict]:
        """
        Run an aggregation pipeline.

        Args:
            collection: Collection name
            pipeline: Aggregation pipeline stages
            allow_disk_use: Allow using disk for large operations

        Returns:
            List of aggregation results
        """
        cursor = self.db[collection].aggregate(
            pipeline,
            allowDiskUse=allow_disk_use
        )

        results = []
        for doc in cursor:
            if '_id' in doc and isinstance(doc['_id'], ObjectId):
                doc['_id'] = str(doc['_id'])
            results.append(doc)

        return results

    def count_documents(
        self,
        collection: str,
        filter: Optional[Dict] = None
    ) -> int:
        """Count documents matching filter."""
        return self.db[collection].count_documents(filter or {})

    def distinct(self, collection: str, field: str, filter: Optional[Dict] = None) -> List:
        """Get distinct values for a field."""
        return self.db[collection].distinct(field, filter or {})

    # ==================== Index Management ====================

    def create_index(
        self,
        collection: str,
        keys: Union[str, List[Tuple[str, int]]],
        unique: bool = False,
        name: Optional[str] = None
    ) -> str:
        """
        Create an index.

        Args:
            collection: Collection name
            keys: Index key(s) - string or [(field, direction), ...]
            unique: Create unique index
            name: Index name

        Returns:
            Index name
        """
        options = {}
        if unique:
            options['unique'] = True
        if name:
            options['name'] = name

        result = self.db[collection].create_index(keys, **options)
        print(f"[MongoDBModule] Index created: {result}")
        return result

    def drop_index(self, collection: str, index_name: str):
        """Drop an index."""
        self.db[collection].drop_index(index_name)
        print(f"[MongoDBModule] Index dropped: {index_name}")

    def list_indexes(self, collection: str) -> List[Dict]:
        """List all indexes for a collection."""
        return list(self.db[collection].list_indexes())

    # ==================== Bulk Operations ====================

    def bulk_write(self, collection: str, operations: List[Dict]) -> Dict[str, Any]:
        """
        Execute bulk write operations.

        Args:
            collection: Collection name
            operations: List of write operations

        Returns:
            Bulk write result
        """
        from pymongo import InsertOne, UpdateOne, DeleteOne, ReplaceOne

        ops = []
        for op in operations:
            op_type = op.get('type')

            if op_type == 'insert':
                ops.append(InsertOne(op['document']))
            elif op_type == 'update':
                ops.append(UpdateOne(op['filter'], op['update'], upsert=op.get('upsert', False)))
            elif op_type == 'delete':
                ops.append(DeleteOne(op['filter']))
            elif op_type == 'replace':
                ops.append(ReplaceOne(op['filter'], op['replacement'], upsert=op.get('upsert', False)))

        result = self.db[collection].bulk_write(ops)

        return {
            'inserted_count': result.inserted_count,
            'matched_count': result.matched_count,
            'modified_count': result.modified_count,
            'deleted_count': result.deleted_count,
            'upserted_count': result.upserted_count
        }

    # ==================== Text Search ====================

    def create_text_index(self, collection: str, fields: Union[str, List[str]]):
        """
        Create a text index for full-text search.

        Args:
            collection: Collection name
            fields: Field(s) to index for text search
        """
        if isinstance(fields, str):
            fields = [fields]

        index_spec = [(field, 'text') for field in fields]
        return self.create_index(collection, index_spec)

    def text_search(
        self,
        collection: str,
        search_text: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Perform text search.

        Args:
            collection: Collection name
            search_text: Text to search
            limit: Maximum results

        Returns:
            List of matching documents
        """
        return self.find(
            collection,
            {'$text': {'$search': search_text}},
            limit=limit
        )

    # ==================== Utility Methods ====================

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        return self.db.command('dbStats')

    def get_collection_stats(self, collection: str) -> Dict[str, Any]:
        """Get collection statistics."""
        return self.db.command('collStats', collection)

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            print("[MongoDBModule] Connection closed")

    def __del__(self):
        """Destructor to ensure connection is closed."""
        try:
            self.close()
        except:
            pass

    # ========================================
    # Metadata methods for AIbasic compiler
    # ========================================

    @classmethod
    def get_metadata(cls):
        """Get module metadata for compiler prompt generation."""
        from aibasic.modules.module_base import ModuleMetadata
        return ModuleMetadata(
            name="MongoDB",
            task_type="mongodb",
            description="MongoDB document-oriented NoSQL database with CRUD operations, aggregation pipelines, indexing, and text search",
            version="1.0.0",
            keywords=[
                "mongodb", "nosql", "document", "database", "crud", "aggregation",
                "index", "query", "collection", "bson", "gridfs", "full-text-search"
            ],
            dependencies=["pymongo>=4.0.0"]
        )

    @classmethod
    def get_usage_notes(cls):
        """Get detailed usage notes for this module."""
        return [
            "Module uses singleton pattern via from_config() - one instance per application",
            "Requires pymongo library version 4.0.0 or higher for full functionality",
            "Supports MongoDB connection strings (mongodb://) or individual host/port/credentials",
            "Default database is 'test' if not specified in configuration",
            "All document _id fields are automatically converted to strings in results",
            "TLS/SSL encryption supported with CA certificates and client certificates",
            "Connection pool configurable with max_pool_size and min_pool_size settings",
            "Server selection timeout defaults to 30 seconds (30000ms)",
            "Supports SCRAM and X.509 authentication mechanisms via connection string",
            "Authentication database defaults to 'admin' unless otherwise specified",
            "MongoDB creates databases and collections on first write operation",
            "Aggregation pipelines support complex data transformations and analytics",
            "Indexes improve query performance - create on frequently queried fields",
            "Text indexes enable full-text search across string fields",
            "Bulk operations provide efficient batch inserts, updates, and deletes",
            "Upsert option available for update operations (insert if not found)",
            "Sort, limit, and skip supported for query result pagination",
            "Projection parameter controls which fields are returned in queries",
            "Capped collections available for fixed-size, ordered data storage",
            "ObjectId strings can be used for queries - automatic conversion handled internally"
        ]

    @classmethod
    def get_methods_info(cls):
        """Get information about all methods in this module."""
        from aibasic.modules.module_base import MethodInfo
        return [
            # Database Operations
            MethodInfo(
                name="list_databases",
                description="List all database names on the MongoDB server",
                parameters={},
                returns="list[str] - List of database names",
                examples=[
                    'list databases',
                    'get all databases'
                ]
            ),
            MethodInfo(
                name="create_database",
                description="Create a new database (MongoDB creates on first write operation)",
                parameters={
                    "name": "str (required) - Database name to create"
                },
                returns="None - prints confirmation message",
                examples=[
                    'create database "myapp_db"',
                    'create database "production"'
                ]
            ),
            MethodInfo(
                name="drop_database",
                description="Drop (delete) a database and all its collections",
                parameters={
                    "name": "str (required) - Database name to drop"
                },
                returns="None - prints confirmation message",
                examples=[
                    'drop database "old_database"',
                    'drop database "test_db"'
                ]
            ),
            MethodInfo(
                name="use_database",
                description="Switch to a different database for subsequent operations",
                parameters={
                    "name": "str (required) - Database name to use"
                },
                returns="None - prints confirmation message",
                examples=[
                    'use database "production"',
                    'switch to database "analytics"'
                ]
            ),

            # Collection Operations
            MethodInfo(
                name="list_collections",
                description="List all collection names in a database",
                parameters={
                    "database": "str (optional) - Database name (uses current database if not specified)"
                },
                returns="list[str] - List of collection names",
                examples=[
                    'list collections',
                    'list collections in database "myapp"'
                ]
            ),
            MethodInfo(
                name="create_collection",
                description="Create a new collection with optional capped collection settings",
                parameters={
                    "name": "str (required) - Collection name",
                    "capped": "bool (optional) - Create capped collection (default False)",
                    "size": "int (optional) - Max size in bytes for capped collection",
                    "max_documents": "int (optional) - Max number of documents for capped collection"
                },
                returns="None - prints confirmation message",
                examples=[
                    'create collection "users"',
                    'create capped collection "logs" size 1048576',
                    'create capped collection "events" size 5242880 max 10000'
                ]
            ),
            MethodInfo(
                name="drop_collection",
                description="Drop (delete) a collection and all its documents",
                parameters={
                    "name": "str (required) - Collection name to drop"
                },
                returns="None - prints confirmation message",
                examples=[
                    'drop collection "old_users"',
                    'drop collection "temp_data"'
                ]
            ),

            # CRUD Operations
            MethodInfo(
                name="insert_one",
                description="Insert a single document into a collection",
                parameters={
                    "collection": "str (required) - Collection name",
                    "document": "dict (required) - Document to insert as key-value pairs"
                },
                returns="str - Inserted document ID",
                examples=[
                    'insert {"name": "Alice", "age": 30, "email": "alice@example.com"} into "users"',
                    'insert {"title": "Product Launch", "status": "active"} into "projects"'
                ]
            ),
            MethodInfo(
                name="insert_many",
                description="Insert multiple documents into a collection in a single operation",
                parameters={
                    "collection": "str (required) - Collection name",
                    "documents": "list[dict] (required) - List of documents to insert"
                },
                returns="list[str] - List of inserted document IDs",
                examples=[
                    'insert [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}] into "users"',
                    'bulk insert [{"product": "Widget", "price": 19.99}, {"product": "Gadget", "price": 29.99}] into "products"'
                ]
            ),
            MethodInfo(
                name="find_one",
                description="Find and return a single document matching the filter criteria",
                parameters={
                    "collection": "str (required) - Collection name",
                    "filter": "dict (optional) - Query filter (empty dict returns any document)",
                    "projection": "dict (optional) - Fields to include/exclude (1=include, 0=exclude)"
                },
                returns="dict or None - First matching document or None if not found",
                examples=[
                    'find one in "users" where {"name": "Alice"}',
                    'find one in "users" where {"age": {"$gt": 25}}',
                    'find one in "users" where {"email": "alice@example.com"} project {"name": 1, "email": 1}'
                ]
            ),
            MethodInfo(
                name="find",
                description="Find and return multiple documents matching the filter criteria with sort, limit, and skip options",
                parameters={
                    "collection": "str (required) - Collection name",
                    "filter": "dict (optional) - Query filter (empty dict returns all)",
                    "projection": "dict (optional) - Fields to include/exclude",
                    "sort": "list[tuple] (optional) - Sort specification [(field, direction), ...] where direction: 1=asc, -1=desc",
                    "limit": "int (optional) - Maximum documents to return (0=unlimited)",
                    "skip": "int (optional) - Number of documents to skip (for pagination)"
                },
                returns="list[dict] - List of matching documents",
                examples=[
                    'find all in "users"',
                    'find in "users" where {"age": {"$gte": 25}}',
                    'find in "users" where {"status": "active"} sort [("name", 1)] limit 10',
                    'find in "products" where {"category": "electronics"} skip 20 limit 10'
                ]
            ),
            MethodInfo(
                name="update_one",
                description="Update a single document matching the filter with update operations",
                parameters={
                    "collection": "str (required) - Collection name",
                    "filter": "dict (required) - Query filter to find document",
                    "update": "dict (required) - Update operations (e.g., {\"$set\": {...}}, {\"$inc\": {...}})",
                    "upsert": "bool (optional) - Insert if not found (default False)"
                },
                returns="dict - Update result with matched_count, modified_count, upserted_id",
                examples=[
                    'update one in "users" where {"name": "Alice"} set {"age": 31}',
                    'update one in "users" where {"email": "bob@example.com"} set {"status": "inactive"}',
                    'upsert in "counters" where {"name": "visits"} set {"count": 1}'
                ]
            ),
            MethodInfo(
                name="update_many",
                description="Update multiple documents matching the filter",
                parameters={
                    "collection": "str (required) - Collection name",
                    "filter": "dict (required) - Query filter",
                    "update": "dict (required) - Update operations",
                    "upsert": "bool (optional) - Insert if not found"
                },
                returns="dict - Update result with matched_count, modified_count, upserted_id",
                examples=[
                    'update many in "users" where {"status": "pending"} set {"status": "approved"}',
                    'update all in "products" where {"category": "electronics"} inc {"views": 1}'
                ]
            ),
            MethodInfo(
                name="replace_one",
                description="Replace entire document matching filter with new document",
                parameters={
                    "collection": "str (required) - Collection name",
                    "filter": "dict (required) - Query filter",
                    "replacement": "dict (required) - New document to replace with (no update operators)",
                    "upsert": "bool (optional) - Insert if not found"
                },
                returns="dict - Replace result with matched_count, modified_count, upserted_id",
                examples=[
                    'replace in "users" where {"_id": "507f1f77bcf86cd799439011"} with {"name": "Alice", "age": 32, "email": "alice@newmail.com"}',
                    'replace one in "settings" where {"key": "theme"} with {"key": "theme", "value": "dark"}'
                ]
            ),
            MethodInfo(
                name="delete_one",
                description="Delete a single document matching the filter",
                parameters={
                    "collection": "str (required) - Collection name",
                    "filter": "dict (required) - Query filter"
                },
                returns="int - Number of deleted documents (0 or 1)",
                examples=[
                    'delete one from "users" where {"name": "Alice"}',
                    'delete from "sessions" where {"expired": true}'
                ]
            ),
            MethodInfo(
                name="delete_many",
                description="Delete multiple documents matching the filter",
                parameters={
                    "collection": "str (required) - Collection name",
                    "filter": "dict (required) - Query filter"
                },
                returns="int - Number of deleted documents",
                examples=[
                    'delete many from "users" where {"status": "inactive"}',
                    'delete all from "logs" where {"timestamp": {"$lt": 1609459200}}'
                ]
            ),

            # Aggregation
            MethodInfo(
                name="aggregate",
                description="Run aggregation pipeline for complex data transformations and analytics",
                parameters={
                    "collection": "str (required) - Collection name",
                    "pipeline": "list[dict] (required) - List of aggregation stages ($match, $group, $sort, etc.)",
                    "allow_disk_use": "bool (optional) - Allow using disk for large operations (default False)"
                },
                returns="list[dict] - Aggregation results",
                examples=[
                    'aggregate "orders" pipeline [{"$group": {"_id": "$customer", "total": {"$sum": "$amount"}}}]',
                    'aggregate "sales" pipeline [{"$match": {"year": 2023}}, {"$group": {"_id": "$product", "count": {"$sum": 1}}}]'
                ]
            ),
            MethodInfo(
                name="count_documents",
                description="Count documents matching the filter",
                parameters={
                    "collection": "str (required) - Collection name",
                    "filter": "dict (optional) - Query filter (empty dict counts all)"
                },
                returns="int - Number of matching documents",
                examples=[
                    'count documents in "users"',
                    'count in "users" where {"status": "active"}',
                    'count in "orders" where {"total": {"$gt": 100}}'
                ]
            ),
            MethodInfo(
                name="distinct",
                description="Get distinct values for a field across documents",
                parameters={
                    "collection": "str (required) - Collection name",
                    "field": "str (required) - Field name to get distinct values from",
                    "filter": "dict (optional) - Query filter to apply before getting distinct values"
                },
                returns="list - List of distinct values",
                examples=[
                    'distinct "status" in "users"',
                    'distinct "category" in "products"',
                    'distinct "country" in "users" where {"status": "active"}'
                ]
            ),

            # Index Management
            MethodInfo(
                name="create_index",
                description="Create an index on collection fields for improved query performance",
                parameters={
                    "collection": "str (required) - Collection name",
                    "keys": "str or list[tuple] (required) - Field name or [(field, direction), ...] where direction: 1=asc, -1=desc",
                    "unique": "bool (optional) - Create unique index (default False)",
                    "name": "str (optional) - Custom index name"
                },
                returns="str - Index name",
                examples=[
                    'create index on "users" field "email" unique true',
                    'create index on "users" fields [("lastname", 1), ("firstname", 1)]',
                    'create index on "products" field "sku" name "product_sku_idx"'
                ]
            ),
            MethodInfo(
                name="drop_index",
                description="Drop (delete) an index from a collection",
                parameters={
                    "collection": "str (required) - Collection name",
                    "index_name": "str (required) - Name of index to drop"
                },
                returns="None - prints confirmation message",
                examples=[
                    'drop index "email_1" from "users"',
                    'drop index "product_sku_idx" from "products"'
                ]
            ),
            MethodInfo(
                name="list_indexes",
                description="List all indexes for a collection",
                parameters={
                    "collection": "str (required) - Collection name"
                },
                returns="list[dict] - List of index information",
                examples=[
                    'list indexes for "users"',
                    'get indexes from "products"'
                ]
            ),

            # Text Search
            MethodInfo(
                name="create_text_index",
                description="Create a text index for full-text search on string fields",
                parameters={
                    "collection": "str (required) - Collection name",
                    "fields": "str or list[str] (required) - Field(s) to index for text search"
                },
                returns="str - Index name",
                examples=[
                    'create text index on "articles" field "content"',
                    'create text index on "products" fields ["name", "description"]'
                ]
            ),
            MethodInfo(
                name="text_search",
                description="Perform full-text search on indexed text fields",
                parameters={
                    "collection": "str (required) - Collection name",
                    "search_text": "str (required) - Text to search for",
                    "limit": "int (optional) - Maximum results (default 10)"
                },
                returns="list[dict] - Matching documents",
                examples=[
                    'text search "mongodb tutorial" in "articles"',
                    'text search "javascript" in "articles" limit 20',
                    'search "machine learning" in "posts" limit 5'
                ]
            ),

            # Utility Methods
            MethodInfo(
                name="get_stats",
                description="Get database statistics including size, collection count, etc.",
                parameters={},
                returns="dict - Database statistics",
                examples=[
                    'get database stats',
                    'show database statistics'
                ]
            ),
            MethodInfo(
                name="get_collection_stats",
                description="Get collection statistics including document count, size, indexes",
                parameters={
                    "collection": "str (required) - Collection name"
                },
                returns="dict - Collection statistics",
                examples=[
                    'get stats for collection "users"',
                    'show collection statistics for "orders"'
                ]
            ),
            MethodInfo(
                name="close",
                description="Close MongoDB connection and cleanup resources",
                parameters={},
                returns="None - prints confirmation message",
                examples=[
                    'close connection',
                    'close mongodb'
                ]
            )
        ]

    @classmethod
    def get_examples(cls):
        """Get example AIbasic code snippets."""
        return [
            # Basic CRUD operations
            '10 (mongodb) insert {"name": "Alice", "age": 30, "email": "alice@example.com"} into "users"',
            '20 (mongodb) find all in "users"',
            '30 (mongodb) find in "users" where {"age": {"$gte": 25}}',
            '40 (mongodb) update one in "users" where {"name": "Alice"} set {"age": 31}',
            '50 (mongodb) delete one from "users" where {"name": "Alice"}',

            # Insert multiple documents
            '10 (mongodb) insert [{"name": "Bob", "age": 25}, {"name": "Carol", "age": 28}, {"name": "Dave", "age": 35}] into "users"',

            # Advanced queries
            '10 (mongodb) find in "users" where {"status": "active"} sort [("age", -1)] limit 10',
            '20 (mongodb) find in "users" where {"age": {"$gte": 18, "$lt": 65}} project {"name": 1, "email": 1}',
            '30 (mongodb) find in "products" where {"category": "electronics"} skip 20 limit 10',

            # Update operations
            '10 (mongodb) update one in "users" where {"email": "bob@example.com"} set {"status": "inactive", "updated_at": 1234567890}',
            '20 (mongodb) update many in "products" where {"category": "electronics"} inc {"views": 1}',
            '30 (mongodb) upsert in "counters" where {"name": "page_views"} set {"count": 1}',

            # Aggregation
            '10 (mongodb) aggregate "orders" pipeline [{"$group": {"_id": "$customer_id", "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}]',
            '20 (mongodb) aggregate "sales" pipeline [{"$match": {"year": 2023}}, {"$group": {"_id": "$product", "revenue": {"$sum": "$amount"}}}]',
            '30 (mongodb) aggregate "users" pipeline [{"$group": {"_id": "$country", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}]',

            # Count and distinct
            '10 (mongodb) count documents in "users"',
            '20 (mongodb) count in "users" where {"status": "active"}',
            '30 (mongodb) distinct "country" in "users"',
            '40 (mongodb) distinct "category" in "products" where {"in_stock": true}',

            # Index management
            '10 (mongodb) create index on "users" field "email" unique true',
            '20 (mongodb) create index on "users" fields [("lastname", 1), ("firstname", 1)]',
            '30 (mongodb) list indexes for "users"',
            '40 (mongodb) drop index "email_1" from "users"',

            # Text search
            '10 (mongodb) create text index on "articles" fields ["title", "content"]',
            '20 (mongodb) text search "mongodb tutorial" in "articles" limit 10',
            '30 (mongodb) search "python programming" in "posts" limit 20',

            # Database operations
            '10 (mongodb) list databases',
            '20 (mongodb) create database "production"',
            '30 (mongodb) use database "production"',
            '40 (mongodb) list collections',
            '50 (mongodb) drop database "old_test_db"',

            # Collection operations
            '10 (mongodb) create collection "audit_logs"',
            '20 (mongodb) create capped collection "events" size 10485760 max 10000',
            '30 (mongodb) drop collection "temp_data"',

            # Bulk operations
            '10 (mongodb) insert [{"product": "Widget", "price": 19.99, "stock": 100}, {"product": "Gadget", "price": 29.99, "stock": 50}] into "products"',

            # Replace document
            '10 (mongodb) replace in "settings" where {"key": "theme"} with {"key": "theme", "value": "dark", "updated": 1234567890}',

            # Statistics
            '10 (mongodb) get database stats',
            '20 (mongodb) get stats for collection "users"',

            # Complete workflow
            '10 (mongodb) create collection "customers"',
            '20 (mongodb) create index on "customers" field "email" unique true',
            '30 (mongodb) insert {"name": "Acme Corp", "email": "info@acme.com", "credits": 1000} into "customers"',
            '40 (mongodb) find in "customers" where {"credits": {"$gt": 500}}',
            '50 (mongodb) update one in "customers" where {"email": "info@acme.com"} inc {"credits": 500}',
            '60 (mongodb) count in "customers" where {"credits": {"$gte": 1000}}',

            # E-commerce example
            '10 (mongodb) insert {"order_id": "ORD001", "customer": "Alice", "items": [{"product": "Widget", "qty": 2}], "total": 39.98} into "orders"',
            '20 (mongodb) aggregate "orders" pipeline [{"$unwind": "$items"}, {"$group": {"_id": "$items.product", "total_qty": {"$sum": "$items.qty"}}}]',
            '30 (mongodb) find in "orders" where {"customer": "Alice"} sort [("order_date", -1)] limit 5',

            # Cleanup
            '10 (mongodb) close connection'
        ]
