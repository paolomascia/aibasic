# ScyllaDB Module - Complete Reference

## Overview

The **ScyllaDB module** provides comprehensive integration with ScyllaDB, a high-performance NoSQL database that is fully compatible with Apache Cassandra but delivers 10x better performance through its C++ implementation. ScyllaDB offers sub-millisecond latencies, automatic tuning, and extreme scalability for modern high-throughput applications.

**Module Type:** `(scylladb)`
**Primary Use Cases:** Time-series data, IoT, real-time analytics, high-throughput applications, session storage, event logging, metrics collection

---

## Table of Contents

1. [Features](#features)
2. [Configuration](#configuration)
3. [Basic Operations](#basic-operations)
4. [Advanced Features](#advanced-features)
5. [Common Use Cases](#common-use-cases)
6. [Best Practices](#best-practices)
7. [Performance Optimization](#performance-optimization)
8. [Troubleshooting](#troubleshooting)

---

## Features

### Core Capabilities

- **10x Performance**: C++ implementation vs Java (Cassandra) for superior speed
- **Cassandra-Compatible**: Same CQL API, drivers, and tools
- **Low Latency**: Sub-millisecond p99 latencies
- **Keyspace Management**: Create, drop, use keyspaces
- **Table Operations**: Create, drop, truncate tables
- **CRUD Operations**: Insert, update, delete, select with CQL
- **Batch Operations**: Logged, unlogged, and counter batches
- **Prepared Statements**: 2-3x performance improvement
- **Consistency Levels**: Tunable consistency (ONE, QUORUM, ALL, LOCAL_QUORUM)
- **Secondary Indexes**: Additional query patterns
- **Materialized Views**: Auto-maintained query optimization
- **Counter Columns**: Distributed counters
- **TTL Support**: Automatic data expiration
- **Time-Series Optimized**: Efficient time-based partitioning

### Supported Operations

| Category | Operations |
|----------|-----------|
| **Keyspace** | Create, drop, use, list keyspaces |
| **Tables** | Create, drop, truncate, list tables |
| **Data Operations** | Insert, update, delete, select with WHERE/LIMIT |
| **Batch** | Logged, unlogged, counter batch operations |
| **Prepared** | Prepare and execute statements |
| **Indexes** | Create and drop secondary indexes |
| **Materialized Views** | Create and drop views |
| **Counters** | Increment distributed counters |
| **Consistency** | ONE, QUORUM, LOCAL_QUORUM, EACH_QUORUM, ALL |

---

## Configuration

### Basic Configuration (aibasic.conf)

```ini
[scylladb]
CONTACT_POINTS = localhost
PORT = 9042
KEYSPACE = aibasic_keyspace
USERNAME =
PASSWORD =
PROTOCOL_VERSION = 4
COMPRESSION = true
CONSISTENCY_LEVEL = LOCAL_QUORUM
REPLICATION_STRATEGY = NetworkTopologyStrategy
REPLICATION_FACTOR = 3
POOL_SIZE = 10
CONNECT_TIMEOUT = 10
REQUEST_TIMEOUT = 10
```

### Configuration Parameters

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `CONTACT_POINTS` | Comma-separated list of ScyllaDB nodes | `localhost` | Yes |
| `PORT` | CQL native transport port | `9042` | No |
| `KEYSPACE` | Default keyspace | `aibasic_keyspace` | No |
| `USERNAME` | Authentication username | - | No |
| `PASSWORD` | Authentication password | - | No |
| `PROTOCOL_VERSION` | CQL protocol version | `4` | No |
| `COMPRESSION` | Enable compression | `true` | No |
| `CONSISTENCY_LEVEL` | Default consistency | `LOCAL_QUORUM` | No |
| `REPLICATION_STRATEGY` | Keyspace replication strategy | `NetworkTopologyStrategy` | No |
| `REPLICATION_FACTOR` | Replication factor | `3` | No |
| `POOL_SIZE` | Connection pool size | `10` | No |
| `CONNECT_TIMEOUT` | Connection timeout (seconds) | `10` | No |
| `REQUEST_TIMEOUT` | Request timeout (seconds) | `10` | No |

### Environment Variables

All configuration parameters can be overridden with environment variables:

```bash
export SCYLLADB_CONTACT_POINTS=scylla1,scylla2,scylla3
export SCYLLADB_PORT=9042
export SCYLLADB_KEYSPACE=my_keyspace
export SCYLLADB_CONSISTENCY_LEVEL=QUORUM
```

---

## Basic Operations

### Keyspace Management

```basic
REM Create keyspace with SimpleStrategy (single datacenter)
10 (scylladb) create keyspace "test_keyspace" with replication_strategy "SimpleStrategy" and replication_factor 1

REM Create keyspace with NetworkTopologyStrategy (multi-datacenter)
20 (scylladb) create keyspace "prod_keyspace" with replication_strategy "NetworkTopologyStrategy" and replication_factor 3

REM Use keyspace
30 (scylladb) use keyspace "test_keyspace"

REM List all keyspaces
40 (scylladb) list keyspaces

REM Drop keyspace
50 (scylladb) drop keyspace "old_keyspace"
```

### Table Operations

```basic
REM Create table with primary key
10 (scylladb) create table "users" with schema "id UUID PRIMARY KEY, name TEXT, email TEXT, age INT"

REM Create table with composite primary key
20 (scylladb) create table "sensor_data" with schema "sensor_id TEXT, timestamp TIMESTAMP, temperature DOUBLE, PRIMARY KEY (sensor_id, timestamp)"

REM Create table with clustering order
30 (scylladb) create table "events" with schema "user_id UUID, event_time TIMESTAMP, event_type TEXT, data TEXT, PRIMARY KEY (user_id, event_time) WITH CLUSTERING ORDER BY (event_time DESC)"

REM List tables
40 (scylladb) list tables

REM Truncate table (remove all data)
50 (scylladb) truncate table "users"

REM Drop table
60 (scylladb) drop table "old_table"
```

### Insert Data

```basic
REM Insert single record
10 (scylladb) insert into "users" data {"id": "uuid()", "name": "John Doe", "email": "john@example.com", "age": 30}

REM Insert with TTL (time to live - auto-expires after 24 hours)
20 (scylladb) insert into "sessions" data {"session_id": "uuid()", "user_id": "uuid()", "data": "..."} with ttl 86400

REM Insert with consistency level
30 (scylladb) insert into "users" data {"id": "uuid()", "name": "Jane"} with consistency "QUORUM"
```

### Query Data

```basic
REM Select all records
10 (scylladb) select * from "users"

REM Select specific columns
20 (scylladb) select "name, email" from "users"

REM Select with WHERE clause
30 LET user_id = "123e4567-e89b-12d3-a456-426614174000"
40 (scylladb) select * from "users" where {"id": user_id}

REM Select with LIMIT
50 (scylladb) select * from "users" limit 10

REM Select with consistency level
60 (scylladb) select * from "users" with consistency "ONE"
```

### Update and Delete

```basic
REM Update data
10 LET user_id = "123e4567-e89b-12d3-a456-426614174000"
20 (scylladb) update "users" set {"name": "John Updated", "age": 31} where {"id": user_id}

REM Update with TTL
30 (scylladb) update "users" set {"email": "new@example.com"} where {"id": user_id} with ttl 3600

REM Delete record
40 (scylladb) delete from "users" where {"id": user_id}
```

---

## Advanced Features

### Batch Operations

```basic
REM Create batch of inserts (LOGGED for atomicity)
10 LET users = [
20   {"id": "uuid()", "name": "Alice", "email": "alice@example.com", "age": 28},
30   {"id": "uuid()", "name": "Bob", "email": "bob@example.com", "age": 35},
40   {"id": "uuid()", "name": "Carol", "email": "carol@example.com", "age": 42}
50 ]

60 (scylladb) batch insert into "users" data users with batch_type "LOGGED"

REM UNLOGGED batch for maximum performance (no atomicity)
70 (scylladb) batch insert into "users" data users with batch_type "UNLOGGED"

REM COUNTER batch for counter updates
80 (scylladb) batch insert into "counters" data counter_updates with batch_type "COUNTER"
```

### Prepared Statements

```basic
REM Prepare statement for reuse
10 LET stmt_id = (scylladb) prepare "INSERT INTO users (id, name, email, age) VALUES (?, ?, ?, ?)"

REM Execute prepared statement multiple times
20 FOR i = 1 TO 1000
30   LET values = ["uuid()", "User " + STR(i), "user" + STR(i) + "@example.com", 20 + i]
40   (scylladb) execute prepared stmt_id with values values
50 NEXT i
```

### Consistency Levels

```basic
REM ONE: Fastest, least consistent (1 replica)
10 (scylladb) insert into "logs" data log_data with consistency "ONE"

REM QUORUM: Balanced (majority of replicas)
20 (scylladb) select * from "users" with consistency "QUORUM"

REM LOCAL_QUORUM: Datacenter-local majority (recommended for multi-DC)
30 (scylladb) insert into "data" data values with consistency "LOCAL_QUORUM"

REM ALL: Slowest, most consistent (all replicas)
40 (scylladb) select * from "critical_data" with consistency "ALL"
```

### Secondary Indexes

```basic
REM Create index on column
10 (scylladb) create index "users_email_idx" on "users" column "email"

REM Now can query by indexed column
20 (scylladb) execute "SELECT * FROM users WHERE email = 'john@example.com'"

REM Drop index
30 (scylladb) drop index "users_email_idx"
```

### Materialized Views

```basic
REM Create materialized view for alternative query pattern
10 (scylladb) create materialized view "users_by_email" from table "users" select "id, name, email, age" where "email IS NOT NULL AND id IS NOT NULL" with primary_key "(email, id)"

REM Query using materialized view
20 (scylladb) execute "SELECT * FROM users_by_email WHERE email = 'john@example.com'"

REM Drop materialized view
30 (scylladb) drop materialized view "users_by_email"
```

### Counter Columns

```basic
REM Create counter table
10 (scylladb) create table "page_views" with schema "page_url TEXT PRIMARY KEY, view_count COUNTER"

REM Increment counter
20 (scylladb) increment counter in "page_views" column "view_count" by 1 where {"page_url": "/home"}

REM Increment by specific amount
30 (scylladb) increment counter in "page_views" column "view_count" by 100 where {"page_url": "/products"}

REM Query counter values
40 (scylladb) select * from "page_views"
```

---

## Common Use Cases

### 1. Time-Series IoT Data

```basic
REM Create time-series table with time-based partitioning
10 (scylladb) create keyspace "iot_data" with replication_strategy "SimpleStrategy" and replication_factor 1

20 (scylladb) use keyspace "iot_data"

30 (scylladb) create table "sensor_readings" with schema "sensor_id TEXT, reading_date DATE, reading_time TIMESTAMP, temperature DOUBLE, humidity DOUBLE, PRIMARY KEY ((sensor_id, reading_date), reading_time) WITH CLUSTERING ORDER BY (reading_time DESC)"

40 REM Insert sensor readings
50 FOR i = 1 TO 10000
60   LET reading = {
70     "sensor_id": "SENSOR_001",
80     "reading_date": "2025-01-15",
90     "reading_time": "now()",
100    "temperature": 20 + (i MOD 10),
110    "humidity": 50 + (i MOD 20)
120  }
130  (scylladb) insert into "sensor_readings" data reading with consistency "ONE"
140 NEXT i

150 REM Query readings for specific sensor and date
160 (scylladb) select * from "sensor_readings" where {"sensor_id": "SENSOR_001", "reading_date": "2025-01-15"} limit 100
```

### 2. E-commerce Product Catalog

```basic
REM Multi-table design for different access patterns
10 (scylladb) create keyspace "ecommerce" with replication_strategy "NetworkTopologyStrategy" and replication_factor 3

20 (scylladb) use keyspace "ecommerce"

30 REM Products by ID
40 (scylladb) create table "products" with schema "product_id UUID PRIMARY KEY, name TEXT, description TEXT, price DECIMAL, category TEXT, stock INT"

50 REM Products by category
60 (scylladb) create table "products_by_category" with schema "category TEXT, product_id UUID, name TEXT, price DECIMAL, PRIMARY KEY (category, product_id)"

70 REM Insert product into both tables
80 LET product = {"product_id": "uuid()", "name": "Laptop", "description": "...", "price": 999.99, "category": "Electronics", "stock": 50}

90 (scylladb) insert into "products" data product

100 LET category_data = {"category": product["category"], "product_id": product["product_id"], "name": product["name"], "price": product["price"]}
110 (scylladb) insert into "products_by_category" data category_data

120 REM Query by category
130 (scylladb) select * from "products_by_category" where {"category": "Electronics"}
```

### 3. Session Storage

```basic
REM User sessions with automatic expiration
10 (scylladb) create keyspace "sessions" with replication_strategy "SimpleStrategy" and replication_factor 1

20 (scylladb) use keyspace "sessions"

30 (scylladb) create table "user_sessions" with schema "session_id UUID PRIMARY KEY, user_id UUID, ip_address TEXT, created_at TIMESTAMP"

40 REM Create session with 1-hour TTL
50 LET session = {
60   "session_id": "uuid()",
70   "user_id": "uuid()",
80   "ip_address": "192.168.1.100",
90   "created_at": "now()"
100 }

110 (scylladb) insert into "user_sessions" data session with ttl 3600 and consistency "QUORUM"
```

### 4. Real-Time Analytics

```basic
REM Event tracking and analytics
10 (scylladb) create keyspace "analytics" with replication_strategy "NetworkTopologyStrategy" and replication_factor 3

20 (scylladb) use keyspace "analytics"

30 REM Event log partitioned by date
40 (scylladb) create table "events" with schema "event_date DATE, event_id UUID, user_id UUID, event_type TEXT, properties TEXT, timestamp TIMESTAMP, PRIMARY KEY (event_date, timestamp, event_id) WITH CLUSTERING ORDER BY (timestamp DESC)"

50 REM Event counters
60 (scylladb) create table "event_counts" with schema "event_type TEXT, date DATE, count COUNTER, PRIMARY KEY (event_type, date)"

70 REM Log event
80 LET event = {
90   "event_date": "2025-01-15",
100  "event_id": "uuid()",
110  "user_id": "uuid()",
120  "event_type": "page_view",
130  "properties": '{"page": "/home"}',
140  "timestamp": "now()"
150 }

160 (scylladb) insert into "events" data event with consistency "ONE"

170 REM Increment counter
180 (scylladb) increment counter in "event_counts" column "count" by 1 where {"event_type": "page_view", "date": "2025-01-15"}
```

### 5. Social Media Feed

```basic
REM User activity feed with reverse chronological order
10 (scylladb) create keyspace "social" with replication_strategy "SimpleStrategy" and replication_factor 1

20 (scylladb) use keyspace "social"

30 (scylladb) create table "user_feed" with schema "user_id UUID, activity_time TIMESTAMP, activity_id UUID, activity_type TEXT, content TEXT, PRIMARY KEY (user_id, activity_time, activity_id) WITH CLUSTERING ORDER BY (activity_time DESC)"

40 REM Insert activities
50 LET user_id = "uuid()"

60 FOR i = 1 TO 100
70   LET activity = {
80     "user_id": user_id,
90     "activity_time": "now()",
100    "activity_id": "uuid()",
110    "activity_type": "post",
120    "content": "Post content " + STR(i)
130  }
140  (scylladb) insert into "user_feed" data activity
150 NEXT i

160 REM Get latest 20 activities (automatically ordered DESC)
170 (scylladb) select * from "user_feed" where {"user_id": user_id} limit 20
```

---

## Best Practices

### Data Modeling

1. **Primary Key Design**: Critical for performance
   - Partition key determines data distribution
   - Clustering key determines sort order within partition
   - Choose partition key for even distribution

2. **Avoid Large Partitions**: Keep partitions < 100MB
   - Use time-based partitioning for time-series data
   - Use composite partition keys for better distribution

3. **Denormalization**: Optimize for query patterns
   - Create separate tables for different access patterns
   - Duplicate data when necessary for performance

4. **No JOINs**: Design tables to avoid JOINs
   - Each table should answer one query pattern
   - Use materialized views for alternative queries

### Performance

1. **Use Prepared Statements**: 2-3x faster than regular statements
2. **Batch Wisely**:
   - Use UNLOGGED batches for maximum performance
   - Keep batches small (< 100 statements)
   - Only batch same partition key for best performance

3. **Consistency Levels**:
   - Use ONE for high-throughput writes
   - Use LOCAL_QUORUM for balanced consistency
   - Use QUORUM or ALL only when necessary

4. **TTL for Temporary Data**: Automatic cleanup
5. **Compression**: Enable for network efficiency

### Replication

1. **SimpleStrategy**: Single datacenter only
2. **NetworkTopologyStrategy**: Multi-datacenter deployments
3. **Replication Factor**: Typically 3 for production
4. **LOCAL_QUORUM**: For multi-DC deployments

---

## Performance Optimization

### Connection Pooling

```ini
POOL_SIZE = 10  # Connections per host
```

### Compression

```ini
COMPRESSION = true  # Enable LZ4 compression
```

### Prepared Statements

Always use prepared statements for repeated queries:

```basic
10 LET stmt = (scylladb) prepare "INSERT INTO users (id, name) VALUES (?, ?)"
20 FOR i = 1 TO 10000
30   (scylladb) execute prepared stmt with values ["uuid()", "User " + STR(i)]
40 NEXT i
```

### Batch Size

Keep batches small (< 100 statements) for best performance.

---

## Troubleshooting

### Common Issues

**Connection Timeout**

```
Issue: "Failed to connect to ScyllaDB"
Solution:
- Verify CONTACT_POINTS are correct and reachable
- Check PORT (default: 9042)
- Verify firewall allows connections
- Increase CONNECT_TIMEOUT if network is slow
```

**Keyspace Not Found**

```
Issue: "Keyspace does not exist"
Solution:
- Create keyspace first: (scylladb) create keyspace "..."
- Verify keyspace name is correct
- Use: (scylladb) list keyspaces
```

**Invalid Query**

```
Issue: "Invalid CQL syntax"
Solution:
- Verify table schema matches query
- Check WHERE clause uses partition key
- Use (scylladb) execute "..." for raw CQL
```

**Write Timeout**

```
Issue: "Write timed out"
Solution:
- Reduce batch size
- Use lower consistency level (ONE instead of QUORUM)
- Increase REQUEST_TIMEOUT
- Check cluster health
```

**Large Partition Warning**

```
Issue: "Partition too large"
Solution:
- Redesign partition key for better distribution
- Use time-based partitioning
- Split large partitions
```

---

## API Reference

### Keyspace Methods

- `create_keyspace(keyspace, replication_strategy, replication_factor, durable_writes)` - Create keyspace
- `drop_keyspace(keyspace)` - Drop keyspace
- `use_keyspace(keyspace)` - Set current keyspace
- `list_keyspaces()` - List all keyspaces

### Table Methods

- `create_table(table, schema, if_not_exists)` - Create table
- `drop_table(table, if_exists)` - Drop table
- `truncate_table(table)` - Remove all data
- `list_tables(keyspace)` - List tables in keyspace

### Data Methods

- `insert(table, data, consistency, ttl)` - Insert data
- `update(table, set_values, where, consistency, ttl)` - Update data
- `delete(table, where, consistency)` - Delete data
- `select(table, columns, where, limit, consistency)` - Query data

### Batch Methods

- `batch_insert(table, data_list, batch_type, consistency)` - Batch insert

### Prepared Statement Methods

- `prepare(cql)` - Prepare statement
- `execute_prepared(stmt_id, values, consistency)` - Execute prepared

### Index and View Methods

- `create_index(index_name, table, column, if_not_exists)` - Create index
- `drop_index(index_name, if_exists)` - Drop index
- `create_materialized_view(view_name, table, select_columns, where_clause, primary_key, if_not_exists)` - Create materialized view
- `drop_materialized_view(view_name, if_exists)` - Drop materialized view

### Counter Methods

- `increment_counter(table, counter_column, increment, where, consistency)` - Increment counter

### Utility Methods

- `execute(cql, consistency)` - Execute raw CQL
- `close()` - Close connection
- `get_cluster_metadata()` - Get cluster info

---

## ScyllaDB vs Cassandra

| Feature | ScyllaDB | Cassandra |
|---------|----------|-----------|
| **Implementation** | C++ | Java |
| **Performance** | 10x faster | Baseline |
| **Latency** | Sub-millisecond p99 | Higher |
| **CPU Efficiency** | Uses all cores efficiently | Limited by JVM |
| **Memory Management** | Better (no GC pauses) | JVM GC pauses |
| **Compatibility** | 100% Cassandra-compatible | - |
| **Tuning** | Automatic (shard-per-core) | Manual tuning required |

---

## Module Information

- **Module Name**: ScyllaDBModule
- **Task Type**: `(scylladb)`
- **Dependencies**: `scylla-driver>=3.28.0`
- **Python Version**: 3.7+
- **AIbasic Version**: 1.0+

---

*For more examples, see [example_scylladb.aib](../../examples/example_scylladb.aib)*
