# Prometheus Module - Complete Reference

## Overview

The **Prometheus module** provides comprehensive monitoring and observability capabilities using the industry-standard Prometheus metrics system. This module enables metric collection, exposition for Prometheus scraping, Pushgateway integration for batch jobs, and PromQL queries for data analysis.

**Module Type:** `(prometheus)`
**Primary Use Cases:** Application monitoring, infrastructure observability, SLA tracking, performance monitoring, business metrics, alerting

---

## Table of Contents

1. [Features](#features)
2. [Configuration](#configuration)
3. [Basic Operations](#basic-operations)
4. [Advanced Features](#advanced-features)
5. [Common Use Cases](#common-use-cases)
6. [Best Practices](#best-practices)
7. [Security Considerations](#security-considerations)
8. [Troubleshooting](#troubleshooting)

---

## Features

### Core Capabilities

- **Metric Types**: Counter, Gauge, Histogram, Summary
- **Metric Creation**: Create metrics with descriptions and labels
- **Metric Operations**: Increment, set, observe, time operations
- **Labels**: Multi-dimensional metrics with label support
- **HTTP Exposition**: Expose metrics for Prometheus scraping
- **Pushgateway**: Push metrics for batch jobs and short-lived processes
- **PromQL Queries**: Query Prometheus server with PromQL
- **Range Queries**: Time-series data analysis
- **Custom Registries**: Isolated metric registries
- **Thread-Safe**: Production-ready singleton pattern

### Supported Operations

| Category | Operations |
|----------|-----------|
| **Metric Creation** | Counter, Gauge, Histogram, Summary |
| **Counter Operations** | Increment by value |
| **Gauge Operations** | Set, increment, decrement |
| **Histogram Operations** | Observe values, time code blocks |
| **Summary Operations** | Observe values with percentiles |
| **Exposition** | HTTP server, get metrics text |
| **Pushgateway** | Push metrics, delete metrics |
| **Queries** | Instant queries, range queries, current values |

---

## Configuration

### Basic Configuration (aibasic.conf)

```ini
[prometheus]
PROMETHEUS_URL = http://localhost:9090
EXPOSITION_PORT = 8000
EXPOSITION_ADDR = 0.0.0.0
PUSHGATEWAY_URL = localhost:9091
PUSHGATEWAY_JOB = aibasic
NAMESPACE = aibasic
SUBSYSTEM =
CUSTOM_REGISTRY = false
AUTO_START_HTTP = false
```

### Configuration Parameters

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `PROMETHEUS_URL` | Prometheus server URL for queries | `http://localhost:9090` | No |
| `EXPOSITION_PORT` | HTTP port for metric exposition | `8000` | No |
| `EXPOSITION_ADDR` | Bind address for HTTP server | `0.0.0.0` | No |
| `PUSHGATEWAY_URL` | Pushgateway URL | `localhost:9091` | No |
| `PUSHGATEWAY_JOB` | Default job name for Pushgateway | `aibasic` | No |
| `NAMESPACE` | Default namespace prefix for metrics | `aibasic` | No |
| `SUBSYSTEM` | Default subsystem for metrics | - | No |
| `CUSTOM_REGISTRY` | Use custom registry vs global | `false` | No |
| `AUTO_START_HTTP` | Auto-start HTTP server on init | `false` | No |

### Environment Variables

All configuration parameters can be overridden with environment variables:

```bash
export PROMETHEUS_URL=http://prometheus:9090
export PROMETHEUS_EXPOSITION_PORT=8000
export PROMETHEUS_NAMESPACE=myapp
export PROMETHEUS_PUSHGATEWAY_URL=pushgateway:9091
```

---

## Basic Operations

### Creating Metrics

```basic
REM Create Counter
10 (prometheus) create counter "http_requests_total" with description "Total HTTP requests"

REM Create Counter with labels
20 (prometheus) create counter "http_requests_total" with description "Total requests" and labels ["method", "status", "endpoint"]

REM Create Gauge
30 (prometheus) create gauge "active_connections" with description "Number of active connections"

REM Create Gauge with labels
40 (prometheus) create gauge "queue_size" with description "Queue size" and labels ["queue_type"]

REM Create Histogram
50 (prometheus) create histogram "request_duration_seconds" with description "Request duration in seconds"

REM Create Histogram with custom buckets
60 (prometheus) create histogram "payment_amount" with description "Payment amounts" and buckets [10, 50, 100, 500, 1000]

REM Create Summary
70 (prometheus) create summary "response_size_bytes" with description "Response size in bytes"
```

### Counter Operations

```basic
REM Increment counter by 1
10 (prometheus) increment counter "aibasic_http_requests_total"

REM Increment by specific value
20 (prometheus) increment counter "aibasic_http_requests_total" by 5

REM Increment with labels
30 (prometheus) increment counter "aibasic_http_requests_total" with labels {"method": "GET", "status": "200", "endpoint": "/api/users"}
```

### Gauge Operations

```basic
REM Set gauge value
10 (prometheus) set gauge "aibasic_active_connections" to 42

REM Increment gauge
20 (prometheus) increment gauge "aibasic_active_connections" by 1

REM Decrement gauge
30 (prometheus) decrement gauge "aibasic_active_connections" by 1

REM With labels
40 (prometheus) set gauge "aibasic_queue_size" to 100 with labels {"queue_type": "email"}
```

### Histogram Operations

```basic
REM Observe value
10 (prometheus) observe histogram "aibasic_request_duration_seconds" value 0.234

REM Observe with labels
20 (prometheus) observe histogram "aibasic_request_duration_seconds" value 0.456 with labels {"method": "POST", "endpoint": "/api/orders"}
```

### Summary Operations

```basic
REM Observe value
10 (prometheus) observe summary "aibasic_response_size_bytes" value 2048

REM Observe with labels
20 (prometheus) observe summary "aibasic_database_query_duration" value 0.012 with labels {"operation": "SELECT", "table": "users"}
```

---

## Advanced Features

### Metric Exposition

```basic
REM Start HTTP server for Prometheus scraping
10 (prometheus) start http server on port 8000

REM Metrics will be available at http://localhost:8000/metrics

REM Get metrics as text (for custom endpoints)
20 (prometheus) get metrics
30 PRINT RESULT
```

**Prometheus Configuration (prometheus.yml):**
```yaml
scrape_configs:
  - job_name: 'aibasic'
    static_configs:
      - targets: ['localhost:8000']
```

### Pushgateway Integration

```basic
REM For batch jobs that can't be scraped
10 (prometheus) create counter "batch_records_processed" with description "Records processed"
20 (prometheus) increment counter "aibasic_batch_records_processed" by 1000

30 REM Push to Pushgateway
40 (prometheus) push to gateway with job "nightly_batch"

50 REM Push with grouping labels
60 (prometheus) push to gateway with job "backup" and grouping {"instance": "server1", "type": "daily"}

70 REM Delete from Pushgateway
80 (prometheus) delete from gateway with job "backup" and grouping {"instance": "server1"}
```

### PromQL Queries

```basic
REM Instant query
10 (prometheus) query "http_requests_total"

REM Query with label selector
20 (prometheus) query "http_requests_total{method='GET',status='200'}"

REM Query with rate function
30 (prometheus) query "rate(http_requests_total[5m])"

REM Query with aggregation
40 (prometheus) query "sum(rate(http_requests_total[5m])) by (endpoint)"

REM Range query
50 LET end_time = TIME()
60 LET start_time = end_time - 3600
70 (prometheus) query range "cpu_usage_percent" from start_time to end_time step "1m"

REM Get current metric value
80 (prometheus) get current value of "http_requests_total" with labels {"endpoint": "/api/users"}
```

### Namespace and Subsystem

```basic
REM Create metric with custom namespace
10 (prometheus) create counter "requests" with description "Requests" and namespace "webapp"
REM Creates: webapp_requests_total

REM Create with namespace and subsystem
20 (prometheus) create counter "requests" with description "Requests" and namespace "webapp" and subsystem "api"
REM Creates: webapp_api_requests_total
```

---

## Common Use Cases

### 1. Web Application Monitoring

```basic
REM Create web app metrics
10 (prometheus) create counter "http_requests_total" with description "Total HTTP requests" and labels ["method", "endpoint", "status"]

20 (prometheus) create histogram "http_request_duration_seconds" with description "Request duration" and labels ["method", "endpoint"] and buckets [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5]

30 (prometheus) create gauge "http_requests_in_progress" with description "Requests in progress" and labels ["method", "endpoint"]

40 (prometheus) create counter "http_request_errors_total" with description "Request errors" and labels ["method", "endpoint", "error_type"]

50 REM Track request
60 (prometheus) increment gauge "aibasic_http_requests_in_progress" with labels {"method": "GET", "endpoint": "/api/users"}

70 LET start = TIME()
80 REM Process request...
90 LET duration = TIME() - start

100 (prometheus) observe histogram "aibasic_http_request_duration_seconds" value duration with labels {"method": "GET", "endpoint": "/api/users"}

110 (prometheus) increment counter "aibasic_http_requests_total" with labels {"method": "GET", "endpoint": "/api/users", "status": "200"}

120 (prometheus) decrement gauge "aibasic_http_requests_in_progress" with labels {"method": "GET", "endpoint": "/api/users"}

130 REM Start exposition
140 (prometheus) start http server on port 8000
```

### 2. Database Performance Monitoring

```basic
REM Create database metrics
10 (prometheus) create histogram "db_query_duration_seconds" with description "Query duration" and labels ["operation", "table"] and buckets [0.001, 0.01, 0.1, 1, 10]

20 (prometheus) create counter "db_queries_total" with description "Total queries" and labels ["operation", "table", "status"]

30 (prometheus) create gauge "db_connections_active" with description "Active connections"
40 (prometheus) create gauge "db_connections_idle" with description "Idle connections"

50 REM Track query
60 LET start = TIME()
70 (postgres) SELECT * FROM users WHERE active = true
80 LET duration = TIME() - start

90 (prometheus) observe histogram "aibasic_db_query_duration_seconds" value duration with labels {"operation": "SELECT", "table": "users"}

100 (prometheus) increment counter "aibasic_db_queries_total" with labels {"operation": "SELECT", "table": "users", "status": "success"}

110 (prometheus) set gauge "aibasic_db_connections_active" to 10
120 (prometheus) set gauge "aibasic_db_connections_idle" to 5
```

### 3. Microservices Monitoring

```basic
REM Service-to-service metrics
10 (prometheus) create counter "service_requests_total" with description "Service requests" and labels ["source_service", "target_service", "operation", "status"]

20 (prometheus) create histogram "service_request_duration_seconds" with description "Request duration" and labels ["source_service", "target_service", "operation"]

30 (prometheus) create gauge "service_health_status" with description "Service health (1=healthy, 0=unhealthy)" and labels ["service"]

40 REM Order service calls payment service
50 LET start = TIME()
60 (restapi) POST "http://payment-service/api/process" with data {"amount": 99.99}
70 LET duration = TIME() - start

80 (prometheus) observe histogram "aibasic_service_request_duration_seconds" value duration with labels {"source_service": "order", "target_service": "payment", "operation": "process_payment"}

90 (prometheus) increment counter "aibasic_service_requests_total" with labels {"source_service": "order", "target_service": "payment", "operation": "process_payment", "status": "200"}

100 REM Update service health
110 (prometheus) set gauge "aibasic_service_health_status" to 1 with labels {"service": "order"}
120 (prometheus) set gauge "aibasic_service_health_status" to 1 with labels {"service": "payment"}
```

### 4. Message Queue Monitoring

```basic
REM Queue metrics
10 (prometheus) create gauge "queue_size" with description "Messages in queue" and labels ["queue_name"]

20 (prometheus) create counter "queue_messages_published_total" with description "Messages published" and labels ["queue_name"]

30 (prometheus) create counter "queue_messages_consumed_total" with description "Messages consumed" and labels ["queue_name", "status"]

40 (prometheus) create histogram "queue_message_processing_duration_seconds" with description "Processing duration" and labels ["queue_name"]

50 REM Publish messages
60 FOR i = 1 TO 100
70   (mqtt) publish to "orders/new" with payload {"order_id": i}
80   (prometheus) increment counter "aibasic_queue_messages_published_total" with labels {"queue_name": "orders"}
90 NEXT i

100 (prometheus) set gauge "aibasic_queue_size" to 100 with labels {"queue_name": "orders"}

110 REM Process message
120 LET start = TIME()
130 REM Process...
140 LET duration = TIME() - start

150 (prometheus) observe histogram "aibasic_queue_message_processing_duration_seconds" value duration with labels {"queue_name": "orders"}

160 (prometheus) increment counter "aibasic_queue_messages_consumed_total" with labels {"queue_name": "orders", "status": "success"}

170 (prometheus) decrement gauge "aibasic_queue_size" with labels {"queue_name": "orders"}
```

### 5. Business Metrics

```basic
REM Business KPIs
10 (prometheus) create counter "orders_total" with description "Total orders" and labels ["status", "payment_method"]

20 (prometheus) create counter "revenue_total" with description "Total revenue" and labels ["currency", "product_category"]

30 (prometheus) create gauge "active_users" with description "Currently active users"

40 (prometheus) create histogram "order_value" with description "Order value" and buckets [10, 25, 50, 100, 250, 500, 1000]

50 REM Track order
60 (prometheus) increment counter "aibasic_orders_total" with labels {"status": "completed", "payment_method": "credit_card"}

70 (prometheus) increment counter "aibasic_revenue_total" by 99.99 with labels {"currency": "USD", "product_category": "electronics"}

80 (prometheus) observe histogram "aibasic_order_value" value 99.99

90 REM Update active users
100 (prometheus) set gauge "aibasic_active_users" to 1234
```

### 6. Batch Job Monitoring

```basic
REM Batch job metrics
10 (prometheus) create counter "jobs_total" with description "Jobs executed" and labels ["job_name", "status"]

20 (prometheus) create histogram "job_duration_seconds" with description "Job duration" and labels ["job_name"]

30 (prometheus) create gauge "job_last_success_timestamp" with description "Last successful run" and labels ["job_name"]

40 (prometheus) create gauge "job_running" with description "Job running (1=running, 0=stopped)" and labels ["job_name"]

50 REM Execute job
60 LET job_name = "email_digest"
70 (prometheus) set gauge "aibasic_job_running" to 1 with labels {"job_name": job_name}

80 LET start = TIME()
90 REM Perform job tasks...
100 LET duration = TIME() - start

110 (prometheus) increment counter "aibasic_jobs_total" with labels {"job_name": job_name, "status": "success"}

120 (prometheus) observe histogram "aibasic_job_duration_seconds" value duration with labels {"job_name": job_name}

130 (prometheus) set gauge "aibasic_job_last_success_timestamp" to TIME() with labels {"job_name": job_name}

140 (prometheus) set gauge "aibasic_job_running" to 0 with labels {"job_name": job_name}

150 REM Push to Pushgateway (batch jobs can't be scraped)
160 (prometheus) push to gateway with job job_name
```

### 7. SLA and Availability Monitoring

```basic
REM SLA metrics
10 (prometheus) create gauge "service_availability_percent" with description "Service availability" and labels ["service"]

20 (prometheus) create counter "sla_violations_total" with description "SLA violations" and labels ["service", "sla_type"]

30 (prometheus) create histogram "response_time_sla_seconds" with description "Response time vs SLA" and labels ["endpoint"]

40 REM Check SLA compliance
50 LET response_time = 0.456
60 LET sla_threshold = 0.500

70 IF response_time > sla_threshold THEN
80   (prometheus) increment counter "aibasic_sla_violations_total" with labels {"service": "api", "sla_type": "response_time"}
90 END IF

100 (prometheus) observe histogram "aibasic_response_time_sla_seconds" value response_time with labels {"endpoint": "/api/search"}

110 REM Calculate availability
120 LET availability = 99.95
130 (prometheus) set gauge "aibasic_service_availability_percent" to availability with labels {"service": "api"}
```

### 8. Cache Performance Monitoring

```basic
REM Cache metrics
10 (prometheus) create counter "cache_operations_total" with description "Cache operations" and labels ["operation", "result"]

20 (prometheus) create histogram "cache_operation_duration_seconds" with description "Operation duration" and labels ["operation"]

30 (prometheus) create gauge "cache_size_bytes" with description "Cache size"
40 (prometheus) create gauge "cache_items_count" with description "Cached items"

50 REM Cache lookup
60 LET start = TIME()
70 (redis) GET "user:12345"
80 LET duration = TIME() - start

90 IF RESULT THEN
100   (prometheus) increment counter "aibasic_cache_operations_total" with labels {"operation": "get", "result": "hit"}
110 ELSE
120   (prometheus) increment counter "aibasic_cache_operations_total" with labels {"operation": "get", "result": "miss"}
130 END IF

140 (prometheus) observe histogram "aibasic_cache_operation_duration_seconds" value duration with labels {"operation": "get"}

150 REM Cache statistics
160 (prometheus) set gauge "aibasic_cache_size_bytes" to 104857600
170 (prometheus) set gauge "aibasic_cache_items_count" to 10000
```

---

## Best Practices

### Metric Naming

1. **Use Base Units**: Always use base units (seconds, bytes) not derived (milliseconds, megabytes)
2. **Naming Convention**: `namespace_subsystem_name_unit`
   - Example: `aibasic_http_request_duration_seconds`
3. **Suffixes**:
   - Counters: `_total` (e.g., `http_requests_total`)
   - Histograms: `_bucket`, `_count`, `_sum` (auto-generated)
   - No suffix for gauges
4. **Avoid Abbreviations**: Use full words for clarity

### Label Design

1. **Low Cardinality**: Keep label values low-cardinality
   - ✅ Good: `status` (200, 404, 500)
   - ❌ Bad: `user_id` (potentially millions of values)
2. **Consistent Names**: Use same label names across metrics
   - Use `method` not `http_method` in one place and `request_method` in another
3. **Avoid Timestamps**: Never use timestamps as labels
4. **Meaningful Values**: Use descriptive label values

### Performance

1. **Minimize Metrics**: Don't create excessive metrics
2. **Reuse Metrics**: Create once, use many times with different labels
3. **Avoid High-Cardinality Labels**: Keep total label combinations < 10,000
4. **Use Summaries Sparingly**: Histograms are generally preferred

### Histogram Buckets

1. **Default Buckets**: `[.005, .01, .025, .05, .075, .1, .25, .5, .75, 1, 2.5, 5, 7.5, 10]`
2. **Custom Buckets**: Tailor to your use case
   - Request duration: `[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5]`
   - Payment amounts: `[10, 50, 100, 500, 1000, 5000]`
3. **Include Upper Bound**: Always include `+Inf` (automatic)

### Monitoring Strategy

1. **Four Golden Signals**:
   - **Latency**: How long requests take (histogram)
   - **Traffic**: Requests per second (counter with rate())
   - **Errors**: Error rate (counter with rate())
   - **Saturation**: Resource utilization (gauge)
2. **RED Method** (for services):
   - Rate, Errors, Duration
3. **USE Method** (for resources):
   - Utilization, Saturation, Errors

---

## Security Considerations

### Metric Exposition

- **Network Security**: Bind to internal network only (`EXPOSITION_ADDR = 10.0.0.1`)
- **Firewall**: Restrict access to Prometheus server only
- **No Authentication**: Prometheus metrics endpoint has no built-in auth
- **Sensitive Data**: Never include PII or secrets in metric labels or names

### Pushgateway

- **Access Control**: Restrict Pushgateway access
- **Job Naming**: Use unique job names to prevent conflicts
- **Cleanup**: Delete old metrics to prevent stale data

### PromQL Queries

- **Rate Limiting**: Implement query rate limiting
- **Timeout**: Set query timeouts to prevent resource exhaustion
- **Access Control**: Use Prometheus's authentication features

---

## Troubleshooting

### Common Issues

**Metrics Not Appearing**

```
Issue: Metrics don't show up in Prometheus
Solution:
- Check HTTP server is started: (prometheus) start http server
- Verify Prometheus scrape config includes target
- Check firewall allows connections on exposition port
- Verify namespace matches: metric name should be namespace_metric_name_total
```

**High Cardinality Warning**

```
Issue: Too many time series
Solution:
- Reduce label values (avoid user IDs, timestamps)
- Remove unnecessary labels
- Use recording rules to pre-aggregate
- Consider sampling for high-frequency metrics
```

**Pushgateway Not Working**

```
Issue: Metrics not appearing in Pushgateway
Solution:
- Verify Pushgateway URL is correct
- Check network connectivity
- Ensure job name is unique
- Check grouping labels are consistent
```

**Query Performance Issues**

```
Issue: PromQL queries are slow
Solution:
- Add time range limits to queries
- Use recording rules for complex queries
- Reduce retention period if too long
- Optimize label selectors
```

---

## API Reference

### Metric Creation Methods

- `create_counter(name, description, labels, namespace, subsystem)` - Create counter metric
- `create_gauge(name, description, labels, namespace, subsystem)` - Create gauge metric
- `create_histogram(name, description, buckets, labels, namespace, subsystem)` - Create histogram
- `create_summary(name, description, labels, namespace, subsystem)` - Create summary

### Metric Operation Methods

- `counter_inc(metric_name, value, labels)` - Increment counter
- `gauge_set(metric_name, value, labels)` - Set gauge value
- `gauge_inc(metric_name, value, labels)` - Increment gauge
- `gauge_dec(metric_name, value, labels)` - Decrement gauge
- `histogram_observe(metric_name, value, labels)` - Observe histogram value
- `summary_observe(metric_name, value, labels)` - Observe summary value

### Exposition Methods

- `start_http_server(port, addr)` - Start HTTP server for scraping
- `get_metrics()` - Get metrics in Prometheus text format

### Pushgateway Methods

- `push_to_gateway(job, grouping_key, gateway_url)` - Push metrics to Pushgateway
- `delete_from_gateway(job, grouping_key, gateway_url)` - Delete metrics from Pushgateway

### Query Methods

- `query(promql)` - Execute instant PromQL query
- `query_range(promql, start_time, end_time, step)` - Execute range query
- `get_metric_range_data(metric_name, label_config, start_time, end_time, step)` - Get metric range data
- `get_current_metric_value(metric_name, label_config)` - Get current metric value

### Utility Methods

- `list_metrics()` - List all registered metrics
- `get_metric_info(metric_name)` - Get metric information
- `metric_exists(metric_name)` - Check if metric exists

---

## Integration Examples

### With REST API Module

```basic
REM Monitor API calls
10 (prometheus) create counter "api_calls_total" with description "API calls" and labels ["endpoint", "status"]

20 LET start = TIME()
30 (restapi) GET "https://api.example.com/users"
40 LET duration = TIME() - start

50 (prometheus) increment counter "aibasic_api_calls_total" with labels {"endpoint": "/users", "status": "200"}
```

### With PostgreSQL Module

```basic
REM Monitor database queries
10 (prometheus) create histogram "db_query_seconds" with description "Query duration"

20 LET start = TIME()
30 (postgres) SELECT * FROM users
40 LET duration = TIME() - start

50 (prometheus) observe histogram "aibasic_db_query_seconds" value duration
```

### With Docker Module

```basic
REM Monitor container metrics
10 (prometheus) create gauge "containers_running" with description "Running containers"

20 (docker) list containers
30 LET count = LEN(RESULT)
40 (prometheus) set gauge "aibasic_containers_running" to count
```

---

## Additional Resources

- **Prometheus Documentation**: https://prometheus.io/docs/
- **PromQL Guide**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Best Practices**: https://prometheus.io/docs/practices/naming/
- **Metric Types**: https://prometheus.io/docs/concepts/metric_types/
- **Pushgateway**: https://github.com/prometheus/pushgateway
- **Grafana Integration**: https://grafana.com/docs/grafana/latest/datasources/prometheus/

---

## Module Information

- **Module Name**: PrometheusModule
- **Task Type**: `(prometheus)`
- **Dependencies**: `prometheus-client>=0.19.0`, `prometheus-api-client>=0.5.3`
- **Python Version**: 3.7+
- **AIbasic Version**: 1.0+

---

*For more examples, see [example_prometheus.aib](../../examples/example_prometheus.aib)*
