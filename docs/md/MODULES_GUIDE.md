# AIBasic Modules System Guide

## Overview

The AIBasic Modules System extends the compiler with reusable, stateful components that can be configured and used across multiple instructions. This is particularly useful for:

- Database connections with connection pooling
- API clients with authentication
- Resource management (files, sockets, etc.)
- Shared caches and state
- External service integrations

## Architecture

```
AIBasic Instruction → Compiler → LLM (with module info) → Generated Python Code
                                                          ↓
                                                    Uses Module
                                                          ↓
                                              Module (initialized once)
                                                          ↓
                                              External Resource (DB, API, etc.)
```

## Key Concepts

### 1. Module Initialization

Modules are initialized **once** and reused across all instructions:

```python
# First postgres instruction
pg = PostgresModule.from_config('aibasic.conf')  # Initialize

# Subsequent instructions
pg.execute_query(...)  # Reuse existing instance
```

### 2. Configuration-Driven

Modules load settings from `aibasic.conf`:

```ini
[postgres]
HOST = localhost
DATABASE = mydb
USER = postgres
PASSWORD = secret
```

### 3. Context Awareness

The compiler tracks initialized modules in the context:

```json
{
  "pg": "PostgresModule instance connected to 'mydb'",
  "last_output": "query_results"
}
```

The LLM uses this context to avoid re-initializing modules.

### 4. Task Type Integration

Modules are associated with specific task types:

```python
"postgres": {
    "name": "PostgreSQL Operations",
    "module": "postgres_module.PostgresModule",
    "setup_code": "from aibasic.modules import PostgresModule\npg = PostgresModule.from_config('aibasic.conf')",
    ...
}
```

## Using the PostgreSQL Module

### Setup

1. **Install dependencies**:
```bash
pip install psycopg2-binary
```

2. **Configure** `aibasic.conf`:
```ini
[postgres]
HOST = localhost
PORT = 5432
DATABASE = mydb
USER = postgres
PASSWORD = secret
MIN_CONNECTIONS = 1
MAX_CONNECTIONS = 10
```

3. **Write AIBasic code**:
```aibasic
10 (postgres) query all customers from postgres
20 (postgres) insert into postgres table users values ('Alice', 30)
30 (postgres) execute postgres query SELECT * FROM orders WHERE total > 100
```

### Generated Code Example

**AIBasic Input**:
```aibasic
10 (postgres) query all customers from postgres where age > 25
20 (df) convert results to dataframe
30 (csv) save dataframe to customers.csv
```

**Generated Python**:
```python
from aibasic.modules import PostgresModule
import pandas as pd

# 10 (postgres) query all customers from postgres where age > 25
pg = PostgresModule.from_config('aibasic.conf')
results = pg.execute_query("SELECT * FROM customers WHERE age > %s", (25,))

# 20 (df) convert results to dataframe
df = pd.DataFrame(results, columns=['id', 'name', 'age', 'email'])

# 30 (csv) save dataframe to customers.csv
df.to_csv('customers.csv', index=False)
```

## Module API Reference

### PostgresModule

#### Class Methods

**`from_config(config_path: str) -> PostgresModule`**
- Singleton initializer from configuration file
- Returns cached instance if already initialized
- Thread-safe initialization

#### Instance Methods

**`get_connection() -> connection`**
- Get a connection from the pool
- Blocks if all connections are in use
- Must be paired with `release_connection()`

**`release_connection(conn) -> None`**
- Return connection to the pool
- Always call in a `finally` block

**`execute_query(query: str, params: tuple = None, fetch: bool = True) -> list`**
- Execute query with automatic connection management
- Use `%s` placeholders for parameters (prevents SQL injection)
- Set `fetch=False` for INSERT/UPDATE/DELETE

**`execute_many(query: str, params_list: list) -> None`**
- Batch execute for multiple parameter sets
- More efficient than multiple `execute_query()` calls

**`close_all_connections() -> None`**
- Close all connections in the pool
- Called automatically on program exit

**`get_pool_status() -> dict`**
- Get current pool configuration and status

### Usage Patterns

#### Simple Query
```python
results = pg.execute_query("SELECT * FROM customers")
```

#### Parameterized Query
```python
results = pg.execute_query(
    "SELECT * FROM customers WHERE age > %s AND country = %s",
    (25, 'USA')
)
```

#### Insert/Update
```python
pg.execute_query(
    "INSERT INTO customers (name, age) VALUES (%s, %s)",
    ('Alice', 30),
    fetch=False
)
```

#### Batch Insert
```python
pg.execute_many(
    "INSERT INTO customers (name, age) VALUES (%s, %s)",
    [('Alice', 30), ('Bob', 25), ('Charlie', 35)]
)
```

#### Manual Connection Management
```python
conn = pg.get_connection()
try:
    cursor = conn.cursor()
    cursor.execute("BEGIN")
    cursor.execute("INSERT INTO ...")
    cursor.execute("UPDATE ...")
    conn.commit()
finally:
    pg.release_connection(conn)
```

## MySQL Module

Similar to PostgreSQL, a MySQL/MariaDB module is available with additional features.

### Setup

1. **Install dependencies**:
```bash
pip install mysql-connector-python
```

2. **Configure** `aibasic.conf`:
```ini
[mysql]
HOST = localhost
PORT = 3306
DATABASE = mydb
USER = root
PASSWORD = secret
MIN_CONNECTIONS = 1
MAX_CONNECTIONS = 10
CHARSET = utf8mb4
```

3. **Write AIBasic code**:
```aibasic
10 (mysql) query all customers from mysql
20 (mysql) insert into mysql table users values ('Alice', 30)
30 (mysql) call mysql stored procedure get_monthly_report
```

### MySQL-Specific Features

#### Dictionary Results
```python
# Get results as list of dictionaries (easier to work with)
results = mysql.execute_query_dict("SELECT * FROM customers WHERE age > %s", (25,))
# [{'id': 1, 'name': 'Alice', 'age': 30}, ...]
```

#### Stored Procedures
```python
# Call stored procedure with parameters
results = mysql.call_procedure('get_user_orders', (user_id,))
```

#### Character Set Configuration
MySQL module supports configurable character encoding (default: utf8mb4 for full Unicode support)

## RabbitMQ Module

The RabbitMQ module provides AMQP message broker operations with full SSL/TLS support.

### Setup

1. **Install dependencies**:
```bash
pip install pika
```

2. **Configure** `aibasic.conf`:
```ini
[rabbitmq]
HOST = localhost
PORT = 5672
VHOST = /
USERNAME = guest
PASSWORD = guest

# SSL/TLS Settings (optional)
USE_SSL = false
SSL_VERIFY = true  # Set to false for self-signed certs
SSL_CA_CERT = /path/to/ca_cert.pem
SSL_CLIENT_CERT = /path/to/client_cert.pem
SSL_CLIENT_KEY = /path/to/client_key.pem
```

3. **Write AIBasic code**:
```aibasic
10 (rabbitmq) declare rabbitmq exchange my_exchange type topic
20 (rabbitmq) declare rabbitmq queue my_queue durable
30 (rabbitmq) bind queue my_queue to exchange my_exchange with routing key events.*
40 (rabbitmq) publish message "Hello" to exchange my_exchange with routing key events.test
50 (rabbitmq) get one message from rabbitmq queue my_queue
```

### RabbitMQ-Specific Features

#### Exchange Types
Supports all RabbitMQ exchange types: `direct`, `topic`, `fanout`, `headers`

#### SSL/TLS Configuration
Full support for SSL/TLS with optional certificate verification (useful for self-signed certificates in dev/test environments)

#### Pub/Sub Patterns
- Publisher-only mode
- Consumer mode (blocking or non-blocking)
- Request-reply patterns

## Kafka Module

The Kafka module provides distributed streaming platform operations with comprehensive authentication support.

### Setup

1. **Install dependencies**:
```bash
pip install kafka-python
```

2. **Configure** `aibasic.conf`:
```ini
[kafka]
BOOTSTRAP_SERVERS = localhost:9092
SECURITY_PROTOCOL = PLAINTEXT  # PLAINTEXT, SASL_PLAINTEXT, SASL_SSL, SSL

# SASL Settings (if using SASL)
SASL_MECHANISM = PLAIN  # PLAIN, SCRAM-SHA-256, SCRAM-SHA-512, GSSAPI
SASL_USERNAME = user
SASL_PASSWORD = password

# SSL/TLS Settings (if using SSL)
SSL_VERIFY = true  # Set to false for self-signed certs
SSL_CA_CERT = /path/to/ca-cert.pem
SSL_CLIENT_CERT = /path/to/client-cert.pem
SSL_CLIENT_KEY = /path/to/client-key.pem
```

3. **Write AIBasic code**:
```aibasic
10 (kafka) publish message "Hello Kafka" to kafka topic events
20 (kafka) publish JSON message {"user": "Alice"} to topic user_events
30 (kafka) consume messages from kafka topic notifications
40 (kafka) publish batch of messages to kafka topic logs
```

### Kafka-Specific Features

#### Security Protocols
- **PLAINTEXT**: No security (dev only)
- **SASL_PLAINTEXT**: SASL authentication without encryption
- **SASL_SSL**: SASL authentication with SSL encryption
- **SSL**: SSL encryption with client certificates

#### SASL Mechanisms
- **PLAIN**: Simple username/password
- **SCRAM-SHA-256**: Salted Challenge Response (recommended)
- **SCRAM-SHA-512**: Stronger SCRAM variant
- **GSSAPI**: Kerberos authentication

#### JSON Serialization
Automatic JSON serialization/deserialization for messages

## Redis Module

The Redis module provides in-memory data store operations for caching and key-value storage.

### Setup

1. **Install dependencies**:
```bash
pip install redis
```

2. **Configure** `aibasic.conf`:
```ini
[redis]
HOST = localhost
PORT = 6379
DB = 0
PASSWORD = secret

# SSL/TLS Settings (optional)
USE_SSL = false
SSL_VERIFY = true  # Set to false for self-signed certs
SSL_CA_CERT = /path/to/ca.pem
SSL_CLIENT_CERT = /path/to/client-cert.pem
SSL_CLIENT_KEY = /path/to/client-key.pem

# ACL Authentication (Redis 6+)
USERNAME = default

# Connection Pool
MAX_CONNECTIONS = 50
SOCKET_TIMEOUT = 5
```

3. **Write AIBasic code**:
```aibasic
10 (redis) set redis key user:name to value "Alice" with expiration 3600 seconds
20 (redis) get value from redis key user:name
30 (redis) set redis hash user:123 with data {"name": "Bob", "age": 30}
40 (redis) increment redis counter page_views
50 (redis) publish message to redis channel notifications
```

### Redis-Specific Features

#### Data Types Support
- **Strings**: Simple key-value pairs with optional expiration
- **Hashes**: Field-value pairs (like dictionaries)
- **Lists**: Ordered collections (queues, stacks)
- **Sets**: Unique unordered collections
- **Sorted Sets**: Sets with scores (leaderboards)

#### Pub/Sub Messaging
Real-time message publishing and subscription to channels

#### Pipeline Operations
Batch multiple operations for better performance

#### Authentication Methods
- No authentication (dev/test)
- Password authentication (AUTH command)
- ACL username/password (Redis 6+)

## OpenSearch Module

The OpenSearch module provides distributed search and analytics operations with full authentication support.

### Setup

1. **Install dependencies**:
```bash
pip install opensearch-py

# For AWS OpenSearch Service (optional):
pip install boto3 requests-aws4auth
```

2. **Configure** `aibasic.conf`:
```ini
[opensearch]
HOST = localhost
PORT = 9200
USE_SSL = false
VERIFY_CERTS = true  # Set to false for self-signed certs

# Basic Authentication
USERNAME = admin
PASSWORD = admin

# AWS IAM Authentication (for AWS OpenSearch Service)
# USE_AWS_AUTH = true
# AWS_REGION = us-east-1

# SSL/TLS Settings (optional)
# CA_CERTS = /path/to/ca.pem
# CLIENT_CERT = /path/to/client-cert.pem
# CLIENT_KEY = /path/to/client-key.pem

# Connection Settings
TIMEOUT = 30
MAX_RETRIES = 3
POOL_MAXSIZE = 10
```

3. **Write AIBasic code**:
```aibasic
10 (opensearch) create opensearch index products
20 (opensearch) index document {"name": "Laptop", "price": 999} in opensearch index products
30 (opensearch) search opensearch for products matching "laptop"
40 (opensearch) aggregate opensearch products by category
50 (opensearch) bulk index 1000 documents to opensearch index products
```

### OpenSearch-Specific Features

#### Full-Text Search
Advanced search capabilities with Query DSL:
- **Match queries**: Analyzed full-text search
- **Term queries**: Exact value matching
- **Range queries**: Numeric/date ranges
- **Bool queries**: Complex combinations (must, should, must_not)
- **Multi-match**: Search across multiple fields

#### Aggregations
Powerful analytics capabilities:
- **Metrics**: avg, sum, min, max, stats, cardinality
- **Bucket**: terms, date_histogram, histogram, range
- **Pipeline**: Aggregations on aggregations

#### Bulk Operations
Efficient batch processing:
- Bulk indexing for high throughput
- Bulk updates and deletes
- Configurable batch sizes

#### Index Management
Full index lifecycle control:
- Create/delete indices
- Update mappings and settings
- Refresh for real-time visibility
- Index statistics and health monitoring

#### Authentication Methods
- No authentication (dev/test)
- Basic authentication (username/password)
- AWS IAM (for AWS OpenSearch Service)
- SSL/TLS with optional certificate verification

#### Use Cases
- **E-commerce**: Product search, faceted navigation, autocomplete
- **Log Analytics**: Real-time log aggregation and analysis
- **Business Intelligence**: Complex analytics and dashboards
- **Content Management**: Full-text search across documents
- **Application Search**: Search-as-you-type, fuzzy matching

## MongoDB Module

The MongoDB module provides document-oriented NoSQL database operations with flexible schema and powerful query capabilities.

### Setup

1. **Install dependencies**:
```bash
pip install pymongo
```

2. **Configure** `aibasic.conf`:
```ini
[mongodb]
# Connection String (recommended - overrides individual parameters if set)
CONNECTION_STRING = mongodb://username:password@localhost:27017/mydb?authSource=admin

# Or use individual parameters:
HOST = localhost
PORT = 27017
DATABASE = mydb
USERNAME = admin
PASSWORD = secret
AUTH_SOURCE = admin

# SSL/TLS Settings (optional)
TLS = false
TLS_ALLOW_INVALID_CERTIFICATES = false  # Set to true for self-signed certs (dev only)
TLS_CA_FILE = /path/to/ca.pem
TLS_CERT_KEY_FILE = /path/to/client.pem

# Connection Pool Settings
MAX_POOL_SIZE = 100
MIN_POOL_SIZE = 0

# Timeout Settings (milliseconds)
SERVER_SELECTION_TIMEOUT_MS = 30000
CONNECT_TIMEOUT_MS = 20000
SOCKET_TIMEOUT_MS = 20000

# Replica Set (optional)
REPLICA_SET = rs0

# Read/Write Preferences
READ_PREFERENCE = primary
W = 1
```

3. **Write AIBasic code**:
```aibasic
10 (mongodb) insert document {"name": "Alice", "age": 30} into mongodb collection users
20 (mongodb) find documents in mongodb users where age greater than 25
30 (mongodb) update mongodb users set status to active where city equals Boston
40 (mongodb) aggregate mongodb orders group by customer sum total_price
50 (mongodb) create index on mongodb users email field
```

### MongoDB-Specific Features

#### Document Operations
Flexible CRUD operations on JSON-like documents:
- **insert_one()** / **insert_many()**: Insert documents
- **find()** / **find_one()**: Query with filters, projections, sorting
- **update_one()** / **update_many()**: Update with operators ($set, $inc, $push, etc.)
- **delete_one()** / **delete_many()**: Remove documents
- **count_documents()**: Count matching documents

#### Query Operators
Rich query language:
- **Comparison**: $eq, $gt, $gte, $lt, $lte, $ne, $in, $nin
- **Logical**: $and, $or, $not, $nor
- **Element**: $exists, $type
- **Array**: $all, $elemMatch, $size
- **Regex**: Pattern matching on strings

#### Aggregation Pipelines
Powerful data processing framework:
- **$match**: Filter documents
- **$group**: Group by fields with accumulators ($sum, $avg, $max, $min, $count)
- **$sort**: Order results
- **$project**: Reshape documents
- **$limit** / **$skip**: Pagination
- **$lookup**: Joins between collections
- **$unwind**: Deconstruct arrays

#### Indexing
Performance optimization:
- **Single field indexes**: Speed up queries on specific fields
- **Compound indexes**: Multi-field indexes
- **Text indexes**: Full-text search capability
- **Unique indexes**: Enforce uniqueness constraints
- **TTL indexes**: Automatic document expiration

#### Text Search
Full-text search capabilities:
- Create text indexes on string fields
- Search with natural language queries
- Relevance scoring
- Language-specific stemming

#### Bulk Operations
Efficient batch processing:
- Mixed operations (insert, update, delete) in single batch
- Ordered or unordered execution
- Automatic batching for large datasets

#### GridFS
Large file storage (files > 16MB):
- Store files as chunks in MongoDB
- Stream large files efficiently
- Metadata storage for file attributes

#### Transactions
ACID guarantees across multiple documents/collections:
- Multi-document transactions
- Read/write isolation
- Automatic rollback on failure

#### Connection Pooling
Automatic connection management:
- Configurable pool size
- Connection reuse
- Thread-safe operations

#### Use Cases
- **Content Management**: Flexible schema for varied content types
- **User Profiles**: Dynamic user data with nested documents
- **E-commerce Catalogs**: Product catalogs with varying attributes
- **IoT Data**: Time-series sensor data with flexible structure
- **Mobile Apps**: JSON-native backend for mobile applications
- **Real-time Analytics**: Aggregation pipelines for on-the-fly analytics

## Cassandra Module

The Cassandra module provides distributed NoSQL wide-column database operations with high scalability and availability.

### Setup

1. **Install dependencies**:
```bash
pip install cassandra-driver
```

2. **Configure** `aibasic.conf`:
```ini
[cassandra]
CONTACT_POINTS = localhost,node2.example.com,node3.example.com
PORT = 9042
KEYSPACE = my_keyspace

# Authentication
USERNAME = cassandra
PASSWORD = cassandra

# SSL/TLS Settings (optional)
USE_SSL = false
SSL_VERIFY = true  # Set to false for self-signed certs
SSL_CA_CERT = /path/to/ca.pem

# Connection Settings
CONSISTENCY_LEVEL = LOCAL_QUORUM
LOAD_BALANCING_POLICY = RoundRobinPolicy
PROTOCOL_VERSION = 4
CONNECT_TIMEOUT = 10
REQUEST_TIMEOUT = 30
```

3. **Write AIBasic code**:
```aibasic
10 (cassandra) create cassandra keyspace my_app with replication factor 3
20 (cassandra) create cassandra table users with columns id uuid name text email text
30 (cassandra) insert into cassandra users values id uuid name Alice email alice@example.com
40 (cassandra) select from cassandra users where id equals user_id
50 (cassandra) batch insert 1000 sensor readings into cassandra
```

### Cassandra-Specific Features

#### Keyspace and Table Management
Schema definition:
- Create keyspaces with replication strategies
- Create tables with primary keys and clustering
- Alter tables and add columns
- Drop keyspaces and tables

#### CQL Queries
Cassandra Query Language:
- SELECT with WHERE clauses
- INSERT, UPDATE, DELETE operations
- Prepared statements for performance
- Batch operations for atomicity

#### Consistency Levels
Tunable consistency:
- **ONE**: Single replica (fastest)
- **QUORUM**: Majority of replicas
- **ALL**: All replicas (strongest)
- **LOCAL_QUORUM**: Data center local quorum
- **EACH_QUORUM**: Quorum in each data center

#### Clustering and Distribution
High availability:
- Multiple contact points for failover
- Automatic node discovery
- Load balancing policies
- Token-aware routing

#### Counter Columns
Distributed counters:
- Increment and decrement operations
- Eventually consistent counters
- Useful for metrics and analytics

#### TTL (Time To Live)
Automatic expiration:
- Set TTL on individual columns or rows
- Automatic tombstone creation
- Useful for session data, caching

#### Use Cases
- **Time-Series Data**: IoT sensor data, metrics, logs
- **High-Volume Writes**: Event tracking, user activity
- **Geographic Distribution**: Multi-datacenter deployments
- **Always-On Applications**: High availability requirements
- **Big Data Analytics**: Large-scale data processing

## Email Module

The Email module provides SMTP email sending with attachments, HTML content, templates, and batch processing capabilities.

### Setup

1. **No external dependencies required** - uses Python standard library (smtplib, email)

2. **Configure** `aibasic.conf`:
```ini
[email]
SMTP_HOST = smtp.gmail.com  # Gmail SMTP server
SMTP_PORT = 587  # 587 for TLS, 465 for SSL
USERNAME = your-email@gmail.com
PASSWORD = your-app-password  # For Gmail, use App Password

# Encryption
USE_TLS = true  # STARTTLS encryption (recommended)
USE_SSL = false  # SSL encryption

# Sender Information
FROM_EMAIL = your-email@gmail.com
FROM_NAME = My Application

# Connection Settings
TIMEOUT = 30
```

3. **Write AIBasic code**:
```aibasic
10 (email) send email to customer@example.com subject "Welcome" body "Thank you for signing up"
20 (email) send email with attachment report.pdf to manager@example.com
30 (email) send HTML email with logo to subscribers
40 (email) send batch emails to mailing list with 2 second delay
```

### Email-Specific Features

#### Email Types
Multiple email formats:
- **Plain text emails**: Simple text-based messages
- **HTML emails**: Rich formatting with CSS styling
- **Template emails**: Variable substitution in templates
- **Multipart emails**: HTML with plain text fallback

#### Attachments
File attachment support:
- **Single attachments**: Attach one file
- **Multiple attachments**: Attach multiple files
- **Inline images**: Embed images in HTML emails with CID
- **Any file type**: PDF, Excel, images, etc.

#### Recipients
Flexible recipient handling:
- **To**: Primary recipients
- **CC**: Carbon copy recipients
- **BCC**: Blind carbon copy (hidden recipients)
- **Multiple recipients**: Lists of email addresses

#### Email Features
Advanced capabilities:
- **Email validation**: Validate email address format
- **Priority levels**: Low, normal, high priority
- **Reply-To address**: Specify reply-to different from sender
- **Custom headers**: Add custom email headers
- **Test connection**: Verify SMTP connection before sending

#### Batch Sending
Efficient bulk email:
- **Batch processing**: Send to multiple recipients
- **Delay between emails**: Avoid spam filters
- **Personalization**: Variable substitution per recipient
- **Error handling**: Collect failed recipients for retry

#### Security
Secure email transmission:
- **TLS encryption**: STARTTLS on port 587 (recommended)
- **SSL encryption**: Direct SSL on port 465
- **Authentication**: Username and password
- **App passwords**: Support for Gmail app-specific passwords

#### Use Cases
- **Transactional Emails**: Order confirmations, receipts, password resets
- **Notifications**: Alert emails, system notifications
- **Marketing**: Newsletters, promotional campaigns
- **Reports**: Automated reports with attachments
- **User Onboarding**: Welcome emails, verification emails

## SSH Module

The SSH module provides secure remote server access for command execution and file transfer via SFTP.

### Setup

1. **Install dependencies**:
```bash
pip install paramiko
```

2. **Configure in `aibasic.conf`**:
```ini
[ssh]
HOST = server.example.com
PORT = 22
USERNAME = admin

# Password authentication
PASSWORD = your_password_here

# OR Key-based authentication (recommended)
# KEY_FILE = /path/to/private_key
# KEY_PASSWORD = key_passphrase  # If key is encrypted

# Host key verification
VERIFY_HOST_KEY = false  # true, false, or auto-add

# Connection timeouts
TIMEOUT = 30
BANNER_TIMEOUT = 15
AUTH_TIMEOUT = 10
KEEPALIVE_INTERVAL = 30
```

3. **Write AIBasic code**:
```aibasic
10 (ssh) execute command "uptime" on remote server
20 (ssh) transfer file local.txt to remote server path /home/user/remote.txt
30 (ssh) download file from remote server /var/log/app.log to local.log
40 (ssh) run shell script deploy.sh on remote host
50 (ssh) execute batch commands: "cd /app", "git pull", "npm install"
```

### SSH-Specific Features

#### Authentication Methods
Multiple authentication options:
- **Password authentication**: Simple username/password
- **SSH key authentication**: More secure, recommended for production
- **Encrypted keys**: Supports password-protected private keys
- **Multiple fallback**: Try key first, then password

#### Remote Command Execution
Execute commands on remote servers:
- **Single commands**: Run one-off commands with `execute_command()`
- **Batch commands**: Execute multiple commands sequentially
- **Interactive shells**: Start interactive terminal sessions
- **Output capture**: Retrieve stdout and stderr separately
- **Exit codes**: Check command success/failure
- **Timeout control**: Configure command timeouts

#### SFTP File Transfer
Secure file transfer protocol:
- **Upload files**: `sftp_upload(local_path, remote_path)`
- **Download files**: `sftp_download(remote_path, local_path)`
- **Directory uploads**: Transfer entire directories
- **Directory downloads**: Download remote directories
- **Preserve attributes**: Maintain file permissions and timestamps
- **Progress tracking**: Monitor large file transfers

#### Connection Management
Robust connection handling:
- **Persistent connections**: Reuse connections across operations
- **Auto-reconnect**: Automatic reconnection on connection loss
- **Keep-alive**: Periodic keep-alive packets
- **Connection pooling**: Efficient resource usage
- **Timeout configuration**: Banner, auth, and general timeouts

#### Security Features
Enterprise-grade security:
- **Host key verification**: Strict, auto-add, or ignore modes
- **Known hosts**: Manage known_hosts file
- **Encrypted connections**: All data encrypted via SSH2
- **Jump host support**: Connect via bastion/jump servers
- **Key rotation**: Easy credential updates

#### Advanced Features
Additional capabilities:
- **Port forwarding**: Local and remote port forwarding
- **SSH tunneling**: Create secure tunnels
- **Signal sending**: Send signals (SIGTERM, SIGKILL) to processes
- **Command chaining**: Execute dependent commands
- **Environment variables**: Set remote environment
- **Working directory**: Change remote working directory

#### Use Cases
- **DevOps automation**: Deploy applications, restart services
- **Remote administration**: System maintenance and monitoring
- **Log collection**: Retrieve logs from remote servers
- **Backup automation**: Transfer backup files
- **Multi-server orchestration**: Coordinate across multiple hosts

## Compression Module

The Compression module provides multi-format file compression and decompression with no configuration required.

### Setup

1. **Install dependencies** (optional, for 7Z support):
```bash
pip install py7zr  # Only needed for 7Z format
```

2. **No configuration required** - works standalone

3. **Write AIBasic code**:
```aibasic
10 (compress) compress folder reports/ into reports.zip
20 (compress) extract archive data.tar.gz to output/
30 (compress) compress file logs.txt with gzip compression
40 (compress) create password-protected zip archive.zip with password secret
50 (compress) list contents of archive backup.tar.bz2
```

### Compression-Specific Features

#### Supported Formats
Multiple compression formats:
- **ZIP**: Most common, supports password protection
- **TAR**: Unix archiving
- **TAR.GZ** / **TAR.BZ2** / **TAR.XZ**: Compressed TAR archives
- **GZIP** / **BZIP2** / **XZ**: Single file compression
- **7Z**: High compression ratio (requires py7zr)

#### Auto-Detection
Automatic format detection:
- By file extension (.zip, .tar.gz, .7z, etc.)
- Works for both compression and extraction
- No need to specify format explicitly

#### Compression Options
Fine-grained control:
- **Compression level**: 0-9 (0=store, 9=best compression)
- **Include/exclude patterns**: Filter files by pattern
- **Password protection**: ZIP and 7Z formats
- **Preserve attributes**: Maintain file permissions and timestamps

#### Archive Operations
Utility functions:
- **List contents**: View files in archive
- **Archive info**: Get statistics (file count, compressed/uncompressed size)
- **Compression ratio**: Calculate compression effectiveness

#### Use Cases
- **Backup**: Compress log files and backups
- **Data Transfer**: Compress data before transfer
- **Storage Optimization**: Save disk space
- **File Distribution**: Package files for distribution

## Vault Module

The Vault module provides HashiCorp Vault secrets management with multiple authentication methods.

### Setup

1. **Install dependencies**:
```bash
pip install hvac
```

2. **Configure** `aibasic.conf`:
```ini
[vault]
URL = https://vault.example.com:8200
VERIFY_SSL = true  # Set to false for self-signed certs

# Token Authentication (simplest)
AUTH_METHOD = token
TOKEN = s.xxxxxxxxxxxxxxxxxxxxxxxx

# AppRole Authentication (recommended for production)
# AUTH_METHOD = approle
# ROLE_ID = xxxxx-xxxx-xxxx
# SECRET_ID = xxxxx-xxxx-xxxx

# Vault Settings
MOUNT_POINT = secret
KV_VERSION = 2
```

3. **Write AIBasic code**:
```aibasic
10 (vault) read secret from vault path database/prod
20 (vault) write secret to vault path api/keys with data {"api_key": "xyz"}
30 (vault) encrypt data with vault transit key app-key
40 (vault) get dynamic database credentials from vault role db-read
```

### Vault-Specific Features

#### Authentication Methods
8 authentication options:
- **Token**: Direct token authentication
- **AppRole**: Role-based authentication for apps
- **Kubernetes**: K8s service account authentication
- **AWS**: IAM authentication
- **LDAP**: LDAP directory authentication
- **GitHub**: GitHub organization authentication
- **UserPass**: Username and password
- **TLS Cert**: Client certificate authentication

#### KV Secrets Engine
Key-value secret storage:
- **KV v1**: Simple key-value storage
- **KV v2**: Versioned secrets with history
- **Version management**: Read specific versions
- **Metadata**: Secret metadata and version info
- **Undelete**: Restore deleted secret versions

#### Transit Engine
Encryption as a service:
- **Encrypt**: Encrypt plaintext data
- **Decrypt**: Decrypt ciphertext
- **Rewrap**: Re-encrypt with new key version
- **Key rotation**: Automatic key rotation

#### Dynamic Secrets
On-demand credentials:
- **Database credentials**: Temporary DB credentials
- **AWS credentials**: Temporary AWS access keys
- **Lease management**: Renew or revoke leases

#### Use Cases
- **Credentials Management**: Centralized secrets storage
- **Encryption Services**: Encrypt sensitive data
- **Dynamic Credentials**: Short-lived database credentials
- **Certificate Management**: PKI certificate generation

## Creating Custom Modules

See [src/aibasic/modules/README.md](src/aibasic/modules/README.md) for detailed guide on:
- Module structure and patterns
- Configuration loading
- Thread safety
- Integration with compiler
- Adding new task types

## Benefits of the Module System

1. **Resource Efficiency**: Connection pooling, singleton instances
2. **Code Reuse**: Write once, use in all programs
3. **Configuration Management**: Centralized in `aibasic.conf`
4. **Type Safety**: Modules provide proper Python APIs
5. **Error Handling**: Consistent error handling patterns
6. **Extensibility**: Easy to add new modules for any service

## Future Modules

Potential modules to implement:

- **SSH**: Remote command execution and file transfer
- **S3/MinIO**: Object storage operations
- **Slack/Discord**: Chat integrations and notifications
- **ML Models**: Pre-loaded models for inference
- **Memcached**: Alternative caching solution
- **Neo4j**: Graph database operations
- **Elasticsearch**: Alternative search engine (OpenSearch fork)
- **InfluxDB**: Time-series database
- **LDAP**: Directory service operations

## Troubleshooting

### Module not found
```
ModuleNotFoundError: No module named 'aibasic.modules'
```
**Solution**: Install AIBasic in development mode: `pip install -e .`

### Configuration error
```
KeyError: "Missing [postgres] section in aibasic.conf"
```
**Solution**: Add the required section to your `aibasic.conf` file

### Connection error
```
RuntimeError: Failed to create PostgreSQL connection pool
```
**Solution**: Check PostgreSQL is running and credentials are correct

### Import error
```
ModuleNotFoundError: No module named 'psycopg2'
```
**Solution**: Install the required dependency: `pip install psycopg2-binary`

## Best Practices

1. **Always use parameterized queries** to prevent SQL injection
2. **Configure connection pools** appropriately for your workload
3. **Handle errors** gracefully with try/finally blocks
4. **Close connections** when done (or use `execute_query()`)
5. **Monitor pool usage** with `get_pool_status()` in production
6. **Use transactions** for related operations
7. **Keep credentials secure** - never commit `aibasic.conf` to version control
