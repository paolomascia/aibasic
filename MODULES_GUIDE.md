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

- **MongoDB**: NoSQL database operations
- **S3/MinIO**: Object storage
- **SMTP**: Email sending
- **Slack/Discord**: Chat integrations
- **ML Models**: Pre-loaded models for inference
- **Memcached**: Alternative caching solution
- **Cassandra**: Distributed NoSQL database
- **Neo4j**: Graph database operations

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
