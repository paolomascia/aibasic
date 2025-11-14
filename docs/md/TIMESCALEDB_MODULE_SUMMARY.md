# TimescaleDB Module Summary

## Overview

The **TimescaleDB Module** provides full integration with TimescaleDB, a PostgreSQL extension optimized for time-series data. TimescaleDB combines the reliability and familiarity of PostgreSQL with automatic partitioning, compression, and time-series specific features, making it perfect for IoT, monitoring, financial data, and analytics applications.

**Module**: `aibasic.modules.TimescaleDBModule`
**Task Type**: `(timescaledb)`
**Python Package**: `psycopg2-binary>=2.9.9` (already included for PostgreSQL)
**Docker Image**: `timescale/timescaledb:latest-pg16`

## Key Features

### Core Capabilities
- **Hypertables** - Automatic partitioning of time-series data into chunks
- **Continuous Aggregates** - Auto-updating materialized views for pre-computed analytics
- **Compression** - Automatic compression of old data (90%+ storage reduction)
- **Data Retention** - Automatic deletion of old data based on policies
- **Time-Bucket Queries** - Efficient aggregation over time intervals
- **Gap Filling** - Fill missing data points in time-series
- **100% PostgreSQL Compatible** - All PostgreSQL features work seamlessly

### Advanced Features
- **Space Partitioning** - Partition by additional dimensions (e.g., sensor_id, symbol)
- **Downsampling** - Create rollups at different time granularities
- **High Ingest Rates** - Millions of rows per second
- **Complex Queries** - Full SQL support with time-series optimizations
- **Distributed Architecture** - Scale across multiple nodes (Enterprise)

## Configuration

Add to `aibasic.conf`:

```ini
[timescaledb]
HOST = localhost
PORT = 5432
DATABASE = tsdb
USERNAME = postgres
PASSWORD = password
POOL_SIZE = 5
MAX_OVERFLOW = 10
```

## Module API

### Initialization
```python
from aibasic.modules import TimescaleDBModule

# Initialize (singleton)
tsdb = TimescaleDBModule(
    host="localhost",
    port=5432,
    database="tsdb",
    user="postgres",
    password="password",
    pool_size=5,
    max_overflow=10
)
```

### Hypertable Management
- `create_hypertable(table_name, time_column, chunk_time_interval, ...)` - Convert table to hypertable
- `drop_hypertable(table_name, cascade)` - Drop hypertable
- `get_hypertable_stats(table_name)` - Get hypertable statistics
- `get_chunk_info(table_name)` - Get chunk information

### Retention Policies
- `add_retention_policy(table_name, drop_after)` - Auto-delete old data
- `remove_retention_policy(table_name)` - Remove retention policy

### Compression Policies
- `add_compression_policy(table_name, compress_after)` - Auto-compress old data
- `remove_compression_policy(table_name)` - Remove compression policy
- `compress_chunk(chunk_name)` - Manually compress chunk
- `decompress_chunk(chunk_name)` - Manually decompress chunk

### Continuous Aggregates
- `create_continuous_aggregate(view_name, hypertable, time_column, bucket_interval, select_query)` - Create auto-updating view
- `drop_continuous_aggregate(view_name)` - Drop continuous aggregate
- `refresh_continuous_aggregate(view_name, start_time, end_time)` - Manual refresh
- `add_continuous_aggregate_policy(view_name, start_offset, end_offset, schedule_interval)` - Auto-refresh policy

### Query Operations
- `execute_query(query, params, fetch)` - Execute SQL query
- `execute_many(query, params_list)` - Batch execute
- `query_to_dataframe(query, params)` - Query to pandas DataFrame
- `time_bucket_query(table_name, time_column, bucket_interval, aggregations, ...)` - Time-bucket aggregation
- `fill_gaps(table_name, time_column, bucket_interval, start_time, end_time, columns, fill_method)` - Fill gaps in data

## Usage Examples

### Example 1: Create Hypertable for IoT Sensors

```python
# Create regular table
tsdb.execute_query("""
    CREATE TABLE sensor_data (
        time TIMESTAMPTZ NOT NULL,
        sensor_id INTEGER,
        temperature DOUBLE PRECISION,
        humidity DOUBLE PRECISION,
        location TEXT
    )
""", fetch=False)

# Convert to hypertable with 1-day chunks
result = tsdb.create_hypertable(
    table_name="sensor_data",
    time_column="time",
    chunk_time_interval="1 day",
    if_not_exists=True
)

# Insert data
tsdb.execute_query("""
    INSERT INTO sensor_data VALUES
        (NOW(), 1, 22.5, 45.0, 'Office'),
        (NOW() - INTERVAL '1 hour', 1, 23.0, 46.5, 'Office'),
        (NOW() - INTERVAL '2 hours', 1, 22.8, 45.8, 'Office')
""", fetch=False)
```

### Example 2: Time-Bucket Aggregations

```python
import pandas as pd

# Get 15-minute averages
df = tsdb.time_bucket_query(
    table_name="sensor_data",
    time_column="time",
    bucket_interval="15 minutes",
    aggregations={
        "temperature": "AVG",
        "humidity": "AVG",
        "count": "COUNT(*)"
    },
    start_time="NOW() - INTERVAL '24 hours'",
    order_by="bucket ASC"
)

print(df.head())
```

### Example 3: Continuous Aggregates

```python
# Create hourly summary that auto-updates
result = tsdb.create_continuous_aggregate(
    view_name="sensor_data_hourly",
    hypertable="sensor_data",
    time_column="time",
    bucket_interval="1 hour",
    select_query="""
        sensor_id,
        AVG(temperature) as avg_temp,
        AVG(humidity) as avg_humidity,
        MAX(temperature) as max_temp,
        MIN(temperature) as min_temp
        FROM sensor_data
        GROUP BY bucket, sensor_id
    """,
    with_data=True
)

# Add automatic refresh policy (every 30 minutes)
tsdb.add_continuous_aggregate_policy(
    view_name="sensor_data_hourly",
    start_offset="3 days",
    end_offset="1 hour",
    schedule_interval="30 minutes"
)

# Query the aggregate
df = tsdb.query_to_dataframe("""
    SELECT * FROM sensor_data_hourly
    WHERE sensor_id = 1
    ORDER BY bucket DESC
    LIMIT 24
""")
```

### Example 4: Data Retention

```python
# Keep data for 30 days, automatically delete older
result = tsdb.add_retention_policy(
    table_name="sensor_data",
    drop_after="30 days",
    if_not_exists=True
)

# Result: {'success': True, 'table': 'sensor_data', 'drop_after': '30 days'}
```

### Example 5: Compression

```python
# Compress data older than 7 days
result = tsdb.add_compression_policy(
    table_name="sensor_data",
    compress_after="7 days",
    if_not_exists=True
)

# Get compression stats
chunks = tsdb.get_chunk_info("sensor_data")
for chunk in chunks:
    print(f"Chunk: {chunk['chunk_name']}, Compressed: {chunk['is_compressed']}")
```

### Example 6: Gap Filling

```python
# Fill missing data points using last observation carried forward
df = tsdb.fill_gaps(
    table_name="sensor_data",
    time_column="time",
    bucket_interval="10 minutes",
    start_time="NOW() - INTERVAL '2 hours'",
    end_time="NOW()",
    columns=["temperature"],
    fill_method="locf"  # or "linear" or "NULL"
)
```

### Example 7: Stock Market Data with Space Partitioning

```python
# Create table
tsdb.execute_query("""
    CREATE TABLE stock_prices (
        time TIMESTAMPTZ NOT NULL,
        symbol TEXT,
        open DOUBLE PRECISION,
        high DOUBLE PRECISION,
        low DOUBLE PRECISION,
        close DOUBLE PRECISION,
        volume BIGINT
    )
""", fetch=False)

# Create hypertable with space partitioning by symbol
result = tsdb.create_hypertable(
    table_name="stock_prices",
    time_column="time",
    chunk_time_interval="1 week",
    partitioning_column="symbol",
    number_partitions=4,
    if_not_exists=True
)

# Insert stock data
tsdb.execute_query("""
    INSERT INTO stock_prices VALUES
        (NOW(), 'AAPL', 150.0, 152.5, 149.0, 151.5, 50000000),
        (NOW(), 'GOOGL', 2800.0, 2850.0, 2780.0, 2820.0, 1000000)
""", fetch=False)

# Create daily OHLCV continuous aggregate
tsdb.create_continuous_aggregate(
    view_name="stock_prices_daily",
    hypertable="stock_prices",
    time_column="time",
    bucket_interval="1 day",
    select_query="""
        symbol,
        FIRST(open, time) as open,
        MAX(high) as high,
        MIN(low) as low,
        LAST(close, time) as close,
        SUM(volume) as total_volume
        FROM stock_prices
        GROUP BY bucket, symbol
    """,
    with_data=True
)
```

### Example 8: Application Performance Monitoring

```python
# Create APM metrics table
tsdb.execute_query("""
    CREATE TABLE apm_metrics (
        time TIMESTAMPTZ NOT NULL,
        service_name TEXT,
        endpoint TEXT,
        response_time_ms INTEGER,
        status_code INTEGER
    )
""", fetch=False)

# Convert to hypertable (high-frequency data, use 1-hour chunks)
tsdb.create_hypertable(
    table_name="apm_metrics",
    time_column="time",
    chunk_time_interval="1 hour"
)

# Create 5-minute performance summary
tsdb.create_continuous_aggregate(
    view_name="apm_summary_5min",
    hypertable="apm_metrics",
    time_column="time",
    bucket_interval="5 minutes",
    select_query="""
        service_name,
        endpoint,
        AVG(response_time_ms) as avg_response,
        MAX(response_time_ms) as max_response,
        COUNT(*) as request_count,
        COUNT(*) FILTER (WHERE status_code >= 500) as error_count
        FROM apm_metrics
        GROUP BY bucket, service_name, endpoint
    """,
    with_data=True
)

# Query errors
df = tsdb.query_to_dataframe("""
    SELECT * FROM apm_summary_5min
    WHERE error_count > 0
    ORDER BY bucket DESC
    LIMIT 10
""")
```

## Best Practices

### Hypertable Design
1. **Choose appropriate chunk intervals**:
   - High-frequency data (seconds/minutes): 1 hour to 1 day
   - Medium-frequency (minutes/hours): 1 day to 1 week
   - Low-frequency (hours/days): 1 week to 1 month

2. **Use space partitioning** for high-cardinality dimensions (e.g., device_id, symbol)
   - Improves query performance when filtering by that dimension
   - Typically use 2-8 partitions

3. **Create indexes** on commonly queried columns:
   ```sql
   CREATE INDEX ON sensor_data (sensor_id, time DESC);
   ```

### Continuous Aggregates
1. **Use for frequently queried aggregations** (hourly, daily summaries)
2. **Set appropriate refresh policies**:
   - Real-time data: refresh every few minutes
   - Historical data: refresh daily or weekly
3. **Use cascading aggregates** for multi-level rollups (5min → hourly → daily)

### Compression
1. **Enable compression** for data older than your typical query range
2. **Typical compression ratios**: 90-95% for time-series data
3. **Compressed data is still queryable** (decompression is automatic)
4. **Tradeoff**: Saves storage but adds decompression overhead on queries

### Retention Policies
1. **Set retention based on business requirements**
2. **Consider cascading retention**:
   - Raw data: 30 days
   - Hourly aggregates: 1 year
   - Daily aggregates: forever
3. **Test with `SELECT drop_chunks()` before setting policy**

### Performance Optimization
1. **Batch inserts** for high throughput (1000-10000 rows per batch)
2. **Use COPY for bulk loading** (faster than INSERT)
3. **Partition queries** by time and space dimensions
4. **Use continuous aggregates** instead of repeated calculations
5. **Monitor chunk size** (aim for 25-100 chunks per query)

## Common Use Cases

### 1. IoT & Sensor Data
- Temperature, humidity, pressure sensors
- Smart home devices
- Industrial equipment monitoring
- Environmental monitoring

### 2. Application Performance Monitoring (APM)
- Response times
- Error rates
- Resource usage (CPU, memory, disk)
- Request tracking

### 3. Financial Data
- Stock prices (OHLCV data)
- Trading volumes
- Market indicators
- Cryptocurrency prices

### 4. Server & Infrastructure Monitoring
- System metrics (CPU, memory, disk, network)
- Log aggregation
- Service health checks
- Performance metrics

### 5. Business Analytics
- User activity tracking
- Sales metrics over time
- Website analytics
- Customer behavior analysis

## Comparison with Other Databases

### vs. ClickHouse
**TimescaleDB Advantages:**
- PostgreSQL compatibility (use all PostgreSQL features)
- ACID transactions
- Easier to learn (standard SQL)
- Better for updates and deletes

**ClickHouse Advantages:**
- Faster for pure OLAP queries on massive datasets
- Better compression ratios
- Columnar storage

### vs. InfluxDB
**TimescaleDB Advantages:**
- Full SQL support
- PostgreSQL ecosystem (tools, extensions)
- Better for complex queries and joins
- ACID guarantees

**InfluxDB Advantages:**
- Purpose-built query language (InfluxQL/Flux)
- Simpler for basic time-series use cases

### vs. Regular PostgreSQL
**TimescaleDB Advantages:**
- Automatic partitioning (no manual chunk management)
- Continuous aggregates (auto-updating materialized views)
- Native compression
- Time-series specific functions
- 10-100x better performance for time-series queries

## Troubleshooting

### Slow Queries
```python
# Check chunk statistics
stats = tsdb.get_hypertable_stats("sensor_data")
print(f"Number of chunks: {stats['num_chunks']}")

# Check query plan
df = tsdb.query_to_dataframe("EXPLAIN ANALYZE SELECT ...")
```

### High Storage Usage
```python
# Check compression status
chunks = tsdb.get_chunk_info("sensor_data")
uncompressed = [c for c in chunks if not c['is_compressed']]
print(f"Uncompressed chunks: {len(uncompressed)}")

# Manually compress old chunks
for chunk in uncompressed:
    tsdb.compress_chunk(chunk['chunk_name'])
```

### Connection Issues
```python
# Test connection
try:
    result = tsdb.execute_query("SELECT NOW();")
    print("Connected successfully:", result)
except Exception as e:
    print("Connection error:", e)
```

## Additional Resources

- **TimescaleDB Documentation**: https://docs.timescale.com/
- **Time-Series Best Practices**: https://docs.timescale.com/timescaledb/latest/how-to-guides/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Compression Guide**: https://docs.timescale.com/timescaledb/latest/how-to-guides/compression/

## Module Summary

The TimescaleDB module brings enterprise-grade time-series capabilities to AIbasic. With automatic partitioning, compression, continuous aggregates, and full PostgreSQL compatibility, it's perfect for IoT, monitoring, financial data, and any application dealing with time-series data.

**Total Capabilities**: Hypertables, continuous aggregates, compression, retention policies, gap filling, time-bucket queries, space partitioning

**Production Ready**: Connection pooling, automatic chunk management, 90%+ compression, millions of rows/sec ingest

**Status**: ✅ Complete and tested with TimescaleDB 2.x on PostgreSQL 16
