# AIBasic Task Types Reference

## Overview

Task types help the compiler understand what kind of operation you want to perform, allowing it to generate more accurate and efficient code. Task types are **optional** and can be specified explicitly in your instructions.

## Syntax

To specify a task type, use the format `(task_type)` at the beginning of your instruction:

```
10 (csv) read the file customers.csv
20 (api) call the weather API
30 (math) calculate the average revenue
```

If you don't specify a task type, the compiler will automatically detect it based on keywords in your instruction.

## Available Task Types

### Data Operations

#### `csv` - CSV Operations
- **Description**: Reading, writing, or manipulating CSV files
- **Keywords**: csv, read_csv, to_csv
- **Common Libraries**: pandas, csv
- **Examples**:
  - `10 (csv) read the file data.csv`
  - `20 (csv) save dataframe to output.csv`

#### `excel` - Excel Operations
- **Description**: Working with Excel files (.xlsx, .xls)
- **Keywords**: excel, xlsx, xls, workbook, worksheet
- **Common Libraries**: pandas, openpyxl, xlsxwriter
- **Examples**:
  - `10 (excel) create Excel file with sales data`
  - `20 (excel) read worksheet from report.xlsx`

#### `json` - JSON Operations
- **Description**: Parsing, creating, or manipulating JSON data
- **Keywords**: json, parse json, to_json
- **Common Libraries**: json, pandas
- **Examples**:
  - `10 (json) parse JSON from API response`
  - `20 (json) convert dataframe to JSON`

#### `xml` - XML Operations
- **Description**: Working with XML files and data
- **Keywords**: xml, parse xml, xpath
- **Common Libraries**: xml.etree.ElementTree, lxml
- **Examples**:
  - `10 (xml) parse XML configuration`
  - `20 (xml) extract data from XML`

#### `db` - Database Operations
- **Description**: SQL database queries, connections, and data storage
- **Keywords**: database, sql, query, table, insert, select, update, delete
- **Common Libraries**: sqlite3, sqlalchemy, pandas
- **Examples**:
  - `10 (db) query customers from database`
  - `20 (db) insert records into table`

#### `postgres` - PostgreSQL Operations (with Module)
- **Description**: PostgreSQL-specific operations using connection pool module
- **Keywords**: postgres, postgresql, pg
- **Common Libraries**: psycopg2
- **Module**: `aibasic.modules.PostgresModule`
- **Configuration**: Requires `[postgres]` section in `aibasic.conf`
- **Examples**:
  - `10 (postgres) query all customers from postgres`
  - `20 (postgres) insert data into postgres table users`
  - `30 (postgres) execute postgres query SELECT * FROM orders WHERE status = 'pending'`
- **Usage Notes**:
  - The PostgresModule manages a connection pool automatically
  - First postgres operation initializes the module from config
  - Module instance is reused across all postgres operations
  - Use `pg.execute_query()` for simple queries with automatic connection management
  - Or use `pg.get_connection()` / `pg.release_connection()` for manual control

#### `mysql` - MySQL/MariaDB Operations (with Module)
- **Description**: MySQL/MariaDB-specific operations using connection pool module
- **Keywords**: mysql, mariadb
- **Common Libraries**: mysql.connector
- **Module**: `aibasic.modules.MySQLModule`
- **Configuration**: Requires `[mysql]` section in `aibasic.conf`
- **Examples**:
  - `10 (mysql) query all customers from mysql`
  - `20 (mysql) insert data into mysql table users`
  - `30 (mysql) execute mysql query SELECT * FROM orders WHERE status = 'active'`
  - `40 (mysql) call mysql stored procedure get_user_orders`
- **Usage Notes**:
  - The MySQLModule manages a connection pool automatically
  - First mysql operation initializes the module from config
  - Module instance is reused across all mysql operations
  - Use `mysql.execute_query()` for simple queries with automatic connection management
  - Use `mysql.execute_query_dict()` to get results as dictionaries
  - Use `mysql.call_procedure()` for calling stored procedures
  - Or use `mysql.get_connection()` / `mysql.release_connection()` for manual control

### Network Operations

#### `api` - API/REST Operations
- **Description**: HTTP requests, REST API calls, web services
- **Keywords**: api, rest, http, get, post, request, endpoint
- **Common Libraries**: requests, urllib, httpx
- **Examples**:
  - `10 (api) call the weather API`
  - `20 (api) POST data to endpoint`

#### `web` - Web Scraping
- **Description**: Extracting data from websites, HTML parsing
- **Keywords**: scrape, web page, html, beautifulsoup, parse html
- **Common Libraries**: beautifulsoup4, requests, selenium
- **Examples**:
  - `10 (web) scrape product prices from website`
  - `20 (web) extract links from page`

### Data Processing

#### `df` - DataFrame Operations
- **Description**: Pandas DataFrame manipulations, filtering, transformations
- **Keywords**: dataframe, column, row, filter, group by, merge, join
- **Common Libraries**: pandas, numpy
- **Examples**:
  - `10 (df) filter rows where age > 30`
  - `20 (df) group by country and sum sales`

#### `math` - Mathematical Operations
- **Description**: Calculations, statistical operations, numerical analysis
- **Keywords**: calculate, sum, average, mean, median, multiply, divide, statistics
- **Common Libraries**: numpy, pandas, statistics, math
- **Examples**:
  - `10 (math) calculate average revenue`
  - `20 (math) compute standard deviation`

#### `plot` - Data Visualization
- **Description**: Creating charts, graphs, and visualizations
- **Keywords**: plot, chart, graph, visualize, histogram, scatter, bar chart
- **Common Libraries**: matplotlib, seaborn, plotly
- **Examples**:
  - `10 (plot) create bar chart of sales`
  - `20 (plot) plot time series data`

### File & System Operations

#### `fs` - File System Operations
- **Description**: File reading, writing, copying, moving, directory operations
- **Keywords**: file, save, write, read, copy, move, delete, directory, folder
- **Common Libraries**: os, pathlib, shutil
- **Examples**:
  - `10 (fs) save data to file`
  - `20 (fs) copy files to backup folder`

#### `text` - Text Processing
- **Description**: String manipulation, text parsing, regular expressions
- **Keywords**: text, string, parse, regex, split, replace, extract
- **Common Libraries**: re, string
- **Examples**:
  - `10 (text) extract email addresses from text`
  - `20 (text) replace all occurrences`

#### `compress` - Compression/Archive
- **Description**: ZIP, TAR, compression and decompression operations
- **Keywords**: zip, unzip, compress, decompress, archive, tar
- **Common Libraries**: zipfile, tarfile, gzip
- **Examples**:
  - `10 (compress) compress files into zip`
  - `20 (compress) extract archive contents`

### Communication

#### `email` - Email Operations
- **Description**: Sending emails, reading mailboxes, email processing
- **Keywords**: email, send email, smtp, mailbox, imap
- **Common Libraries**: smtplib, email, imaplib
- **Examples**:
  - `10 (email) send email to customer`
  - `20 (email) read unread messages`

### Media Processing

#### `image` - Image Processing
- **Description**: Image manipulation, resizing, filtering, format conversion
- **Keywords**: image, photo, picture, resize, crop, filter
- **Common Libraries**: PIL, Pillow, opencv
- **Examples**:
  - `10 (image) resize image to 800x600`
  - `20 (image) convert PNG to JPEG`

#### `pdf` - PDF Operations
- **Description**: Reading, creating, or manipulating PDF documents
- **Keywords**: pdf, document, extract text from pdf
- **Common Libraries**: PyPDF2, pdfplumber, reportlab
- **Examples**:
  - `10 (pdf) extract text from PDF`
  - `20 (pdf) create PDF report`

### Time & Configuration

#### `date` - Date/Time Operations
- **Description**: Date parsing, formatting, calculations, time operations
- **Keywords**: date, time, datetime, timestamp, parse date, format date
- **Common Libraries**: datetime, dateutil, pandas
- **Examples**:
  - `10 (date) parse date from string`
  - `20 (date) calculate days between dates`

#### `config` - Configuration Management
- **Description**: Reading/writing configuration files (INI, YAML, TOML)
- **Keywords**: config, configuration, ini, yaml, toml, settings
- **Common Libraries**: configparser, yaml, toml
- **Examples**:
  - `10 (config) read settings from config.ini`
  - `20 (config) update YAML configuration`

### Automation & Advanced

#### `rpa` - RPA/Automation
- **Description**: UI automation, keyboard/mouse control, desktop automation
- **Keywords**: automate, click, keyboard, mouse, gui, window
- **Common Libraries**: pyautogui, selenium, playwright
- **Examples**:
  - `10 (rpa) click button on screen`
  - `20 (rpa) type text in application`

#### `ml` - Machine Learning
- **Description**: ML models, training, predictions, data science
- **Keywords**: model, train, predict, machine learning, classification, regression
- **Common Libraries**: scikit-learn, tensorflow, pytorch
- **Examples**:
  - `10 (ml) train classification model`
  - `20 (ml) predict customer churn`

#### `shell` - Shell Commands
- **Description**: Running system commands, shell scripts, process execution
- **Keywords**: execute, run command, shell, subprocess, system
- **Common Libraries**: subprocess, os
- **Examples**:
  - `10 (shell) run shell command`
  - `20 (shell) execute batch script`

#### `stream` - Stream Processing
- **Description**: Real-time data streams, message queues, event processing
- **Keywords**: stream, kafka, queue, message, event, subscribe
- **Common Libraries**: kafka-python, pika, asyncio
- **Examples**:
  - `10 (stream) consume messages from queue`
  - `20 (stream) process event stream`

#### `rabbitmq` - RabbitMQ Operations (with Module)
- **Description**: RabbitMQ message broker operations with full SSL/TLS support
- **Keywords**: rabbitmq, amqp, message broker
- **Common Libraries**: pika
- **Module**: `aibasic.modules.RabbitMQModule`
- **Configuration**: Requires `[rabbitmq]` section in `aibasic.conf`
- **Examples**:
  - `10 (rabbitmq) publish message to rabbitmq exchange my_exchange`
  - `20 (rabbitmq) consume messages from rabbitmq queue my_queue`
  - `30 (rabbitmq) declare rabbitmq exchange with type topic`
  - `40 (rabbitmq) bind rabbitmq queue to exchange with routing key`
- **Usage Notes**:
  - The RabbitMQModule manages connection automatically
  - First rabbitmq operation initializes the module from config
  - Module instance is reused across all rabbitmq operations
  - Supports SSL/TLS with optional certificate verification
  - Set `SSL_VERIFY=false` in config to skip certificate validation (dev/testing only)
  - Use `rmq.publish_message()` for publishing
  - Use `rmq.consume_messages()` for consuming (blocking)
  - Use `rmq.get_message()` for single message retrieval (non-blocking)
  - Supports all RabbitMQ exchange types: direct, topic, fanout, headers

#### `kafka` - Apache Kafka Operations (with Module)
- **Description**: Apache Kafka distributed streaming platform with full authentication support
- **Keywords**: kafka, streaming, topic, producer, consumer
- **Common Libraries**: kafka-python
- **Module**: `aibasic.modules.KafkaModule`
- **Configuration**: Requires `[kafka]` section in `aibasic.conf`
- **Examples**:
  - `10 (kafka) publish message to kafka topic events`
  - `20 (kafka) consume messages from kafka topic notifications`
  - `30 (kafka) publish batch of messages to kafka`
  - `40 (kafka) produce event to kafka with key user:123`
- **Usage Notes**:
  - The KafkaModule manages producer/consumer automatically
  - First kafka operation initializes the module from config
  - Module instance is reused across all kafka operations
  - Supports security protocols: PLAINTEXT, SASL_PLAINTEXT, SASL_SSL, SSL
  - Supports SASL mechanisms: PLAIN, SCRAM-SHA-256, SCRAM-SHA-512, GSSAPI (Kerberos)
  - Set `SSL_VERIFY=false` in config to skip certificate validation (dev/testing only)
  - Use `kafka.publish_message()` for single messages
  - Use `kafka.publish_batch()` for batch publishing
  - Use `kafka.consume_messages()` for consuming with auto-commit
  - Messages are automatically serialized/deserialized as JSON

#### `redis` - Redis Cache Operations (with Module)
- **Description**: Redis in-memory data store for caching and key-value operations
- **Keywords**: redis, cache, key-value, set, get, hash
- **Common Libraries**: redis
- **Module**: `aibasic.modules.RedisModule`
- **Configuration**: Requires `[redis]` section in `aibasic.conf`
- **Examples**:
  - `10 (redis) set redis key user:name to value "Alice" with expiration 3600 seconds`
  - `20 (redis) get value from redis key user:name`
  - `30 (redis) set redis hash user:123 with data {"name": "Bob", "age": 30}`
  - `40 (redis) get all fields from redis hash user:123`
  - `50 (redis) push tasks to redis list job_queue`
  - `60 (redis) increment redis counter page_views`
  - `70 (redis) publish message to redis channel notifications`
- **Usage Notes**:
  - The RedisModule manages connection pool automatically
  - First redis operation initializes the module from config
  - Module instance is reused across all redis operations
  - Supports authentication: no auth, password, ACL username/password (Redis 6+)
  - Supports SSL/TLS with optional certificate verification
  - Set `SSL_VERIFY=false` in config to skip certificate validation (dev/testing only)
  - Use `redis_client.set()` / `get()` for strings
  - Use `redis_client.hset()` / `hgetall()` for hashes
  - Use `redis_client.lpush()` / `rpop()` for lists (queues)
  - Use `redis_client.sadd()` / `smembers()` for sets
  - Use `redis_client.zadd()` / `zrange()` for sorted sets
  - Use `redis_client.publish()` / `subscribe()` for pub/sub
  - Use `redis_client.pipeline()` for batch operations

#### `opensearch` - OpenSearch Search and Analytics (with Module)
- **Description**: OpenSearch distributed search and analytics engine with full authentication support
- **Keywords**: opensearch, elasticsearch, search, index, query, aggregate, full-text
- **Common Libraries**: opensearch-py
- **Module**: `aibasic.modules.OpenSearchModule`
- **Configuration**: Requires `[opensearch]` section in `aibasic.conf`
- **Examples**:
  - `10 (opensearch) index document in opensearch index products`
  - `20 (opensearch) search opensearch for products matching "laptop"`
  - `30 (opensearch) bulk index 1000 documents to opensearch`
  - `40 (opensearch) aggregate opensearch sales by category`
  - `50 (opensearch) search opensearch with query {"match": {"field": "value"}}`
  - `60 (opensearch) get opensearch top 10 products by sales`
- **Usage Notes**:
  - The OpenSearchModule manages connection automatically
  - First opensearch operation initializes the module from config
  - Module instance is reused across all opensearch operations
  - Supports basic auth (username/password) and AWS IAM authentication
  - Set `VERIFY_CERTS=false` in config to skip certificate validation (dev/testing only)
  - Use `os_client.index_document()` to index a single document
  - Use `os_client.search()` for full-text search with Query DSL
  - Use `os_client.search_simple()` for simple field:value searches
  - Use `os_client.bulk_index()` for batch indexing (faster than individual)
  - Use `os_client.aggregate()` for analytics and aggregations
  - Use `os_client.get_document()` to retrieve by ID
  - Use `os_client.create_index()` / `delete_index()` for index management
  - Query DSL: `{'match': {'field': 'value'}}` for text search (analyzed)
  - Query DSL: `{'term': {'field': 'exact'}}` for exact matches (not analyzed)
  - Query DSL: `{'range': {'field': {'gte': 10, 'lte': 100}}}` for ranges
  - Query DSL: `{'bool': {'must': [...], 'should': [...], 'must_not': [...]}}` for complex queries
  - Aggregations: `{'agg_name': {'terms': {'field': 'category'}}}` for grouping
  - Aggregations: `{'agg_name': {'avg': {'field': 'price'}}}` for statistics
  - Perfect for: full-text search, log analytics, real-time analytics, e-commerce search
  - AWS OpenSearch Service: Set `USE_AWS_AUTH=true` and configure AWS credentials

### Logging & Security

#### `log` - Logging Operations
- **Description**: Application logging, log parsing, monitoring
- **Keywords**: log, logger, logging, parse log
- **Common Libraries**: logging
- **Examples**:
  - `10 (log) log error message`
  - `20 (log) parse application logs`

#### `crypto` - Cryptography
- **Description**: Encryption, decryption, hashing, security operations
- **Keywords**: encrypt, decrypt, hash, crypto, password, security
- **Common Libraries**: hashlib, cryptography, bcrypt
- **Examples**:
  - `10 (crypto) hash password`
  - `20 (crypto) encrypt sensitive data`

### Other

#### `other` - General/Other
- **Description**: General purpose operations not fitting specific categories
- **Used when**: No specific task type matches or is specified
- **Examples**:
  - `10 (other) custom logic`
  - `20 miscellaneous task`

## Configuring Modules

Some task types use AIBasic modules that require configuration in `aibasic.conf`.

### PostgreSQL Module Configuration

To use the `postgres` task type, add the following section to your `aibasic.conf`:

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

### MySQL/MariaDB Module Configuration

To use the `mysql` task type, add the following section to your `aibasic.conf`:

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

### RabbitMQ Module Configuration

To use the `rabbitmq` task type, add the following section to your `aibasic.conf`:

```ini
[rabbitmq]
HOST = localhost
PORT = 5672
VHOST = /
USERNAME = guest
PASSWORD = guest

# SSL/TLS settings (optional)
USE_SSL = false
SSL_VERIFY = true
SSL_CA_CERT = /path/to/ca_cert.pem
SSL_CLIENT_CERT = /path/to/client_cert.pem
SSL_CLIENT_KEY = /path/to/client_key.pem

# Connection settings
HEARTBEAT = 60
BLOCKED_CONNECTION_TIMEOUT = 300
CONNECTION_ATTEMPTS = 3
RETRY_DELAY = 2
```

**Important SSL/TLS Notes:**
- Set `USE_SSL=true` to enable SSL/TLS connections
- Set `SSL_VERIFY=false` to skip certificate verification (⚠️ **use only for development/testing with self-signed certificates**)
- For production, always use `SSL_VERIFY=true` with proper CA certificates
- Provide client certificates if your RabbitMQ requires client authentication

All database and messaging modules will automatically:
- Create a connection pool on first use
- Reuse connections efficiently
- Handle connection lifecycle
- Provide thread-safe operations

## Best Practices

1. **Use explicit task types for clarity**: When you know the specific operation type, specify it explicitly to help the compiler generate better code.

2. **Let auto-detection work**: For simple operations, you can omit the task type and let the compiler detect it automatically.

3. **Combine task types**: Different instructions in your program can use different task types as needed.

4. **Check for typos**: Invalid task types will be ignored with a warning, and the instruction will be auto-detected instead.

## Example Program

```aibasic
# Data pipeline with explicit task types

10 (csv) read the file sales_data.csv
20 (df) filter rows where revenue > 1000
30 (df) group by country and sum revenue
40 (math) calculate average revenue per country
50 (excel) create Excel report with results
60 (plot) create bar chart of revenue by country
70 (email) send report to manager@example.com
```

## Auto-Detection Examples

Without explicit task types, the compiler will detect them automatically:

```aibasic
10 read the file sales_data.csv              # Detected as: csv
20 filter rows where revenue > 1000          # Detected as: df
30 call the weather API                       # Detected as: api
40 create a bar chart of sales               # Detected as: plot
50 send email with the results               # Detected as: email
```
