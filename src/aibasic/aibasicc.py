#!/usr/bin/env python3
import argparse
import configparser
import json
import sys
import requests
import re

from pathlib import Path
from textwrap import indent

from aibasic.aibasic_intent import determine_intent, InstructionHint
from aibasic.modules.module_base import collect_all_modules_metadata, generate_prompt_context

# ==========================
# CONSTANTS
# ==========================

# Task type definitions with detailed metadata
TASK_TYPES = {
    "csv": {
        "name": "CSV Operations",
        "description": "Reading, writing, or manipulating CSV files",
        "keywords": ["csv", "read_csv", "to_csv"],
        "common_libraries": ["pandas", "csv"],
        "examples": ["read the file data.csv", "save dataframe to output.csv"]
    },
    "excel": {
        "name": "Excel Operations",
        "description": "Working with Excel files (.xlsx, .xls)",
        "keywords": ["excel", "xlsx", "xls", "workbook", "worksheet"],
        "common_libraries": ["pandas", "openpyxl", "xlsxwriter"],
        "examples": ["create Excel file with sales data", "read worksheet from report.xlsx"]
    },
    "json": {
        "name": "JSON Operations",
        "description": "Parsing, creating, or manipulating JSON data",
        "keywords": ["json", "parse json", "to_json"],
        "common_libraries": ["json", "pandas"],
        "examples": ["parse JSON from API response", "convert dataframe to JSON"]
    },
    "xml": {
        "name": "XML Operations",
        "description": "Working with XML files and data",
        "keywords": ["xml", "parse xml", "xpath"],
        "common_libraries": ["xml.etree.ElementTree", "lxml"],
        "examples": ["parse XML configuration", "extract data from XML"]
    },
    "db": {
        "name": "Database Operations",
        "description": "SQL database queries, connections, and data storage",
        "keywords": ["database", "sql", "query", "table", "insert", "select", "update", "delete"],
        "common_libraries": ["sqlite3", "sqlalchemy", "pandas"],
        "examples": ["query customers from database", "insert records into table"]
    },
    "postgres": {
        "name": "PostgreSQL Operations",
        "description": "PostgreSQL-specific operations using connection pool module",
        "keywords": ["postgres database", "postgresql", "from postgres", "into postgres", "pg query"],
        "common_libraries": ["psycopg2"],
        "module": "postgres_module.PostgresModule",
        "examples": [
            "query all customers from postgres",
            "insert data into postgres table users",
            "execute postgres query SELECT * FROM orders"
        ],
        "setup_code": "from aibasic.modules import PostgresModule\npg = PostgresModule.from_config('aibasic.conf')",
        "usage_notes": [
            "Use pg.get_connection() to get a connection from the pool",
            "Always release connections with pg.release_connection(conn)",
            "Or use pg.execute_query() for simple queries with automatic connection management",
            "The module is initialized once and reused across all postgres operations"
        ]
    },
    "mysql": {
        "name": "MySQL/MariaDB Operations",
        "description": "MySQL/MariaDB-specific operations using connection pool module",
        "keywords": ["mysql database", "mariadb", "from mysql", "into mysql", "mysql query"],
        "common_libraries": ["mysql.connector"],
        "module": "mysql_module.MySQLModule",
        "examples": [
            "query all customers from mysql",
            "insert data into mysql table users",
            "execute mysql query SELECT * FROM orders",
            "call mysql stored procedure get_user_data"
        ],
        "setup_code": "from aibasic.modules import MySQLModule\nmysql = MySQLModule.from_config('aibasic.conf')",
        "usage_notes": [
            "Use mysql.get_connection() to get a connection from the pool",
            "Always release connections with mysql.release_connection(conn)",
            "Use mysql.execute_query() for simple queries with automatic connection management",
            "Use mysql.execute_query_dict() to get results as list of dictionaries",
            "Use mysql.call_procedure() for stored procedures",
            "The module is initialized once and reused across all mysql operations"
        ]
    },
    "cassandra": {
        "name": "Apache Cassandra NoSQL Operations",
        "description": "Distributed NoSQL database with high scalability and availability",
        "keywords": ["cassandra", "nosql", "cql", "distributed database", "wide column", "time series"],
        "common_libraries": ["cassandra-driver"],
        "module": "cassandra_module.CassandraModule",
        "examples": [
            "execute cql query on cassandra",
            "insert data into cassandra table",
            "select from cassandra where key equals value",
            "create cassandra keyspace with replication",
            "batch insert multiple rows to cassandra"
        ],
        "setup_code": "from aibasic.modules import CassandraModule\ncass = CassandraModule.from_config('aibasic.conf')",
        "usage_notes": [
            "Use cass.execute() for CQL queries",
            "Use cass.execute_prepared() for better performance with repeated queries",
            "Use cass.execute_batch() for atomic multi-row operations",
            "Use cass.insert() / select() / update() / delete() for CRUD operations",
            "Use cass.create_keyspace() / create_table() for schema management",
            "Supports consistency levels: ONE, QUORUM, ALL, LOCAL_QUORUM, etc.",
            "Use cass.increment_counter() / decrement_counter() for counter columns",
            "TTL supported: specify time-to-live for automatic expiration",
            "Supports clustering: multiple contact_points in config",
            "SSL/TLS with SSL_VERIFY=false for self-signed certs",
            "Load balancing policies: RoundRobinPolicy, DCAwareRoundRobinPolicy, TokenAwarePolicy",
            "Prepared statements are cached automatically for performance",
            "The module is initialized once and reused"
        ]
    },
    "mongodb": {
        "name": "MongoDB NoSQL Operations",
        "description": "Document-oriented NoSQL database with flexible schema and powerful query capabilities",
        "keywords": ["mongodb", "nosql", "document database", "mongo", "collection", "bson"],
        "common_libraries": ["pymongo"],
        "module": "mongodb_module.MongoDBModule",
        "examples": [
            "insert document into mongodb collection",
            "find documents in mongodb where field equals value",
            "update mongodb documents",
            "aggregate data from mongodb collection",
            "create index on mongodb field"
        ],
        "setup_code": "from aibasic.modules import MongoDBModule\nmongo = MongoDBModule.from_config('aibasic.conf')",
        "usage_notes": [
            "Use mongo.insert_one() / insert_many() to insert documents",
            "Use mongo.find() / find_one() to query documents",
            "Use mongo.update_one() / update_many() to update documents",
            "Use mongo.delete_one() / delete_many() to delete documents",
            "Use mongo.aggregate() for aggregation pipelines with $match, $group, $sort, etc.",
            "Use mongo.create_index() / drop_index() for index management",
            "Use mongo.create_text_index() / text_search() for full-text search",
            "Use mongo.bulk_write() for batch operations",
            "Use mongo.count_documents() to count matching documents",
            "Supports SSL/TLS with TLS_ALLOW_INVALID_CERTIFICATES=true for self-signed certs",
            "Connection string format: mongodb://user:pass@host:port/database",
            "Or use individual parameters: HOST, PORT, USERNAME, PASSWORD, DATABASE",
            "ObjectId fields automatically converted to strings in results",
            "Connection pooling configured via MAX_POOL_SIZE and MIN_POOL_SIZE",
            "The module is initialized once and reused"
        ]
    },
    "s3": {
        "name": "S3/MinIO Object Storage Operations",
        "description": "AWS S3 and S3-compatible object storage (MinIO, DigitalOcean Spaces, Wasabi)",
        "keywords": ["s3", "minio", "object storage", "bucket", "upload", "download", "cloud storage"],
        "common_libraries": ["boto3"],
        "module": "s3_module.S3Module",
        "examples": [
            "upload file to s3 bucket",
            "download file from s3",
            "list objects in s3 bucket",
            "create s3 bucket",
            "generate presigned url for s3 object"
        ],
        "setup_code": "from aibasic.modules import S3Module\ns3 = S3Module.from_config('aibasic.conf')",
        "usage_notes": [
            "Use s3.create_bucket() to create buckets",
            "Use s3.upload_file() to upload files with automatic multipart for large files",
            "Use s3.download_file() to download files",
            "Use s3.delete_object() to delete objects",
            "Use s3.copy_object() to copy objects within S3",
            "Use s3.list_objects() to list objects with filtering by prefix",
            "Use s3.generate_presigned_url() for temporary public access URLs",
            "Use s3.upload_directory() to upload entire folders",
            "Use s3.download_directory() to download folders",
            "Use s3.delete_objects() for batch deletions",
            "Supports AWS S3, MinIO, DigitalOcean Spaces, Wasabi, and any S3-compatible storage",
            "Configure ENDPOINT_URL for MinIO or other providers (omit for AWS S3)",
            "Supports server-side encryption (SSE-S3, SSE-KMS, SSE-C)",
            "Multipart uploads automatic for files larger than threshold",
            "Set VERIFY_SSL=false for self-signed certificates (MinIO dev)",
            "The module is initialized once and reused"
        ]
    },
    "api": {
        "name": "API/REST Operations",
        "description": "HTTP/HTTPS REST API calls with multiple authentication methods",
        "keywords": ["api", "rest", "http", "get", "post", "put", "patch", "delete", "request", "endpoint", "json"],
        "common_libraries": ["requests"],
        "module": "restapi_module.RestAPIModule",
        "examples": [
            "call the weather API",
            "POST data to endpoint",
            "make GET request to api endpoint",
            "upload file to api",
            "authenticate with bearer token"
        ],
        "setup_code": "from aibasic.modules import RestAPIModule\napi = RestAPIModule.from_config('aibasic.conf')",
        "usage_notes": [
            "Use api.get() for GET requests",
            "Use api.post() for POST requests with JSON or form data",
            "Use api.put() / patch() / delete() for other HTTP methods",
            "Use api.get_json() / post_json() for automatic JSON response parsing",
            "Use api.upload_file() to upload files",
            "Use api.download_file() to download files",
            "Use api.paginate() to automatically fetch paginated results",
            "Supports authentication: none, basic, bearer, apikey, oauth2",
            "Bearer token: set BEARER_TOKEN in config",
            "Basic auth: set USERNAME and PASSWORD in config",
            "API Key: set API_KEY and API_KEY_HEADER or API_KEY_PARAM in config",
            "OAuth2: set OAUTH2_CLIENT_ID, OAUTH2_CLIENT_SECRET, OAUTH2_TOKEN_URL",
            "Automatic retry logic with exponential backoff",
            "SSL/TLS with VERIFY_SSL=false for self-signed certs",
            "Session management for connection pooling and cookies",
            "The module is initialized once and reused"
        ]
    },
    "ssh": {
        "name": "SSH Remote Server Operations",
        "description": "Secure Shell for remote server management, command execution, and file transfer",
        "keywords": ["ssh", "remote", "server", "sftp", "command", "execute", "transfer", "tunnel", "shell"],
        "common_libraries": ["paramiko"],
        "module": "ssh_module.SSHModule",
        "examples": [
            "execute command on remote server via ssh",
            "transfer file to remote server via sftp",
            "download file from remote server",
            "run shell script on remote host",
            "create ssh tunnel to server"
        ],
        "setup_code": "from aibasic.modules import SSHModule\nssh = SSHModule.from_config('aibasic.conf')",
        "usage_notes": [
            "Use ssh.execute_command() to run commands on remote server",
            "Use ssh.sftp_upload() / sftp_download() for file transfer",
            "Use ssh.start_interactive_shell() for interactive sessions",
            "Use ssh.execute_batch_commands() for multiple commands",
            "Use ssh.local_forward() / remote_forward() for port forwarding",
            "Use ssh.send_signal() to send signals to remote processes",
            "Supports password authentication: set PASSWORD in config",
            "Supports key-based authentication: set KEY_FILE in config",
            "For encrypted keys, set KEY_PASSWORD in config",
            "Host key verification: VERIFY_HOST_KEY=true/false/auto-add",
            "Connection timeouts: TIMEOUT, BANNER_TIMEOUT, AUTH_TIMEOUT",
            "Use KEEPALIVE_INTERVAL for long-running connections",
            "Supports jump hosts/bastion via PROXY_HOST settings",
            "Command output available via stdout and stderr",
            "The module is initialized once and reused"
        ]
    },
    "web": {
        "name": "Web Scraping",
        "description": "Extracting data from websites, HTML parsing",
        "keywords": ["scrape", "web page", "html", "beautifulsoup", "parse html"],
        "common_libraries": ["beautifulsoup4", "requests", "selenium"],
        "examples": ["scrape product prices from website", "extract links from page"]
    },
    "df": {
        "name": "DataFrame Operations",
        "description": "Pandas DataFrame manipulations, filtering, transformations",
        "keywords": ["dataframe", "column", "row", "filter", "group by", "merge", "join"],
        "common_libraries": ["pandas", "numpy"],
        "examples": ["filter rows where age > 30", "group by country and sum sales"]
    },
    "math": {
        "name": "Mathematical Operations",
        "description": "Calculations, statistical operations, numerical analysis",
        "keywords": ["calculate", "sum", "average", "mean", "median", "multiply", "divide", "statistics"],
        "common_libraries": ["numpy", "pandas", "statistics", "math"],
        "examples": ["calculate average revenue", "compute standard deviation"]
    },
    "plot": {
        "name": "Data Visualization",
        "description": "Creating charts, graphs, and visualizations",
        "keywords": ["plot", "chart", "graph", "visualize", "histogram", "scatter", "bar chart"],
        "common_libraries": ["matplotlib", "seaborn", "plotly"],
        "examples": ["create bar chart of sales", "plot time series data"]
    },
    "fs": {
        "name": "File System Operations",
        "description": "File reading, writing, copying, moving, directory operations",
        "keywords": ["file", "save", "write", "read", "copy", "move", "delete", "directory", "folder"],
        "common_libraries": ["os", "pathlib", "shutil"],
        "examples": ["save data to file", "copy files to backup folder"]
    },
    "text": {
        "name": "Text Processing",
        "description": "String manipulation, text parsing, regular expressions",
        "keywords": ["text", "string", "parse", "regex", "split", "replace", "extract"],
        "common_libraries": ["re", "string"],
        "examples": ["extract email addresses from text", "replace all occurrences"]
    },
    "email": {
        "name": "Email Operations",
        "description": "SMTP email sending with attachments, HTML, templates, and batch processing",
        "keywords": ["email", "send email", "smtp", "attachment", "mail", "newsletter"],
        "common_libraries": ["smtplib", "email"],
        "module": "email_module.EmailModule",
        "examples": [
            "send email to customer",
            "send email with attachment",
            "send HTML email with images",
            "send email to multiple recipients",
            "send email using template"
        ],
        "setup_code": "from aibasic.modules import EmailModule\nemail_sender = EmailModule.from_config('aibasic.conf')",
        "usage_notes": [
            "Use email_sender.send_email() for plain text emails",
            "Use email_sender.send_html_email() for HTML emails with styling",
            "Use email_sender.send_template_email() for template-based emails",
            "Attachments: pass list of file paths to attachments parameter",
            "Multiple recipients: use lists for to, cc, bcc parameters",
            "Inline images: use inline_images dict with {cid: filepath}",
            "Email validation: use email_sender.validate_email()",
            "Test connection: use email_sender.test_connection()",
            "Batch sending: use email_sender.send_batch_emails() with delay",
            "Priority levels: 'low', 'normal', 'high'",
            "Supports TLS (port 587) and SSL (port 465) encryption",
            "Common providers: Gmail (smtp.gmail.com:587), Outlook (smtp.office365.com:587)",
            "Gmail requires app passwords (not regular password)",
            "The module is initialized once and reused"
        ]
    },
    "image": {
        "name": "Image Processing",
        "description": "Image manipulation, resizing, filtering, format conversion",
        "keywords": ["image", "photo", "picture", "resize", "crop", "filter"],
        "common_libraries": ["PIL", "Pillow", "opencv"],
        "examples": ["resize image to 800x600", "convert PNG to JPEG"]
    },
    "pdf": {
        "name": "PDF Operations",
        "description": "Reading, creating, or manipulating PDF documents",
        "keywords": ["pdf", "document", "extract text from pdf"],
        "common_libraries": ["PyPDF2", "pdfplumber", "reportlab"],
        "examples": ["extract text from PDF", "create PDF report"]
    },
    "date": {
        "name": "Date/Time Operations",
        "description": "Date parsing, formatting, calculations, time operations",
        "keywords": ["date", "time", "datetime", "timestamp", "parse date", "format date"],
        "common_libraries": ["datetime", "dateutil", "pandas"],
        "examples": ["parse date from string", "calculate days between dates"]
    },
    "rpa": {
        "name": "RPA/Automation",
        "description": "UI automation, keyboard/mouse control, desktop automation",
        "keywords": ["automate", "click", "keyboard", "mouse", "gui", "window"],
        "common_libraries": ["pyautogui", "selenium", "playwright"],
        "examples": ["click button on screen", "type text in application"]
    },
    "ml": {
        "name": "Machine Learning",
        "description": "ML models, training, predictions, data science",
        "keywords": ["model", "train", "predict", "machine learning", "classification", "regression"],
        "common_libraries": ["scikit-learn", "tensorflow", "pytorch"],
        "examples": ["train classification model", "predict customer churn"]
    },
    "compress": {
        "name": "Compression/Archive",
        "description": "Multi-format compression: ZIP, TAR, GZIP, BZIP2, XZ, 7Z with full control",
        "keywords": ["zip", "unzip", "compress", "decompress", "archive", "tar", "gzip", "bzip2", "xz", "7z"],
        "common_libraries": ["zipfile", "tarfile", "gzip", "bz2", "lzma", "py7zr"],
        "module": "compression_module.CompressionModule",
        "examples": [
            "compress folder into zip",
            "extract archive contents",
            "compress with gzip",
            "create tar.gz archive",
            "extract 7z file with password"
        ],
        "setup_code": "from aibasic.modules import CompressionModule\ncomp = CompressionModule()",
        "usage_notes": [
            "Use comp.compress_zip() for ZIP archives with optional password",
            "Use comp.compress_targz() / tarbz2() / tarxz() for TAR archives",
            "Use comp.compress_7z() for 7Z with high compression (requires py7zr)",
            "Use comp.compress_gzip() / bzip2() / xz() for single file compression",
            "Use comp.extract_auto() to auto-detect format and extract",
            "Use comp.compress_auto() to compress based on output file extension",
            "Use comp.list_archive() to inspect archive contents",
            "Use comp.get_archive_info() for archive statistics",
            "Compression level: 0-9 (0=store, 9=best compression)",
            "Include/exclude patterns supported: '*.txt', '*.log'",
            "Password protection: ZIP and 7Z formats",
            "No configuration required - works standalone"
        ]
    },
    "config": {
        "name": "Configuration Management",
        "description": "Reading/writing configuration files (INI, YAML, TOML)",
        "keywords": ["config", "configuration", "ini", "yaml", "toml", "settings"],
        "common_libraries": ["configparser", "yaml", "toml"],
        "examples": ["read settings from config.ini", "update YAML configuration"]
    },
    "log": {
        "name": "Logging Operations",
        "description": "Application logging, log parsing, monitoring",
        "keywords": ["log", "logger", "logging", "parse log"],
        "common_libraries": ["logging"],
        "examples": ["log error message", "parse application logs"]
    },
    "crypto": {
        "name": "Cryptography",
        "description": "Encryption, decryption, hashing, security operations",
        "keywords": ["encrypt", "decrypt", "hash", "crypto", "password", "security"],
        "common_libraries": ["hashlib", "cryptography", "bcrypt"],
        "examples": ["hash password", "encrypt sensitive data"]
    },
    "vault": {
        "name": "HashiCorp Vault Secrets Management",
        "description": "Secure secrets storage and retrieval using HashiCorp Vault with multiple auth methods",
        "keywords": ["vault", "secret", "secrets", "hashicorp", "credentials", "password vault", "sensitive"],
        "common_libraries": ["hvac"],
        "module": "vault_module.VaultModule",
        "examples": [
            "read secret from vault",
            "write secret to vault",
            "get database credentials from vault",
            "encrypt data with vault transit",
            "generate dynamic aws credentials"
        ],
        "setup_code": "from aibasic.modules import VaultModule\nvault = VaultModule.from_config('aibasic.conf')",
        "usage_notes": [
            "Use vault.read_secret('path') to read secrets",
            "Use vault.write_secret('path', {'key': 'value'}) to write secrets",
            "Use vault.list_secrets('path/') to list secrets in a directory",
            "Use vault.delete_secret('path') to delete secrets",
            "Use vault.encrypt('key_name', 'plaintext') for encryption (Transit engine)",
            "Use vault.decrypt('key_name', ciphertext) for decryption",
            "Use vault.read_database_creds('role') for dynamic database credentials",
            "Use vault.read_aws_creds('role') for dynamic AWS credentials",
            "Supports auth methods: token, approle, kubernetes, aws, ldap, github, userpass, cert",
            "Supports KV v1 and v2 secret engines",
            "KV v2 includes versioning: use version parameter in read_secret()",
            "Use vault.get_secret_metadata('path') for version history (KV v2)",
            "Use vault.undelete_secret('path', [versions]) to restore deleted secrets",
            "Use vault.renew_lease(lease_id) to extend dynamic secret leases",
            "SSL/TLS supported with VERIFY_SSL=false for self-signed certs",
            "Vault Enterprise: set NAMESPACE in config for multi-tenancy",
            "The module is initialized once and reused"
        ]
    },
    "shell": {
        "name": "Shell Commands",
        "description": "Running system commands, shell scripts, process execution",
        "keywords": ["execute", "run command", "shell", "subprocess", "system"],
        "common_libraries": ["subprocess", "os"],
        "examples": ["run shell command", "execute batch script"]
    },
    "stream": {
        "name": "Stream Processing",
        "description": "Real-time data streams, message queues, event processing",
        "keywords": ["stream", "kafka", "queue", "message", "event", "subscribe"],
        "common_libraries": ["kafka-python", "pika", "asyncio"],
        "examples": ["consume messages from queue", "process event stream"]
    },
    "rabbitmq": {
        "name": "RabbitMQ Operations",
        "description": "RabbitMQ message broker operations with full SSL/TLS support",
        "keywords": ["rabbitmq", "amqp", "message broker", "publish to rabbitmq", "rabbitmq queue"],
        "common_libraries": ["pika"],
        "module": "rabbitmq_module.RabbitMQModule",
        "examples": [
            "publish message to rabbitmq exchange my_exchange",
            "consume messages from rabbitmq queue my_queue",
            "declare rabbitmq queue with routing key",
            "bind rabbitmq queue to exchange"
        ],
        "setup_code": "from aibasic.modules import RabbitMQModule\nrmq = RabbitMQModule.from_config('aibasic.conf')",
        "usage_notes": [
            "Use rmq.publish_message() to publish messages to exchanges",
            "Use rmq.consume_messages() to consume from queues",
            "Use rmq.declare_exchange() and rmq.declare_queue() to create exchanges/queues",
            "Use rmq.bind_queue() to bind queues to exchanges",
            "Supports SSL/TLS with optional certificate verification",
            "Set SSL_VERIFY=false in config to skip certificate validation (dev only)",
            "The module is initialized once and reused across all rabbitmq operations"
        ]
    },
    "kafka": {
        "name": "Apache Kafka Operations",
        "description": "Apache Kafka streaming platform with full authentication support",
        "keywords": ["kafka", "streaming", "publish to kafka", "kafka topic", "kafka consumer"],
        "common_libraries": ["kafka-python"],
        "module": "kafka_module.KafkaModule",
        "examples": [
            "publish message to kafka topic events",
            "consume messages from kafka topic logs",
            "publish batch of messages to kafka",
            "get kafka topic metadata"
        ],
        "setup_code": "from aibasic.modules import KafkaModule\nkafka = KafkaModule.from_config('aibasic.conf')",
        "usage_notes": [
            "Use kafka.publish_message() to publish single messages",
            "Use kafka.publish_batch() for batch publishing",
            "Use kafka.consume_messages() to consume from topics",
            "Supports all authentication: PLAINTEXT, SASL_PLAINTEXT, SASL_SSL, SSL",
            "Supports SASL mechanisms: PLAIN, SCRAM-SHA-256, SCRAM-SHA-512, GSSAPI",
            "Set SSL_VERIFY=false to skip certificate validation (dev/testing only)",
            "Producer uses automatic JSON serialization for dict messages",
            "Consumer uses automatic JSON deserialization",
            "The module is initialized once and reused across all kafka operations"
        ]
    },
    "redis": {
        "name": "Redis Cache Operations",
        "description": "Redis in-memory data store with full authentication and SSL support",
        "keywords": ["redis", "cache", "redis set", "redis get", "redis hash"],
        "common_libraries": ["redis"],
        "module": "redis_module.RedisModule",
        "examples": [
            "cache data in redis",
            "get value from redis key",
            "set redis hash with user data",
            "publish message to redis channel"
        ],
        "setup_code": "from aibasic.modules import RedisModule\nredis_client = RedisModule.from_config('aibasic.conf')",
        "usage_notes": [
            "Use redis_client.set() / get() for strings",
            "Use redis_client.hset() / hgetall() for hashes",
            "Use redis_client.lpush() / rpop() for lists",
            "Use redis_client.sadd() / smembers() for sets",
            "Use redis_client.zadd() / zrange() for sorted sets",
            "Use redis_client.publish() / subscribe() for pub/sub",
            "Supports SSL/TLS with SSL_VERIFY=false for self-signed certs",
            "Supports password and ACL username authentication",
            "Connection pooling automatic",
            "The module is initialized once and reused"
        ]
    },
    "opensearch": {
        "name": "OpenSearch Search and Analytics",
        "description": "OpenSearch distributed search and analytics engine with full authentication and SSL support",
        "keywords": ["opensearch", "elasticsearch", "search", "index", "query", "aggregate", "full-text"],
        "common_libraries": ["opensearch-py"],
        "module": "opensearch_module.OpenSearchModule",
        "examples": [
            "index document in opensearch",
            "search opensearch for products",
            "query opensearch with filters",
            "aggregate data in opensearch",
            "bulk index documents to opensearch"
        ],
        "setup_code": "from aibasic.modules import OpenSearchModule\nos_client = OpenSearchModule.from_config('aibasic.conf')",
        "usage_notes": [
            "Use os_client.index_document() to index a single document",
            "Use os_client.search() for full-text search with Query DSL",
            "Use os_client.search_simple() for simple field:value searches",
            "Use os_client.bulk_index() for batch indexing",
            "Use os_client.aggregate() for analytics and aggregations",
            "Use os_client.get_document() to retrieve by ID",
            "Use os_client.create_index() / delete_index() for index management",
            "Supports basic auth (username/password) and AWS IAM authentication",
            "Supports SSL/TLS with VERIFY_CERTS=false for self-signed certs",
            "Query DSL: {'match': {'field': 'value'}} for text search",
            "Query DSL: {'term': {'field': 'exact'}} for exact matches",
            "Query DSL: {'range': {'field': {'gte': 10, 'lte': 100}}} for ranges",
            "The module is initialized once and reused"
        ]
    },
    "other": {
        "name": "General/Other",
        "description": "General purpose operations not fitting specific categories",
        "keywords": [],
        "common_libraries": [],
        "examples": ["custom logic", "miscellaneous tasks"]
    }
}

# ==========================
# DYNAMIC MODULE METADATA
# ==========================

# Cache for module metadata (loaded once on first use)
_MODULE_METADATA_CACHE = None

def get_all_task_types():
    """
    Get combined task types from both static TASK_TYPES and dynamic module metadata.

    Returns:
        dict: Combined task type information
    """
    global _MODULE_METADATA_CACHE

    # Load module metadata on first access
    if _MODULE_METADATA_CACHE is None:
        try:
            _MODULE_METADATA_CACHE = collect_all_modules_metadata()
        except Exception as e:
            print(f"[WARNING] Failed to collect module metadata: {e}", file=sys.stderr)
            _MODULE_METADATA_CACHE = {}

    # Start with static TASK_TYPES
    combined = dict(TASK_TYPES)

    # Enhance with dynamic module metadata
    for task_type, module_doc in _MODULE_METADATA_CACHE.items():
        metadata = module_doc.get("metadata", {})

        # Create enhanced task type info from module metadata
        enhanced_info = {
            "name": metadata.get("name", ""),
            "description": metadata.get("description", ""),
            "keywords": metadata.get("keywords", []),
            "common_libraries": [],  # extracted from dependencies
            "examples": [ex for ex in module_doc.get("examples", [])[:3]],  # first 3 examples
            "module_metadata": module_doc  # full module documentation
        }

        # Extract library names from dependencies
        if metadata.get("dependencies"):
            enhanced_info["common_libraries"] = [
                dep.split(">=")[0].split("==")[0].split("[")[0]
                for dep in metadata["dependencies"]
            ]

        # Merge with static definition if exists, otherwise add new
        if task_type in combined:
            # Enhance existing with module metadata
            combined[task_type]["module_metadata"] = module_doc
            if not combined[task_type].get("keywords"):
                combined[task_type]["keywords"] = enhanced_info["keywords"]
        else:
            # Add new task type from module
            combined[task_type] = enhanced_info

    return combined

SYSTEM_PROMPT = (
    '''
    You are an AIBasic-to-Python compiler.
    AIBasic is a simple, natural-language, *numbered* instruction language. Each instruction is independent but is compiled in sequence, and you receive the accumulated context from previous steps.

    Your job is:
    1. Read the current context (a JSON-like description of known variables, last outputs, and their meanings).
    2. Read the current AIBasic instruction (in English, e.g. "read the file customers.csv into a dataframe").
    3. Produce Python code that performs that instruction, using Pandas or standard Python whenever appropriate.
    4. Update the context to tell the compiler what variables now exist, or which variable is the "last output" of this step.
    5. Declare which Python imports are required.

    You MUST respond with a **single valid JSON object** with EXACTLY these keys:
    - "code": string — Python code for this single instruction. Must be runnable in sequence with previous code.
    - "context_updates": object — keys are variable names or meta info (e.g. "df", "last_output"), values are short human-readable descriptions.
    - "needs_imports": array of strings — each string is ONLY what comes after "import" keyword.
      EXAMPLES:
      ✓ CORRECT: ["pandas as pd", "os", "json"]
      ✓ CORRECT: [] (empty if imports already in code)
      ✗ WRONG: ["import pandas as pd"]
      ✗ WRONG: ["from os import path"]

      NOTE: The compiler will add "import " prefix automatically.
      If you need "from X import Y", put it directly in the "code" field instead.

    Rules:
    - Do NOT add explanations, introductions, markdown, or prose. JSON ONLY.
    - If the instruction is ambiguous, make a reasonable assumption and state it in the "context_updates".
    - If you cannot do the instruction, return code that raises a clear Exception and explain the reason in "context_updates".
    - Prefer Pandas for CSV/Excel/table-like operations.
    - If the instruction refers to "the dataframe", assume it refers to the most recent dataframe in context (often stored under "df" or under "last_output").
    - Always set "last_output" in "context_updates" to the most relevant variable produced by this step (e.g. "df").

    **JUMP/GOTO Instructions:**
    - AIBasic supports conditional jumps like "if <condition> jump to line <number>"
    - When you see a jump instruction with an IF condition, generate code that:
      1. Evaluates the condition
      2. Sets a special variable `_aibasic_jump_condition = True` if the condition is met, `False` otherwise
    - Example: "if x > 10 jump to line 50" should generate:
      {
        "code": "_aibasic_jump_condition = (x > 10)",
        "context_updates": {"_aibasic_jump_condition": "True if x > 10, controls jump to line 50"},
        "needs_imports": []
      }
    - The compiler will automatically handle the actual jump based on `_aibasic_jump_condition`

    Output format example (MUST follow this structure):
    {
    "code": "...",
    "context_updates": { ... },
    "needs_imports": [ ... ]
    }
    '''
)

# ==========================
# UTILITY FUNCTIONS
# ==========================
def load_config(path: Path):
    cfg = configparser.ConfigParser()
    read_files = cfg.read(path)
    if not read_files:
        raise FileNotFoundError(f"Config file not found: {path}")
    section = cfg["llm"]
    return {
        "api_url": section.get("API_URL"),
        "api_token": section.get("API_TOKEN"),
        "api_version": section.get("API_VERSION", "1"),
        "model": section.get("MODEL", "gpt-4o-mini"),
    }

def read_aibasic_file(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    instructions = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        instructions.append(line)
    return instructions

def parse_instruction(line: str):
    """
    Parse an instruction line with optional task type and jump detection.

    Examples:
        '10 read the file customers.csv' → (10, 'read the file customers.csv', None, None, False, None, None, False)
        '10 (csv) read the file customers.csv' → (10, 'read the file customers.csv', 'csv', None, False, None, None, False)
        '20 goto 50' → (20, 'goto 50', None, 50, True, None, None, False)
        '30 if x > 10 jump to line 100' → (30, 'if x > 10 jump to line 100', None, 100, False, None, None, False)
        '40 on error goto 200' → (40, 'on error goto 200', None, None, False, 200, None, False)
        '50 call 1000' → (50, 'call 1000', None, None, False, None, 1000, False)
        '60 return' → (60, 'return', None, None, False, None, None, True)

    Returns:
        tuple: (line_number, instruction_text, task_type, jump_target, is_unconditional_jump, error_handler, call_target, is_return)
    """
    import re

    parts = line.split(maxsplit=1)
    if len(parts) == 1:
        return int(parts[0]), "", None, None, False, None, None, False

    num_str, text = parts
    text = text.strip()

    # Check for task type in format (task_type)
    task_type = None
    match = re.match(r'\(([a-z_]+)\)\s*(.*)', text, re.IGNORECASE)
    if match:
        task_type = match.group(1).lower()
        text = match.group(2).strip()

        # Validate task type
        all_types = get_all_task_types()
        if task_type not in all_types:
            print(f"[WARNING] Unknown task type '({task_type})' - will be ignored. Valid types: {', '.join(all_types.keys())}")
            task_type = None

    # Check for RETURN statement
    is_return = False
    return_match = re.match(r'^return$', text, re.IGNORECASE)
    if return_match:
        is_return = True
        print(f"[RETURN] Detected return statement")
        return int(num_str), text, task_type, None, False, None, None, is_return

    # Check for CALL statement: "call <line>"
    call_target = None
    call_match = re.match(r'^call\s+(?:line\s+)?(\d+)$', text, re.IGNORECASE)
    if call_match:
        call_target = int(call_match.group(1))
        print(f"[CALL] Detected subroutine call to line {call_target}")
        return int(num_str), text, task_type, None, False, None, call_target, False

    # Check for error handler: "on error goto <line>"
    error_handler = None
    error_handler_match = re.match(r'^on\s+error\s+(?:goto|jump\s+to)\s+(?:line\s+)?(\d+)$', text, re.IGNORECASE)
    if error_handler_match:
        error_handler = int(error_handler_match.group(1))
        print(f"[ERROR HANDLER] Detected error handler: on error goto {error_handler}")
        return int(num_str), text, task_type, None, False, error_handler, None, False

    # Check for unconditional jump: "goto <line>" or "jump to <line>"
    jump_target = None
    is_unconditional = False

    unconditional_match = re.match(r'^(?:goto|jump\s+to)\s+(?:line\s+)?(\d+)$', text, re.IGNORECASE)
    if unconditional_match:
        jump_target = int(unconditional_match.group(1))
        is_unconditional = True
        print(f"[JUMP] Detected unconditional jump to line {jump_target}")
    else:
        # Check for conditional jump: "if ... jump to line <line>"
        conditional_match = re.search(r'(?:jump\s+to|goto)\s+(?:line\s+)?(\d+)', text, re.IGNORECASE)
        if conditional_match:
            jump_target = int(conditional_match.group(1))
            print(f"[JUMP] Detected conditional jump to line {jump_target}")

    return int(num_str), text, task_type, jump_target, is_unconditional, error_handler, call_target, is_return

def call_llm(conf: dict, context: dict, instruction_text: str, task_type: str = None, mock: bool = False):
    """
    Call the LLM and make sure we get a valid JSON back.
    We try once. If the first response is not JSON, we send a repair prompt.

    Args:
        conf: Configuration dictionary with API settings
        context: Current context with variables and state
        instruction_text: The instruction to compile
        task_type: Optional explicit task type. If None, will be auto-detected
        mock: If True, use mock responses instead of calling the API
    """
    # Use provided task type or detect from instruction
    if task_type is None:
        task_type = detect_task_type(instruction_text)

    # Get detailed task type information
    task_info = get_task_type_info(task_type)

    if mock:
        # --- Simple mock logic for demo purposes ---
        if "read the file" in instruction_text and ".csv" in instruction_text:
            filename = instruction_text.split("file", 1)[1].strip().split()[0]
            code = f"df = pd.read_csv('{filename}')"
            return {
                "code": code,
                "context_updates": {
                    "df": f"pandas.DataFrame containing data from {filename}",
                    "last_output": "df",
                },
                "needs_imports": ["pandas as pd"],
            }
        else:
            return {
                "code": f"# TODO: implement: {instruction_text!r}",
                "context_updates": {"last_output": None},
                "needs_imports": [],
            }

    headers = {
        "Authorization": f"Bearer {conf['api_token']}",
        "Content-Type": "application/json",
    }

    # --- 1) normal prompt ---
    task_hint = (
        f"Task Type: {task_info['name']} ({task_type})\n"
        f"Description: {task_info['description']}\n"
        f"Common Libraries: {', '.join(task_info['common_libraries']) if task_info['common_libraries'] else 'N/A'}\n"
    )

    # Add module-specific information if available
    module_info = ""

    # Check if we have rich module metadata
    if 'module_metadata' in task_info:
        # Use the generate_prompt_context function for rich module documentation
        try:
            module_info = "\n" + generate_prompt_context(task_type) + "\n"
        except Exception as e:
            print(f"[WARNING] Failed to generate module context for {task_type}: {e}", file=sys.stderr)
            # Fall back to basic module info
            if 'module' in task_info:
                module_info = f"\n** MODULE INFORMATION **\n"
                module_info += f"This task type uses the AIBasic module: {task_info['module']}\n"
                if 'setup_code' in task_info:
                    module_info += f"Module setup code:\n{task_info['setup_code']}\n"
                if 'usage_notes' in task_info:
                    module_info += f"Usage notes:\n"
                    for note in task_info['usage_notes']:
                        module_info += f"  - {note}\n"
                module_info += "\n"
    elif 'module' in task_info:
        # Fall back to legacy module info format
        module_info = f"\n** MODULE INFORMATION **\n"
        module_info += f"This task type uses the AIBasic module: {task_info['module']}\n"
        if 'setup_code' in task_info:
            module_info += f"Module setup code (use if module not in context):\n{task_info['setup_code']}\n"
        if 'usage_notes' in task_info:
            module_info += f"Usage notes:\n"
            for note in task_info['usage_notes']:
                module_info += f"  - {note}\n"
        module_info += "\n"

    user_prompt = (
        "You are now compiling ONE AIBasic instruction.\n\n"
        f"{task_hint}\n"
        f"{module_info}"
        "Current CONTEXT (JSON, cumulative from previous steps):\n"
        f"{json.dumps(context, ensure_ascii=False, indent=2)}\n\n"
        f"AIBasic INSTRUCTION to compile:\n{instruction_text}\n\n"
        "Requirements:\n"
        "- Return ONLY a valid JSON object.\n"
        '- Use the exact keys: "code", "context_updates", "needs_imports".\n'
        '- Always set "last_output" in "context_updates".\n'
        f"- Prefer using these libraries for this task type: {', '.join(task_info['common_libraries']) if task_info['common_libraries'] else 'standard library'}\n"
    )

    # Add module-specific requirements
    if 'module_metadata' in task_info or 'module' in task_info:
        module_doc = task_info.get('module_metadata', {})
        metadata = module_doc.get('metadata', {})
        module_name = metadata.get('name', task_info.get('module', 'module'))
        task_type_name = metadata.get('task_type', task_type) if metadata else task_type

        if 'module_metadata' in task_info:
            # Rich metadata available - be very specific
            user_prompt += "\n" + "=" * 70 + "\n"
            user_prompt += "CRITICAL MODULE USAGE REQUIREMENTS:\n"
            user_prompt += "=" * 70 + "\n"
            user_prompt += f"1. MANDATORY: Import and use the {module_name}Module class\n"
            user_prompt += f"   from aibasic.modules import {module_name}Module\n\n"
            user_prompt += f"2. MANDATORY: Create module instance (use existing if in context):\n"
            user_prompt += f"   {task_type_name} = {module_name}Module()\n\n"
            user_prompt += f"3. MANDATORY: Call the appropriate method from the module\n"
            user_prompt += f"   - DO NOT write custom code to implement the functionality\n"
            user_prompt += f"   - DO NOT use external libraries directly (requests, discord.py, etc.)\n"
            user_prompt += f"   - MUST use the module's pre-defined methods documented above\n\n"
            user_prompt += f"4. MANDATORY: Follow the exact method signatures shown in documentation\n"
            user_prompt += f"   - Use the parameter names exactly as documented\n"
            user_prompt += f"   - Pass parameters in the correct format (dict, string, int, etc.)\n\n"
            user_prompt += f"5. IMPORTS: Put the import statement DIRECTLY in your code\n"
            user_prompt += f"   - Include: from aibasic.modules import {module_name}Module\n"
            user_prompt += f"   - Put it in the \"code\" field, NOT in \"needs_imports\"\n"
            user_prompt += f"   - \"needs_imports\" should be [] (empty) for module usage\n\n"
            user_prompt += f"6. Example pattern (adapt to the specific instruction):\n"
            user_prompt += f"   # Your generated code should be:\n"
            user_prompt += f"   from aibasic.modules import {module_name}Module\n"
            user_prompt += f"   {task_type_name} = {module_name}Module()\n"
            user_prompt += f"   result = {task_type_name}.method_name(param1, param2, ...)\n\n"
            user_prompt += "7. FORBIDDEN:\n"
            user_prompt += "   - DO NOT implement webhook calls directly\n"
            user_prompt += "   - DO NOT use requests.post() or similar\n"
            user_prompt += "   - DO NOT create custom HTTP clients\n"
            user_prompt += "   - DO NOT reimplement module functionality\n"
            user_prompt += "   - DO NOT put module imports in \"needs_imports\"\n\n"
            user_prompt += "8. The module methods are ALREADY IMPLEMENTED and TESTED\n"
            user_prompt += "   - Simply call them with correct parameters\n"
            user_prompt += "   - Trust the module to handle the implementation details\n\n"

            # Add concrete example for this specific instruction
            user_prompt += f"9. For THIS specific instruction: '{instruction_text}'\n"
            user_prompt += f"   YOU MUST:\n"
            user_prompt += f"   a) Check if '{task_type_name}' is already in context variables\n"
            user_prompt += f"   b) If not, create it: {task_type_name} = {module_name}Module()\n"
            user_prompt += f"   c) Identify which method matches the instruction (refer to methods list above)\n"
            user_prompt += f"   d) Call that method: result = {task_type_name}.method_name(...)\n"
            user_prompt += f"   e) Store result appropriately\n\n"
            user_prompt += "   CORRECT JSON RESPONSE:\n"
            user_prompt += "   ```json\n"
            user_prompt += "   {\n"
            user_prompt += f'     "code": "from aibasic.modules import {module_name}Module\\n{task_type_name} = {module_name}Module()\\nresult = {task_type_name}.method_name(params...)",\n'
            user_prompt += '     "context_updates": {"' + task_type_name + '": "' + module_name + ' module instance", "result": "method result", "last_output": "result"},\n'
            user_prompt += '     "needs_imports": []\n'
            user_prompt += "   }\n"
            user_prompt += "   ```\n\n"
            user_prompt += "   WRONG JSON RESPONSE (DO NOT DO THIS):\n"
            user_prompt += "   ```json\n"
            user_prompt += "   {\n"
            user_prompt += '     "code": "import requests\\nresponse = requests.post(...)",\n'
            user_prompt += '     "needs_imports": ["from aibasic.modules import ' + module_name + 'Module"]  // WRONG!\n'
            user_prompt += "   }\n"
            user_prompt += "   ```\n"
            user_prompt += "=" * 70 + "\n\n"
        else:
            # Legacy module format
            user_prompt += (
                f"- This instruction uses a specialized AIBasic module with pre-defined methods\n"
                f"- Use the module's methods as documented above - do NOT reimplement functionality\n"
                f"- Follow the parameter names and types exactly as specified in the method documentation\n"
            )

        # Add legacy module requirements if using old format
        if 'module' in task_info and 'setup_code' in task_info:
            user_prompt += (
                f"- If the module variable is not in context, include the setup code in your generated code\n"
                f"- Add the module variable to context_updates so it can be reused in subsequent instructions\n"
            )

    user_prompt += "Return only JSON. Do NOT wrap in markdown.\n"

    # Print prompt details if task type was explicitly specified
    if task_type and 'module_metadata' in task_info:
        print(f"\n[PROMPT] Generating rich prompt for task type: ({task_type})")
        print(f"[PROMPT] Prompt size: {len(user_prompt)} characters")
        print(f"[PROMPT] Module info size: {len(module_info)} characters")
        print(f"[PROMPT] Task hint size: {len(task_hint)} characters")
        print(f"[PROMPT] ---")
        print(f"[PROMPT] Full user prompt being sent to LLM:")
        print(f"[PROMPT] {'=' * 70}")
        # Print prompt with line numbers for easier debugging
        for i, line in enumerate(user_prompt.split('\n'), 1):
            print(f"[PROMPT] {i:4d} | {line}")
        print(f"[PROMPT] {'=' * 70}")
        print(f"[PROMPT] End of prompt\n")

    payload = {
        "model": conf["model"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    }

    resp = requests.post(conf["api_url"], headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"LLM call failed: {resp.status_code} {resp.text}")

    data = resp.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

    # try parse
    parsed = _try_parse_llm_json(content)
    if parsed is not None:
        return _normalize_llm_response(parsed)

    # --- 2) repair attempt ---
    repair_prompt = (
        "Your previous response was NOT valid JSON.\n"
        "You MUST now return the SAME information but as a SINGLE valid JSON object.\n"
        "Use the keys: code, context_updates, needs_imports.\n"
        "Do NOT add explanations. JSON ONLY."
    )

    repair_payload = {
        "model": conf["model"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": content},
            {"role": "user", "content": repair_prompt},
        ],
    }

    repair_resp = requests.post(conf["api_url"], headers=headers, json=repair_payload, timeout=60)
    if repair_resp.status_code != 200:
        raise RuntimeError(f"LLM repair call failed: {repair_resp.status_code} {repair_resp.text}")

    repair_data = repair_resp.json()
    repair_content = repair_data.get("choices", [{}])[0].get("message", {}).get("content", "")

    parsed = _try_parse_llm_json(repair_content)
    if parsed is None:
        # give up, show original content
        raise RuntimeError(f"LLM did not return valid JSON even after repair.\nOriginal:\n{content}\nRepair:\n{repair_content}")

    return _normalize_llm_response(parsed)

def merge_context(old: dict, updates: dict):
    """Merge new updates into the existing context."""
    new_ctx = dict(old)
    new_ctx.update(updates or {})
    return new_ctx

def detect_task_type(instruction: str) -> str:
    """
    Detect task type from instruction text based on keywords.
    This is a fallback when task type is not explicitly specified.

    Args:
        instruction: The instruction text to analyze

    Returns:
        str: The detected task type (defaults to "other" if no match found)
    """
    text = instruction.lower()

    # Score each task type based on keyword matches
    scores = {}
    all_types = get_all_task_types()
    for task_type, metadata in all_types.items():
        score = 0
        keywords = metadata.get("keywords", [])
        for keyword in keywords:
            if keyword.lower() in text:
                # Weight longer keywords more heavily to avoid false positives
                score += len(keyword.split())
        if score > 0:
            scores[task_type] = score

    # Return the task type with highest score, or "other" if no matches
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    return "other"

def get_task_type_info(task_type: str) -> dict:
    """
    Get detailed information about a task type.

    Args:
        task_type: The task type identifier

    Returns:
        dict: Task type metadata including description, libraries, examples
    """
    all_types = get_all_task_types()
    return all_types.get(task_type, all_types.get("other", TASK_TYPES["other"]))

def _try_parse_llm_json(text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # try common bad pattern: ```json ... ```
        text = text.strip()
        if text.startswith("```"):
            text = text.strip("`")
            # sometimes it's "json\n{...}"
            if text.startswith("json"):
                text = text[len("json"):].strip()
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return None
        return None


def _normalize_llm_response(parsed: dict):
    code = parsed.get("code", "")
    ctx = parsed.get("context_updates", {}) or {}
    needs = parsed.get("needs_imports", []) or []
    # always enforce last_output
    if "last_output" not in ctx:
        ctx["last_output"] = None
    return {
        "code": code,
        "context_updates": ctx,
        "needs_imports": needs,
    }


# ==========================
# MAIN LOGIC
# ==========================
def main():
    parser = argparse.ArgumentParser(description="AIBasic → Python compiler")
    parser.add_argument("-c", "--config", required=True, help="path to aibasic.conf")
    parser.add_argument("-i", "--input", required=True, help="AIBasic source file")
    parser.add_argument("-o", "--output", required=True, help="output Python file")
    args = parser.parse_args()

    conf_path = Path(args.config)
    src_path = Path(args.input)
    out_path = Path(args.output)

    try:
        conf = load_config(conf_path)
    except Exception as e:
        print(f"[ERROR] loading config: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        instructions = read_aibasic_file(src_path)
    except Exception as e:
        print(f"[ERROR] reading source: {e}", file=sys.stderr)
        sys.exit(1)

    # Initial context
    context = {
        "description": "Context for AIBasic → Python compilation. Holds variable descriptions and last output.",
        "last_output": None,
        "variables": {}
    }

    generated_codes = []
    collected_imports = set()

    print("=== AIBASIC COMPILER START ===")
    print(f"Config file: {conf_path}")
    print(f"Source file: {src_path}")
    print(f"Output file: {out_path}")
    print()

    parsed_instructions = [parse_instruction(line) for line in instructions]
    parsed_instructions.sort(key=lambda t: t[0])

    # Check if any jumps, error handlers, or subroutines exist in the program
    has_jumps = any(jump_target is not None for _, _, _, jump_target, _, _, _, _ in parsed_instructions)
    has_error_handlers = any(error_handler is not None for _, _, _, _, _, error_handler, _, _ in parsed_instructions)
    has_subroutines = any(call_target is not None or is_return for _, _, _, _, _, _, call_target, is_return in parsed_instructions)

    # Track current error handler (can be updated by "on error goto" instructions)
    current_error_handler = None

    for line_num, instr_text, explicit_task_type, jump_target, is_unconditional, error_handler, call_target, is_return in parsed_instructions:
        print(f"\n--- Compiling instruction {line_num} ---")
        print(f"Text: {instr_text}")

        if explicit_task_type:
            print(f"[TASK TYPE] Explicit: ({explicit_task_type})")

            # Get detailed task type information
            task_info = get_task_type_info(explicit_task_type)
            print(f"[TASK TYPE] Name: {task_info.get('name', 'Unknown')}")
            print(f"[TASK TYPE] Description: {task_info.get('description', 'N/A')}")

            # Check if module has rich metadata
            if 'module_metadata' in task_info:
                module_meta = task_info['module_metadata']
                metadata = module_meta.get('metadata', {})
                print(f"[METADATA] ✓ Rich module metadata available")
                print(f"[METADATA]   Version: {metadata.get('version', 'N/A')}")
                print(f"[METADATA]   Methods: {len(module_meta.get('methods', []))}")
                print(f"[METADATA]   Usage Notes: {len(module_meta.get('usage_notes', []))}")
                print(f"[METADATA]   Examples: {len(module_meta.get('examples', []))}")
                print(f"[METADATA]   Dependencies: {', '.join(metadata.get('dependencies', []))}")

                # Print first few methods
                methods = module_meta.get('methods', [])
                if methods:
                    print(f"[METADATA]   Available methods:")
                    for method in methods[:5]:  # Show first 5 methods
                        print(f"[METADATA]     - {method.get('name')}: {method.get('description', '')[:60]}")
                    if len(methods) > 5:
                        print(f"[METADATA]     ... and {len(methods) - 5} more")
            else:
                print(f"[METADATA] Using legacy format (no rich metadata)")
                libraries = task_info.get('common_libraries', [])
                if libraries:
                    print(f"[METADATA]   Common libraries: {', '.join(libraries)}")

        if jump_target:
            print(f"[CONTROL] Jump target: {jump_target} ({'unconditional' if is_unconditional else 'conditional'})")
        if error_handler:
            print(f"[CONTROL] Error handler: on error goto {error_handler}")
        if call_target:
            print(f"[CONTROL] Subroutine call to line {call_target}")
        if is_return:
            print(f"[CONTROL] Return from subroutine")

        # Handle RETURN statement
        if is_return:
            code = "if _call_stack:\n"
            code += "    _next_line = _call_stack.pop()\n"
            code += "else:\n"
            code += "    _next_line = None  # End program if no return address\n"
            generated_codes.append(f"# {line_num} {instr_text}\n{code}")
            continue

        # Handle CALL statement
        if call_target is not None:
            # Find next line number for return address
            current_idx = next(i for i, (ln, _, _, _, _, _, _, _) in enumerate(parsed_instructions) if ln == line_num)
            if current_idx < len(parsed_instructions) - 1:
                return_line = parsed_instructions[current_idx + 1][0]
                code = f"_call_stack.append({return_line})\n"
                code += f"_next_line = {call_target}\n"
            else:
                # Last line - no return address
                code = f"_next_line = {call_target}\n"
            generated_codes.append(f"# {line_num} {instr_text}\n{code}")
            continue

        # Handle error handler directive
        if error_handler is not None:
            current_error_handler = error_handler
            code = f"_error_handler = {error_handler}"
            generated_codes.append(f"# {line_num} {instr_text}\n{code}\n")
            continue

        # Handle unconditional jumps
        if is_unconditional:
            # Generate jump using program counter
            code = f"_next_line = {jump_target}"
            generated_codes.append(f"# {line_num} {instr_text}\n{code}\n")
            continue

        hint = determine_intent(instr_text)
        print("[INTENT]", hint.to_dict())

        result = call_llm(conf, context, instr_text, task_type=explicit_task_type)

        required_keys = ("code", "context_updates", "needs_imports")
        for k in required_keys:
            if k not in result:
                raise RuntimeError(f"LLM result missing key {k}: {result}")

        print("Raw LLM result:")
        print(indent(json.dumps(result, ensure_ascii=False, indent=2), "  "))

        context = merge_context(context, result.get("context_updates", {}))

        # update context['variables']
        updates = result.get("context_updates", {})
        if updates:
            if "variables" not in context or not isinstance(context["variables"], dict):
                context["variables"] = {}
            for k, v in updates.items():
                if k not in ("last_output", "description"):
                    context["variables"][k] = v

        print("Updated context:")
        print(indent(json.dumps(context, ensure_ascii=False, indent=2), "  "))

        code = result.get("code", "")
        if code:
            # If this is a conditional jump, add the jump after condition
            if jump_target and not is_unconditional:
                # Add conditional jump using program counter
                code += f"\nif _aibasic_jump_condition:\n"
                code += f"    _next_line = {jump_target}\n"

            generated_codes.append(f"# {line_num} {instr_text}\n{code}\n")

        for imp in result.get("needs_imports", []):
            collected_imports.add(imp)

    # Write the output file
    with out_path.open("w", encoding="utf-8") as f:
        if collected_imports:
            for imp in sorted(collected_imports):
                f.write(f"import {imp}\n")
            f.write("\n")

        f.write("# === Generated by AIBasic Compiler ===\n\n")

        if has_jumps or has_error_handlers or has_subroutines:
            # Collect all variables from context
            all_variables = set()
            if "variables" in context and isinstance(context["variables"], dict):
                all_variables.update(context["variables"].keys())
            # Remove internal/meta variables
            all_variables.discard("last_output")
            all_variables.discard("description")

            # Generate a function for each line
            for idx, (line_num, _, _, _, _, _, _, _) in enumerate(parsed_instructions):
                f.write(f"def _line_{line_num}():\n")

                # Declare global variables (include _error_handler and _call_stack if needed)
                globals_list = ["_next_line"]
                if has_error_handlers:
                    globals_list.append("_error_handler")
                if has_subroutines:
                    globals_list.append("_call_stack")
                globals_list.extend(sorted(all_variables))
                f.write(f"    global {', '.join(globals_list)}\n")

                # Write the code for this line
                code = generated_codes[idx]
                for code_line in code.split('\n'):
                    if code_line.strip() and not code_line.strip().startswith('#'):
                        f.write(f"    {code_line}\n")
                    elif code_line.strip().startswith('#'):
                        f.write(f"    {code_line}\n")

                # Set next line if no jump occurred
                if idx < len(parsed_instructions) - 1:
                    next_line_num = parsed_instructions[idx + 1][0]
                    f.write(f"    if _next_line is None:\n")
                    f.write(f"        _next_line = {next_line_num}\n")

                f.write("\n")

            # Generate main function with dispatch loop
            f.write("def main():\n")

            # Declare global variables in main
            globals_list = ["_next_line"]
            if has_error_handlers:
                globals_list.append("_error_handler")
            if has_subroutines:
                globals_list.append("_call_stack")
            globals_list.extend(sorted(all_variables))
            f.write(f"    global {', '.join(globals_list)}\n")

            f.write("    _current_line = " + str(parsed_instructions[0][0]) + "\n")
            f.write("    _next_line = None\n")
            if has_error_handlers:
                f.write("    _error_handler = None  # Error handler line number\n")
            if has_subroutines:
                f.write("    _call_stack = []  # Stack for subroutine return addresses\n")
            f.write("\n")

            f.write("    # Line dispatch table\n")
            f.write("    _line_functions = {\n")
            for line_num, _, _, _, _, _, _, _ in parsed_instructions:
                f.write(f"        {line_num}: _line_{line_num},\n")
            f.write("    }\n\n")

            f.write("    while _current_line is not None:\n")
            f.write("        _next_line = None\n")
            f.write("        line_func = _line_functions.get(_current_line)\n")
            f.write("        if line_func:\n")

            if has_error_handlers:
                # Wrap function call in try-except when error handlers are present
                f.write("            try:\n")
                f.write("                line_func()\n")
                f.write("            except Exception as e:\n")
                f.write("                if _error_handler is not None:\n")
                f.write("                    # Store error information in globals\n")
                f.write("                    globals()['_last_error'] = e\n")
                f.write("                    globals()['_last_error_line'] = _current_line\n")
                f.write("                    _next_line = _error_handler\n")
                f.write("                else:\n")
                f.write("                    raise  # Re-raise if no error handler is set\n")
            else:
                f.write("            line_func()\n")

            f.write("        else:\n")
            f.write("            break\n")
            f.write("        _current_line = _next_line\n\n")

            f.write("if __name__ == '__main__':\n")
            f.write("    main()\n")
        else:
            # Simple linear code
            for code in generated_codes:
                f.write(code)
                if not code.endswith("\n"):
                    f.write("\n")

    print("\n=== COMPILATION COMPLETE ===")
    print(f"Generated file: {out_path}")


if __name__ == "__main__":
    main()
