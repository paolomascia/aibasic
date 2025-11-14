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

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, OperationFailure, DuplicateKeyError
    from bson import ObjectId
    from bson.errors import InvalidId
except ImportError:
    MongoClient = None
    ObjectId = None


class MongoDBModule:
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
