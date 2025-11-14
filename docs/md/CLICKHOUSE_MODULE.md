# ClickHouse Module Documentation

## Overview

The ClickHouse module enables AIbasic programs to interact with ClickHouse, a high-performance column-oriented database management system for online analytical processing (OLAP). ClickHouse is designed for real-time analytics on large datasets with exceptional query performance.

## Features

✅ **Connection Management** - HTTP interface with connection pooling
✅ **Query Execution** - SELECT, INSERT, CREATE, DROP, and all SQL operations
✅ **Batch Inserts** - High-performance bulk data loading
✅ **DataFrame Integration** - Query results to pandas DataFrame, DataFrame to ClickHouse
✅ **Multiple Output Formats** - JSON, CSV, TabSeparated, and more
✅ **Compression Support** - LZ4 and ZSTD compression for network efficiency
✅ **Table Management** - Create, drop, optimize, truncate tables
✅ **Database Management** - Create and drop databases
✅ **Partitioning** - Time-based and custom partitioning support
✅ **Materialized Views** - Pre-aggregated data for faster queries
✅ **Statistics** - Table stats, row counts, sizes
✅ **Distributed Queries** - Support for distributed tables
✅ **Automatic Retries** - Built-in connection pooling and retry logic
✅ **Thread Safety** - Singleton pattern for efficient resource usage

## Configuration

### Basic Configuration

```ini
[clickhouse]
HOST = localhost
PORT = 8123
DATABASE = default
USERNAME = default
PASSWORD = your_password
```

### Advanced Configuration

```ini
[clickhouse]
# Connection
HOST = clickhouse.example.com
PORT = 8123
DATABASE = analytics

# Authentication
USERNAME = admin
PASSWORD = secure_password

# SSL/TLS
USE_SSL = true
VERIFY_SSL = true

# Performance
TIMEOUT = 30
COMPRESSION = lz4  # or zstd
```

### Docker/Cloud Configuration

```ini
[clickhouse]
# ClickHouse Cloud
HOST = your-cluster.clickhouse.cloud
PORT = 8443
USE_SSL = true
USERNAME = default
PASSWORD = your_cloud_password
DATABASE = default
```

## Task Type

Use the `(clickhouse)` task type hint in your AIbasic programs:

```aibasic
10 (clickhouse) query "SELECT * FROM events"
20 (clickhouse) insert into users values
30 (clickhouse) create table analytics
```

## Usage Examples

### 1. Basic Connection and Query

```aibasic
10 (clickhouse) ping server
20 (clickhouse) get version
30 print "Connected to ClickHouse" and version

40 (clickhouse) query "SELECT database, name FROM system.tables LIMIT 10"
50 print "Tables:" and query_result
```

### 2. Create Database and Table

```aibasic
10 (clickhouse) create database if not exists analytics
20 (clickhouse) use database analytics

30 (clickhouse) create table if not exists events with columns:
40 (clickhouse) column "event_date" type "Date"
50 (clickhouse) column "user_id" type "UInt32"
60 (clickhouse) column "event_type" type "String"
70 (clickhouse) column "value" type "Float64"
80 (clickhouse) engine "MergeTree()"
90 (clickhouse) partition by "toYYYYMM(event_date)"
100 (clickhouse) order by "event_date, user_id"

110 print "Table created successfully"
```

**Table Engines:**
- `MergeTree()` - General purpose (requires ORDER BY)
- `ReplacingMergeTree()` - Removes duplicates
- `SummingMergeTree()` - Pre-aggregates numeric columns
- `AggregatingMergeTree()` - Stores intermediate aggregation states
- `CollapsingMergeTree()` - Handles row updates/deletes
- `Log` - Simple log storage
- `Memory` - In-memory tables
- `Distributed` - Distributed tables across shards

### 3. Insert Data

```aibasic
# Single insert
10 (clickhouse) insert into events values:
20 (clickhouse) row event_date="2025-01-14", user_id=1001, event_type="click", value=1.5
30 (clickhouse) row event_date="2025-01-14", user_id=1002, event_type="view", value=0.0

# Batch insert from DataFrame
40 (csv) read file "events.csv" into events_data
50 (clickhouse) batch insert into events from dataframe events_data with batch_size 10000
60 print "Inserted" and rows_inserted and "rows"
```

### 4. Query and Analyze Data

```aibasic
# Simple query
10 (clickhouse) query "SELECT event_type, count() as cnt FROM events GROUP BY event_type"
20 print "Event counts:" and query_result

# Query to DataFrame for further analysis
30 (clickhouse) query to dataframe "SELECT * FROM events WHERE event_date >= today() - 7"
40 (df) show info about dataframe
50 (df) calculate mean of value
60 print "Average value:" and mean_value

# Aggregation query
70 (clickhouse) query """
    SELECT
        toStartOfDay(event_date) as day,
        event_type,
        count() as events,
        avg(value) as avg_value,
        quantile(0.95)(value) as p95_value
    FROM events
    WHERE event_date >= today() - 30
    GROUP BY day, event_type
    ORDER BY day DESC, events DESC
"""
80 print "Daily statistics:" and query_result
```

### 5. Time-Series Analytics

```aibasic
10 (clickhouse) create table if not exists metrics with columns:
20 (clickhouse) column "timestamp" type "DateTime"
30 (clickhouse) column "metric_name" type "String"
40 (clickhouse) column "value" type "Float64"
50 (clickhouse) column "tags" type "Map(String, String)"
60 (clickhouse) engine "MergeTree()"
70 (clickhouse) partition by "toYYYYMMDD(timestamp)"
80 (clickhouse) order by "metric_name, timestamp"

# Query time-series data
90 (clickhouse) query """
    SELECT
        toStartOfHour(timestamp) as hour,
        metric_name,
        avg(value) as avg_value,
        max(value) as max_value,
        min(value) as min_value
    FROM metrics
    WHERE timestamp >= now() - INTERVAL 24 HOUR
    GROUP BY hour, metric_name
    ORDER BY hour
"""
100 print "Hourly metrics:" and query_result
```

### 6. Materialized Views

```aibasic
# Create materialized view for pre-aggregated data
10 (clickhouse) execute query """
    CREATE MATERIALIZED VIEW IF NOT EXISTS daily_events_mv
    ENGINE = SummingMergeTree()
    PARTITION BY toYYYYMM(event_date)
    ORDER BY (event_date, event_type)
    AS SELECT
        event_date,
        event_type,
        count() as event_count,
        sum(value) as total_value
    FROM events
    GROUP BY event_date, event_type
"""

20 print "Materialized view created"

# Query materialized view (much faster than base table)
30 (clickhouse) query "SELECT * FROM daily_events_mv WHERE event_date >= today() - 7"
40 print "Daily aggregates:" and query_result
```

### 7. Table Management

```aibasic
# Get table statistics
10 (clickhouse) get stats for table events
20 print "Table statistics:"
30 print "  Rows:" and row_count
40 print "  Size:" and total_size
50 print "  Partitions:" and partitions

# Describe table schema
60 (clickhouse) describe table events
70 print "Table schema:" and table_schema

# Optimize table (merge parts)
80 (clickhouse) optimize table events final
90 print "Table optimized"

# Show all tables
100 (clickhouse) show tables
110 print "Tables:" and tables_list
```

### 8. Error Handling

```aibasic
10 on error goto 900

20 (clickhouse) query "SELECT * FROM non_existent_table"
30 print "This won't execute"
40 goto 999

900 print "ERROR:" and _last_error
910 print "At line:" and _last_error_line
920 (slack) send alert with message "ClickHouse query failed"
930 (slack) add field "Error" with value _last_error

999 print "Complete"
```

### 9. Real-Time Analytics Pipeline

```aibasic
10 on error goto 900

# Extract from PostgreSQL
20 (postgres) query "SELECT * FROM transactions WHERE created_at >= now() - INTERVAL '1 hour'"
30 set transactions to query_result

# Transform with DataFrame
40 (df) create dataframe from transactions
50 (df) add column "hour" with value "extract hour from timestamp"
60 (df) add column "amount_usd" with value "amount * exchange_rate"

# Load into ClickHouse
70 (clickhouse) batch insert into transactions_fact from dataframe result with batch_size 5000
80 print "Loaded" and rows_inserted and "transactions"

# Run analytics query
90 (clickhouse) query """
    SELECT
        hour,
        count() as transaction_count,
        sum(amount_usd) as total_amount,
        avg(amount_usd) as avg_amount
    FROM transactions_fact
    WHERE event_date = today()
    GROUP BY hour
    ORDER BY hour
"""
100 print "Hourly stats:" and query_result

# Send to Slack
110 (slack) send status message
120 (slack) set title to "Hourly Transaction Report"
130 (slack) add field "Transactions" with value transaction_count
140 (slack) add field "Total Amount" with value total_amount

150 goto 999

900 print "Pipeline error:" and _last_error
910 (slack) send alert with severity "error"
920 (slack) add field "Error" with value _last_error

999 print "Pipeline complete"
```

### 10. Web Analytics Use Case

```aibasic
10 (clickhouse) create table if not exists page_views with columns:
20 (clickhouse) column "timestamp" type "DateTime"
30 (clickhouse) column "user_id" type "UInt64"
40 (clickhouse) column "session_id" type "String"
50 (clickhouse) column "page_url" type "String"
60 (clickhouse) column "referrer" type "String"
70 (clickhouse) column "country" type "String"
80 (clickhouse) column "device_type" type "Enum8('desktop'=1, 'mobile'=2, 'tablet'=3)"
90 (clickhouse) column "duration_sec" type "UInt32"
100 (clickhouse) engine "MergeTree()"
110 (clickhouse) partition by "toYYYYMMDD(timestamp)"
120 (clickhouse) order by "timestamp, user_id"

# Analytics queries
130 (clickhouse) query """
    SELECT
        country,
        device_type,
        count() as pageviews,
        count(DISTINCT user_id) as unique_users,
        count(DISTINCT session_id) as sessions,
        avg(duration_sec) as avg_duration
    FROM page_views
    WHERE timestamp >= now() - INTERVAL 24 HOUR
    GROUP BY country, device_type
    ORDER BY pageviews DESC
    LIMIT 20
"""
140 print "Top countries and devices:" and query_result
```

## Python API

For advanced use cases, use the ClickHouse module directly in Python:

```python
from aibasic.modules import ClickHouseModule

# Initialize
ch = ClickHouseModule(
    host="localhost",
    port=8123,
    database="analytics",
    username="default",
    password="",
    compression="lz4"
)

# Check connection
if ch.ping():
    print(f"Connected to ClickHouse {ch.get_version()}")

# Execute query
result = ch.query("SELECT * FROM events LIMIT 10")
for row in result:
    print(row)

# Query to DataFrame
df = ch.query_df("SELECT event_date, count() as cnt FROM events GROUP BY event_date")
print(df.head())

# Insert data
data = [
    {'event_date': '2025-01-14', 'user_id': 1001, 'event_type': 'click'},
    {'event_date': '2025-01-14', 'user_id': 1002, 'event_type': 'view'}
]
result = ch.insert('events', data)
print(f"Inserted {result['rows_inserted']} rows")

# Batch insert from DataFrame
import pandas as pd
df = pd.read_csv('events.csv')
result = ch.batch_insert('events', df, batch_size=10000)
print(f"Batch inserted {result['rows_inserted']} rows")

# Create table
columns = {
    'event_date': 'Date',
    'user_id': 'UInt32',
    'event_type': 'String',
    'value': 'Float64'
}
ch.create_table(
    'events',
    columns,
    engine='MergeTree()',
    order_by=['event_date', 'user_id'],
    partition_by='toYYYYMM(event_date)'
)

# Get table stats
stats = ch.get_stats('events')
print(f"Rows: {stats['row_count']}, Size: {stats['total_size']}")

# Execute DDL
ch.execute("CREATE DATABASE IF NOT EXISTS analytics")

# Close connection
ch.close()
```

## Data Types

### Numeric Types
- **Integers**: `UInt8`, `UInt16`, `UInt32`, `UInt64`, `Int8`, `Int16`, `Int32`, `Int64`
- **Floats**: `Float32`, `Float64`
- **Decimals**: `Decimal(P, S)` - e.g., `Decimal(18, 2)`

### String Types
- `String` - Variable length string
- `FixedString(N)` - Fixed length (N bytes)

### Date/Time Types
- `Date` - Date (YYYY-MM-DD)
- `DateTime` - Date with time (second precision)
- `DateTime64(3)` - Date with millisecond precision

### Complex Types
- `Array(T)` - Array of type T
- `Tuple(T1, T2, ...)` - Tuple with named fields
- `Map(K, V)` - Key-value map
- `Enum8('val1'=1, 'val2'=2)` - Enumeration
- `Nullable(T)` - Allows NULL values

### Special Types
- `UUID` - Universally unique identifier
- `IPv4`, `IPv6` - IP addresses
- `LowCardinality(T)` - For columns with few unique values (optimization)

## Best Practices

### 1. Choose the Right Table Engine
```aibasic
# For most use cases - MergeTree
10 (clickhouse) engine "MergeTree()"

# For deduplication - ReplacingMergeTree
20 (clickhouse) engine "ReplacingMergeTree(version_column)"

# For pre-aggregation - SummingMergeTree
30 (clickhouse) engine "SummingMergeTree()"
```

### 2. Use Partitioning for Time-Series Data
```aibasic
# Monthly partitioning
10 (clickhouse) partition by "toYYYYMM(event_date)"

# Daily partitioning (for high-volume tables)
20 (clickhouse) partition by "toYYYYMMDD(event_date)"

# Custom partitioning
30 (clickhouse) partition by "country"
```

### 3. Optimize ORDER BY for Query Patterns
```aibasic
# Order by most commonly filtered columns
10 (clickhouse) order by "event_date, user_id, event_type"

# Consider cardinality (low to high)
20 (clickhouse) order by "country, city, user_id"
```

### 4. Use Compression
```ini
[clickhouse]
COMPRESSION = lz4  # 2-3x compression, fast
# or
COMPRESSION = zstd  # 3-5x compression, slower but better ratio
```

### 5. Batch Inserts for Performance
```aibasic
# Always use batch inserts for large datasets
10 (clickhouse) batch insert into events from dataframe data with batch_size 10000
```

### 6. Use Materialized Views
```aibasic
# Pre-aggregate frequently queried data
10 (clickhouse) create materialized view daily_stats as
20 (clickhouse) select date, metric, sum(value) from raw_data group by date, metric
```

### 7. Monitor Table Statistics
```aibasic
10 (clickhouse) get stats for table events
20 if partitions > 1000 jump to line 100  # Too many partitions!
```

### 8. Regular Optimization
```aibasic
# Merge table parts periodically
10 (clickhouse) optimize table events final
```

## Performance Tips

### Query Optimization
- Use `PREWHERE` for filtering (faster than `WHERE`)
- Limit result sets with `LIMIT`
- Use `SAMPLE` for approximate queries on large datasets
- Avoid `SELECT *` - specify columns
- Use appropriate data types (smaller = faster)

### Index Optimization
- Primary key (ORDER BY) is automatically indexed
- Add secondary indices for specific queries
- Use `GRANULARITY` to tune index density

### Partitioning Strategy
- Don't over-partition (< 1000 partitions recommended)
- Partition by time for time-series data
- Drop old partitions instead of DELETE

### Compression
- Use `LowCardinality` for low-cardinality string columns
- Enable LZ4/ZSTD compression
- Use appropriate numeric types (UInt32 vs UInt64)

## Troubleshooting

### Connection Issues
```aibasic
10 (clickhouse) ping server
20 if not ping_success jump to line 100

100 print "Cannot connect to ClickHouse"
110 print "Check host, port, and credentials"
```

### Query Errors
- **Syntax Error**: Check SQL syntax, use ClickHouse dialect
- **Table Not Found**: Verify database and table names
- **Type Mismatch**: Check column types match INSERT data
- **Memory Limit**: Increase `max_memory_usage` setting

### Performance Issues
- **Slow Queries**: Check `EXPLAIN` output, add indexes
- **Too Many Parts**: Run `OPTIMIZE TABLE`
- **High Memory**: Reduce `max_block_size`, use LIMIT
- **Slow Inserts**: Use batch inserts, increase batch size

## Security Considerations

### Authentication
```ini
[clickhouse]
USERNAME = app_user
PASSWORD = strong_password_here
```

### Network Security
```ini
USE_SSL = true
VERIFY_SSL = true
```

### Best Practices
- ⚠️ Never commit credentials to source control
- ✅ Use strong passwords
- ✅ Enable SSL/TLS in production
- ✅ Use least-privilege user accounts
- ✅ Regularly rotate credentials
- ✅ Use firewall rules to restrict access

## Integration with Other Modules

### ClickHouse + PostgreSQL (ETL)
```aibasic
10 (postgres) query "SELECT * FROM orders WHERE created_at >= now() - INTERVAL '1 hour'"
20 (clickhouse) batch insert into orders_fact from dataframe postgres_result
```

### ClickHouse + S3 (Data Lake)
```aibasic
10 (clickhouse) query to dataframe "SELECT * FROM events WHERE event_date = today()"
20 (df) save dataframe to csv "daily_events.csv"
30 (s3) upload file "daily_events.csv" to bucket "data-lake"
```

### ClickHouse + Slack (Monitoring)
```aibasic
10 (clickhouse) query "SELECT count() as errors FROM logs WHERE level = 'ERROR' AND timestamp >= now() - INTERVAL 5 MINUTE"
20 if errors > 100 jump to line 100
30 goto 999

100 (slack) send alert with message "High error rate detected"
110 (slack) add field "Error Count" with value errors

999 print "Done"
```

## Resources

- [ClickHouse Official Documentation](https://clickhouse.com/docs)
- [ClickHouse SQL Reference](https://clickhouse.com/docs/en/sql-reference/)
- [Table Engines Guide](https://clickhouse.com/docs/en/engines/table-engines/)
- [Query Optimization](https://clickhouse.com/docs/en/guides/improving-query-performance/)
- [Data Types](https://clickhouse.com/docs/en/sql-reference/data-types/)

---

**AIbasic v1.0** - ClickHouse Module Documentation
