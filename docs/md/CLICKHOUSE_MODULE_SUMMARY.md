# ClickHouse Module Implementation Summary

## Overview

Successfully implemented a complete ClickHouse integration module for AIbasic v1.0, enabling programs to interact with ClickHouse, a high-performance column-oriented database for real-time analytics and OLAP workloads.

## Files Created/Modified

### 1. Module Implementation
**File:** `src/aibasic/modules/clickhouse_module.py` (750+ lines)

**Features Implemented:**
- ✅ **Connection Management**
  - HTTP interface (port 8123)
  - Session-based connection pooling
  - SSL/TLS support
  - Authentication (username/password)

- ✅ **Query Operations**
  - Execute any SQL query (SELECT, INSERT, CREATE, DROP, etc.)
  - Parameter substitution
  - Multiple output formats (JSONEachRow, JSON, CSV, TabSeparated, etc.)
  - Custom ClickHouse settings per query

- ✅ **Data Loading**
  - Single row insert
  - Batch insert for high performance
  - Insert from list of dictionaries
  - Insert from pandas DataFrame
  - Configurable batch sizes

- ✅ **DataFrame Integration**
  - Query results to pandas DataFrame (`query_df()`)
  - Insert from DataFrame (`batch_insert()`)
  - Seamless integration for data analysis

- ✅ **Table Management**
  - Create tables with various engines (MergeTree, ReplacingMergeTree, etc.)
  - Drop tables
  - Truncate tables
  - Optimize tables (merge parts)
  - Describe table schema
  - Show tables and databases

- ✅ **Database Management**
  - Create databases
  - Drop databases
  - Switch current database
  - Show databases list

- ✅ **Advanced Features**
  - Partitioning support (time-based and custom)
  - ORDER BY configuration (primary key)
  - Compression (LZ4, ZSTD)
  - Materialized views support
  - Table statistics (row count, size, partitions)
  - Server ping and version check

- ✅ **Technical Features**
  - Singleton pattern for resource efficiency
  - Thread-safe operations
  - Comprehensive error handling
  - Request timeouts
  - Connection pooling via requests Session

**Key Classes and Methods:**
```python
class ClickHouseModule:
    # Connection
    def __init__(host, port, database, username, password, use_ssl, compression)
    def ping() -> bool
    def get_version() -> str

    # Query Operations
    def execute(query, params, database, output_format, settings)
    def query(sql, params, database) -> List[Dict]
    def query_df(sql, params, database) -> pd.DataFrame

    # Data Loading
    def insert(table, data, database, columns)
    def batch_insert(table, data, database, batch_size)

    # Table Management
    def create_table(table, columns, engine, order_by, partition_by, database)
    def drop_table(table, database, if_exists)
    def truncate_table(table, database)
    def optimize_table(table, database, partition, final)
    def describe_table(table, database)
    def show_tables(database) -> List[str]

    # Database Management
    def create_database(database, if_not_exists, engine)
    def drop_database(database, if_exists)
    def use_database(database)
    def show_databases() -> List[str]

    # Statistics
    def get_stats(table, database) -> Dict

    # Cleanup
    def close()
```

### 2. Module Registration
**File:** `src/aibasic/modules/__init__.py`

Added ClickHouseModule import and registration:
```python
from .clickhouse_module import ClickHouseModule

__all__ = [..., 'ClickHouseModule']
```

### 3. Configuration
**File:** `aibasic.conf.example`

Added `[clickhouse]` section with:
```ini
[clickhouse]
# Connection
HOST = localhost
PORT = 8123
DATABASE = default

# Authentication
USERNAME = default
PASSWORD =

# SSL/TLS
USE_SSL = false
VERIFY_SSL = true

# Performance
TIMEOUT = 30
COMPRESSION = lz4  # or zstd
```

Setup instructions provided for:
- Local installation
- Docker deployment
- ClickHouse Cloud
- SSL/TLS configuration
- Compression options

### 4. Example Program
**File:** `examples/example_clickhouse.aib`

Comprehensive example demonstrating:
- Server connection and version check
- Database creation
- Table creation with partitioning and ordering
- Data insertion (single and batch)
- Analytical queries with aggregations
- DataFrame integration
- Materialized views
- Table optimization
- Statistics retrieval
- Best practices

### 5. Documentation
**File:** `docs/CLICKHOUSE_MODULE.md` (comprehensive guide)

Sections:
- Overview with feature checklist
- Configuration (basic and advanced)
- Task type usage `(clickhouse)`
- 10 detailed usage examples
- Python API reference
- Data types reference
- Best practices
- Performance tips
- Troubleshooting guide
- Security considerations
- Integration examples with other modules

**File:** `docs/md/TASK_TYPES.md`

Added `(clickhouse)` task type with examples:
```aibasic
(clickhouse) query "SELECT * FROM events"
(clickhouse) batch insert into analytics from dataframe
(clickhouse) create table with MergeTree engine
```

**File:** `requirements.txt`

Added pandas dependency (for DataFrame operations):
```txt
pandas>=1.5.0
```

## Table Engines Supported

### MergeTree Family (Most Common)
- **MergeTree()** - General purpose, requires ORDER BY
- **ReplacingMergeTree()** - Removes duplicates on merge
- **SummingMergeTree()** - Pre-aggregates numeric columns
- **AggregatingMergeTree()** - Stores intermediate aggregation states
- **CollapsingMergeTree()** - Handles row updates/deletes

### Other Engines
- **Log** - Simple log storage
- **Memory** - In-memory tables
- **Distributed** - Distributed tables across shards

## Usage Examples

### 1. Create Analytics Table
```aibasic
10 (clickhouse) create table if not exists page_views with columns:
20 (clickhouse) column "event_date" type "Date"
30 (clickhouse) column "user_id" type "UInt32"
40 (clickhouse) column "page_url" type "String"
50 (clickhouse) column "duration" type "UInt32"
60 (clickhouse) engine "MergeTree()"
70 (clickhouse) partition by "toYYYYMM(event_date)"
80 (clickhouse) order by "event_date, user_id"
```

### 2. Batch Insert from DataFrame
```aibasic
10 (csv) read file "events.csv" into events_data
20 (clickhouse) batch insert into page_views from dataframe events_data with batch_size 10000
30 print "Inserted" and rows_inserted and "rows"
```

### 3. Analytics Query
```aibasic
10 (clickhouse) query """
    SELECT
        country,
        count() as views,
        count(DISTINCT user_id) as unique_users,
        avg(duration) as avg_duration
    FROM page_views
    WHERE event_date >= today() - 7
    GROUP BY country
    ORDER BY views DESC
    LIMIT 10
"""
20 print "Top countries:" and query_result
```

### 4. Query to DataFrame
```aibasic
10 (clickhouse) query to dataframe "SELECT * FROM page_views WHERE duration > 60"
20 (df) calculate statistics
30 (df) create visualization
40 (excel) save dataframe to "analysis.xlsx"
```

### 5. Materialized View
```aibasic
10 (clickhouse) execute query """
    CREATE MATERIALIZED VIEW IF NOT EXISTS daily_stats
    ENGINE = SummingMergeTree()
    ORDER BY (event_date, country)
    AS SELECT
        event_date,
        country,
        count() as total_views,
        sum(duration) as total_duration
    FROM page_views
    GROUP BY event_date, country
"""
20 print "Materialized view created"
```

## Data Types Reference

### Numeric Types
- Integers: `UInt8`, `UInt16`, `UInt32`, `UInt64`, `Int8`, `Int16`, `Int32`, `Int64`
- Floats: `Float32`, `Float64`
- Decimal: `Decimal(P, S)`

### String Types
- `String` - Variable length
- `FixedString(N)` - Fixed length

### Date/Time Types
- `Date` - YYYY-MM-DD
- `DateTime` - Date + time (second precision)
- `DateTime64(3)` - Millisecond precision

### Complex Types
- `Array(T)` - Array of type T
- `Tuple(T1, T2, ...)` - Named tuple
- `Map(K, V)` - Key-value map
- `Enum8('val1'=1, 'val2'=2)` - Enumeration
- `Nullable(T)` - Allows NULL

### Special Types
- `UUID` - Universal unique identifier
- `IPv4`, `IPv6` - IP addresses
- `LowCardinality(T)` - For low-cardinality columns (optimization)

## Performance Features

### Compression
- **LZ4**: 2-3x compression, very fast (default recommendation)
- **ZSTD**: 3-5x compression, slower but better ratio
- Network compression reduces data transfer significantly

### Partitioning Strategies
```aibasic
# Monthly partitioning (recommended for most cases)
10 (clickhouse) partition by "toYYYYMM(event_date)"

# Daily partitioning (for high-volume tables)
20 (clickhouse) partition by "toYYYYMMDD(event_date)"

# Custom partitioning
30 (clickhouse) partition by "country"
```

### Batch Insert Performance
- Batch size 10,000 - Good balance
- Batch size 50,000 - Better for large datasets
- Batch size 100,000+ - Maximum performance for huge datasets

### Query Optimization
- Use `PREWHERE` for filtering (faster than WHERE)
- Use `LIMIT` to restrict result sets
- Use `SAMPLE` for approximate queries
- Specify columns instead of `SELECT *`
- Use appropriate data types (smaller = faster)

## Integration with AIbasic Ecosystem

### ClickHouse + PostgreSQL (ETL)
```aibasic
10 (postgres) query "SELECT * FROM transactions WHERE created_at >= now() - INTERVAL '1 hour'"
20 (clickhouse) batch insert into transactions_fact from dataframe postgres_result
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

100 (slack) send alert with message "High error rate"
110 (slack) add field "Errors" with value errors

999 print "Done"
```

### ClickHouse + Teams (Reporting)
```aibasic
10 (clickhouse) query "SELECT country, sum(revenue) as total FROM sales WHERE date = today() GROUP BY country ORDER BY total DESC LIMIT 5"
20 (teams) send status message
30 (teams) set title to "Daily Sales by Country"
40 (teams) add field "Top Country" with value query_result[0].country
50 (teams) add field "Revenue" with value query_result[0].total
```

## Use Cases

### Web Analytics
- Page views tracking
- User behavior analysis
- Conversion funnels
- A/B testing results
- Real-time dashboards

### Log Aggregation
- Application logs
- System logs
- Security events
- Audit trails
- Performance metrics

### Time-Series Data
- IoT sensor data
- Financial market data
- System monitoring
- Application metrics
- Network telemetry

### Data Warehousing
- ETL pipelines
- Business intelligence
- Reporting and analytics
- Data aggregation
- Historical data analysis

## Security Features

- ✅ SSL/TLS support for encrypted connections
- ✅ Username/password authentication
- ✅ Configurable timeouts
- ⚠️ Never commit credentials to source control
- ✅ Use environment variables or Vault for secrets
- ✅ Regular credential rotation

## Dependencies

Required Python packages:
- `requests>=2.31.0` - HTTP client (already included)
- `pandas>=1.5.0` - For DataFrame operations

## Comparison: ClickHouse vs Other Databases

| Feature | ClickHouse | PostgreSQL | MongoDB |
|---------|-----------|------------|---------|
| Type | Column-oriented OLAP | Row-oriented OLTP | Document NoSQL |
| Best For | Analytics | Transactions | Flexible schemas |
| Query Speed | Extremely fast (billions of rows) | Fast (millions) | Fast (millions) |
| Write Speed | Very fast (bulk) | Moderate | Very fast |
| Compression | Excellent (10-20x) | Good (2-3x) | Moderate |
| Aggregations | Optimized | Good | Good |
| Joins | Limited | Excellent | Limited |
| ACID | Limited | Full | Limited |
| Scalability | Horizontal | Vertical | Horizontal |

**When to Use ClickHouse:**
- ✅ Real-time analytics on large datasets (billions of rows)
- ✅ Time-series data and log aggregation
- ✅ Data warehousing and business intelligence
- ✅ High-speed aggregations and GROUP BY queries
- ✅ Append-only or mostly append workloads
- ❌ Frequent updates/deletes (use PostgreSQL)
- ❌ Complex transactions (use PostgreSQL)
- ❌ Flexible schemas (use MongoDB)

## Performance Benchmarks

Typical ClickHouse performance characteristics:
- **Query Speed**: 100M-1B rows/second on aggregation queries
- **Insert Speed**: 100K-1M rows/second (depends on configuration)
- **Compression**: 10-20x typical compression ratios
- **Scalability**: Tested with petabytes of data

## Version Information

- **Module Version**: 1.0
- **AIbasic Version**: 1.0
- **Python Compatibility**: 3.11+
- **ClickHouse Compatibility**: 20.x, 21.x, 22.x, 23.x+
- **HTTP Interface**: Uses standard ClickHouse HTTP API (port 8123)

## Resources

- [ClickHouse Official Documentation](https://clickhouse.com/docs)
- [ClickHouse SQL Reference](https://clickhouse.com/docs/en/sql-reference/)
- [Table Engines Guide](https://clickhouse.com/docs/en/engines/table-engines/)
- [Query Optimization](https://clickhouse.com/docs/en/guides/improving-query-performance/)
- [AIbasic ClickHouse Module Docs](docs/CLICKHOUSE_MODULE.md)

## Status

✅ **COMPLETE** - ClickHouse module fully implemented and documented

**Module Count**: AIbasic now has **17 integrated modules** (was 16)
**Task Types**: **38 task types** (was 37)

---

**Implementation Date**: January 2025
**AIbasic Version**: v1.0
