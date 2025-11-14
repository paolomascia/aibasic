# Elasticsearch Module Summary

## Overview

The **Elasticsearch Module** provides full integration with Elasticsearch, a distributed search and analytics engine built on Apache Lucene. This module enables AIbasic programs to perform full-text search, log analytics, real-time data processing, and complex aggregations on massive datasets.

**Module**: `aibasic.modules.ElasticsearchModule`
**Task Type**: `(elasticsearch)`
**Python Package**: `elasticsearch>=8.0.0`

## Key Features

### Core Capabilities
- **Full-text Search** - Powerful search with fuzzy matching, wildcards, and relevance scoring
- **Query DSL** - JSON-based query language for complex searches
- **Aggregations** - Statistical analysis, grouping, histograms, and time-series analytics
- **Index Management** - Create, delete, configure indexes with custom mappings
- **Document CRUD** - Complete create, read, update, delete operations
- **Bulk Operations** - High-performance batch indexing and updates
- **Real-time** - Near real-time search and analytics capabilities

### Advanced Features
- **Multi-field Search** - Search across multiple fields simultaneously
- **Fuzzy Search** - Typo-tolerant search with automatic fuzziness
- **Range Queries** - Numeric and date range filtering
- **Bool Queries** - Complex boolean logic (must, should, filter, must_not)
- **Geospatial** - Location-based queries (not yet implemented)
- **Highlighting** - Highlight matching terms in search results
- **Suggestions** - Auto-complete and did-you-mean functionality

## Configuration

Add to `aibasic.conf`:

```ini
[elasticsearch]
# Connection Settings
HOSTS = http://localhost:9200  # Single host
# HOSTS = http://host1:9200,http://host2:9200  # Multiple hosts

# Authentication (choose one)
USERNAME = elastic
PASSWORD = changeme
# API_KEY = base64_encoded_api_key  # Recommended for production

# SSL/TLS
VERIFY_CERTS = false  # Set to true in production
# CA_CERTS = /path/to/ca.pem

# Connection Settings
TIMEOUT = 30
MAX_RETRIES = 3
RETRY_ON_TIMEOUT = true
```

## Module API

### Initialization
```python
from aibasic.modules import ElasticsearchModule

# Initialize (singleton)
es = ElasticsearchModule(
    hosts="http://localhost:9200",
    username="elastic",
    password="changeme",
    verify_certs=False,
    timeout=30,
    max_retries=3
)
```

### Connection Management
- `ping()` - Check cluster connectivity
- `info()` - Get cluster information
- `get_cluster_health()` - Get cluster health status

### Index Management
- `create_index(index, mappings, settings, aliases)` - Create index with configuration
- `delete_index(index)` - Delete index
- `index_exists(index)` - Check if index exists
- `refresh_index(index)` - Make recent changes searchable
- `put_mapping(index, properties)` - Update field mappings
- `create_alias(index, alias)` - Create index alias
- `get_index_stats(index)` - Get index statistics

### Document Operations
- `index_document(index, document, doc_id, refresh)` - Index single document
- `bulk_index(index, documents, id_field, refresh)` - Bulk index documents
- `get_document(index, doc_id)` - Retrieve document by ID
- `update_document(index, doc_id, document, refresh)` - Update document
- `delete_document(index, doc_id, refresh)` - Delete document
- `delete_by_query(index, query, refresh)` - Delete documents matching query
- `update_by_query(index, query, script, refresh)` - Update documents matching query

### Search Operations
- `search(index, query, size, from_, sort, source, aggs)` - Execute search
- `search_df(index, query, size)` - Search and return as pandas DataFrame
- `count(index, query)` - Count documents matching query

## Usage Examples

### Example 1: Create Index with Mappings

```python
es.create_index(
    index="products",
    mappings={
        "properties": {
            "name": {"type": "text"},
            "description": {"type": "text"},
            "category": {"type": "keyword"},
            "price": {"type": "float"},
            "stock": {"type": "integer"},
            "tags": {"type": "keyword"},
            "created_at": {"type": "date"}
        }
    },
    settings={
        "number_of_shards": 1,
        "number_of_replicas": 0
    }
)
```

### Example 2: Index Documents

```python
# Single document
es.index_document(
    index="products",
    document={
        "name": "Laptop Pro 15",
        "description": "High-performance laptop",
        "category": "Electronics",
        "price": 1299.99,
        "stock": 50,
        "tags": ["laptop", "computer"],
        "created_at": "2025-01-15T10:00:00Z"
    },
    doc_id="prod-001",
    refresh=True
)

# Bulk index
documents = [
    {"name": "Mouse", "price": 29.99, "category": "Electronics"},
    {"name": "Keyboard", "price": 89.99, "category": "Electronics"}
]
es.bulk_index(index="products", documents=documents, refresh=True)
```

### Example 3: Search Queries

```python
# Simple match query
result = es.search(
    index="products",
    query={"match": {"description": "laptop"}},
    size=10
)

# Range query
result = es.search(
    index="products",
    query={
        "range": {
            "price": {"gte": 50, "lte": 100}
        }
    }
)

# Bool query (complex)
result = es.search(
    index="products",
    query={
        "bool": {
            "must": [
                {"match": {"description": "keyboard"}}
            ],
            "filter": [
                {"range": {"price": {"lt": 100}}}
            ]
        }
    }
)

# Fuzzy search (typo-tolerant)
result = es.search(
    index="products",
    query={
        "fuzzy": {
            "name": {
                "value": "keybord",  # Misspelled
                "fuzziness": "AUTO"
            }
        }
    }
)

# Multi-match (multiple fields)
result = es.search(
    index="products",
    query={
        "multi_match": {
            "query": "wireless keyboard",
            "fields": ["name", "description"],
            "type": "best_fields"
        }
    }
)
```

### Example 4: Aggregations

```python
# Average price
result = es.search(
    index="products",
    size=0,
    aggs={
        "avg_price": {"avg": {"field": "price"}},
        "total_stock": {"sum": {"field": "stock"}},
        "price_stats": {"stats": {"field": "price"}}
    }
)

# Terms aggregation (grouping)
result = es.search(
    index="products",
    size=0,
    aggs={
        "categories": {
            "terms": {"field": "category"}
        }
    }
)

# Histogram
result = es.search(
    index="products",
    size=0,
    aggs={
        "price_histogram": {
            "histogram": {
                "field": "price",
                "interval": 50
            }
        }
    }
)

# Date histogram (time-series)
result = es.search(
    index="logs",
    size=0,
    aggs={
        "logs_over_time": {
            "date_histogram": {
                "field": "timestamp",
                "fixed_interval": "1h"
            }
        }
    }
)
```

### Example 5: DataFrame Integration

```python
import pandas as pd

# Search and convert to DataFrame
df = es.search_df(
    index="products",
    query={"match_all": {}},
    size=1000
)

print(df.head())
print(df.describe())

# Analyze in pandas
high_price = df[df['price'] > 100]
by_category = df.groupby('category')['price'].mean()
```

### Example 6: Bulk Operations

```python
# Update by query (increase all prices by 10%)
result = es.update_by_query(
    index="products",
    query={"match_all": {}},
    script={
        "source": "ctx._source.price *= 1.10",
        "lang": "painless"
    },
    refresh=True
)

# Delete by query
result = es.delete_by_query(
    index="products",
    query={"term": {"stock": 0}},
    refresh=True
)
```

### Example 7: Log Analytics Use Case

```python
# Create logs index
es.create_index(
    index="logs",
    mappings={
        "properties": {
            "timestamp": {"type": "date"},
            "level": {"type": "keyword"},
            "message": {"type": "text"},
            "service": {"type": "keyword"},
            "host": {"type": "keyword"},
            "response_time": {"type": "integer"}
        }
    }
)

# Index log entries
logs = [
    {
        "timestamp": "2025-01-15T10:00:00Z",
        "level": "ERROR",
        "message": "Connection timeout",
        "service": "api",
        "host": "server1",
        "response_time": 5000
    },
    # ... more logs
]
es.bulk_index(index="logs", documents=logs, refresh=True)

# Search errors only
errors = es.search(
    index="logs",
    query={"term": {"level": "ERROR"}},
    sort=[{"timestamp": "desc"}],
    size=100
)

# Analyze errors by service
result = es.search(
    index="logs",
    size=0,
    aggs={
        "errors_by_service": {
            "terms": {"field": "service"},
            "aggs": {
                "avg_response_time": {
                    "avg": {"field": "response_time"}
                }
            }
        }
    }
)
```

## Query DSL Reference

### Match Queries
```python
{"match": {"field": "value"}}  # Text search (analyzed)
{"match_all": {}}  # Match all documents
{"multi_match": {"query": "text", "fields": ["field1", "field2"]}}
```

### Term Queries
```python
{"term": {"field": "exact"}}  # Exact match (keyword fields)
{"terms": {"field": ["value1", "value2"]}}  # Multiple values
{"wildcard": {"field": {"value": "*pattern*"}}}  # Wildcard
{"fuzzy": {"field": {"value": "vlue", "fuzziness": "AUTO"}}}  # Typo-tolerant
```

### Range Queries
```python
{"range": {"price": {"gte": 10, "lte": 100}}}  # Numeric range
{"range": {"date": {"gte": "2025-01-01", "lt": "2025-02-01"}}}  # Date range
```

### Bool Queries
```python
{
    "bool": {
        "must": [{"match": {"field": "value"}}],  # AND (affects score)
        "filter": [{"term": {"status": "active"}}],  # AND (no scoring)
        "should": [{"term": {"tag": "featured"}}],  # OR (optional)
        "must_not": [{"term": {"deleted": true}}],  # NOT
        "minimum_should_match": 1
    }
}
```

## Aggregation Reference

### Metrics Aggregations
```python
{"avg": {"field": "price"}}  # Average
{"sum": {"field": "quantity"}}  # Sum
{"min": {"field": "price"}}  # Minimum
{"max": {"field": "price"}}  # Maximum
{"stats": {"field": "price"}}  # count, min, max, avg, sum
{"cardinality": {"field": "user_id"}}  # Unique count
```

### Bucket Aggregations
```python
{"terms": {"field": "category", "size": 10}}  # Group by field
{"histogram": {"field": "price", "interval": 50}}  # Numeric distribution
{"date_histogram": {"field": "timestamp", "fixed_interval": "1h"}}  # Time-series
{"range": {"field": "price", "ranges": [{"to": 50}, {"from": 50, "to": 100}, {"from": 100}]}}
```

## Best Practices

### Performance
1. **Use bulk operations** for indexing multiple documents (10-100x faster)
2. **Disable refresh** during bulk indexing, refresh once at the end
3. **Use filters instead of queries** when you don't need scoring
4. **Limit result size** - use pagination for large result sets
5. **Use _source filtering** to return only needed fields
6. **Avoid deep pagination** - use search_after for large offsets

### Index Design
1. **Choose correct field types** - text for full-text, keyword for exact match
2. **Disable indexing** for fields you don't search (`"index": false`)
3. **Use doc_values** for sorting/aggregations (enabled by default)
4. **Set appropriate shard count** - 1 shard for < 50GB, more for larger
5. **Use index templates** for consistent mapping across similar indexes

### Query Optimization
1. **Use term queries** for keyword fields (faster than match)
2. **Use bool filter** instead of bool must when scoring isn't needed
3. **Avoid wildcard** at the beginning of patterns (`*term` is slow)
4. **Use prefix instead of wildcard** when possible
5. **Cache filters** - Elasticsearch caches frequently used filters

### Security
1. **Use API keys** instead of username/password in production
2. **Enable SSL/TLS** for network encryption
3. **Verify certificates** in production (`verify_certs=true`)
4. **Use role-based access control** to limit permissions
5. **Audit access logs** for security monitoring

## Common Use Cases

### 1. Application Search
- E-commerce product search
- Documentation search
- Content management system search

### 2. Log Analytics
- Application log aggregation
- Error tracking and monitoring
- Performance analysis

### 3. Business Intelligence
- Real-time dashboards
- Trend analysis
- Customer behavior analytics

### 4. Security Analytics
- SIEM (Security Information and Event Management)
- Threat detection
- Audit log analysis

### 5. IoT & Time-Series
- Sensor data analysis
- Metric aggregation
- Anomaly detection

## Comparison with OpenSearch

Elasticsearch and OpenSearch are both based on the same codebase (Elasticsearch pre-7.10), but have diverged:

**Similarities:**
- Both use Query DSL
- Similar aggregation framework
- Compatible client libraries
- Index management concepts

**Differences:**
- Elasticsearch has X-Pack features (security, monitoring, ML)
- OpenSearch is fully open-source (Apache 2.0)
- Elasticsearch 8+ requires authentication by default
- Slightly different feature sets and APIs

**When to Use Elasticsearch:**
- Need latest Elasticsearch features
- Elastic Cloud managed service
- Advanced machine learning capabilities
- Official Elastic support

**When to Use OpenSearch:**
- Fully open-source requirement
- AWS OpenSearch Service
- Community-driven development
- Cost-sensitive deployments

## Troubleshooting

### Connection Issues
```python
# Test connectivity
if es.ping():
    print("Connected!")
else:
    print("Cannot connect to Elasticsearch")

# Get cluster info
info = es.info()
print(f"Cluster: {info['cluster_name']}")
print(f"Version: {info['version']['number']}")
```

### Authentication Errors
- Check username/password are correct
- Verify API key is valid and properly formatted
- Ensure user has required permissions

### Search Not Finding Documents
- Check if documents were indexed (`refresh=True`)
- Verify field mappings match your queries
- Use `_analyze` API to test text analysis
- Check if field is `text` (analyzed) or `keyword` (exact match)

### Performance Issues
- Use bulk operations for indexing
- Add more shards for large indexes
- Use filters instead of queries when possible
- Reduce result size and use pagination
- Monitor cluster health and resources

## Additional Resources

- **Elasticsearch Documentation**: https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html
- **Query DSL Reference**: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html
- **Aggregations Guide**: https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations.html
- **Python Client**: https://elasticsearch-py.readthedocs.io/

## Module Summary

The Elasticsearch module brings enterprise-grade search and analytics capabilities to AIbasic. With support for full-text search, complex aggregations, and real-time analytics, it's perfect for applications requiring powerful search functionality, log analytics, or business intelligence.

**Total Capabilities**: 20+ search query types, 15+ aggregation types, index management, bulk operations, DataFrame integration

**Production Ready**: Connection pooling, automatic retries, SSL/TLS support, authentication, cluster health monitoring

**Status**: ✅ Complete and tested with Elasticsearch 8.11+ and compatible with earlier versions
