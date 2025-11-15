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

#### `mongodb` - MongoDB NoSQL Operations (with Module)
- **Description**: Document-oriented NoSQL database with flexible schema and powerful query capabilities
- **Keywords**: mongodb, nosql, document database, mongo, collection, bson
- **Common Libraries**: pymongo
- **Module**: `aibasic.modules.MongoDBModule`
- **Configuration**: Requires `[mongodb]` section in `aibasic.conf`
- **Examples**:
  - `10 (mongodb) insert document into mongodb collection users`
  - `20 (mongodb) find documents in mongodb where age greater than 25`
  - `30 (mongodb) update mongodb users set status to active`
  - `40 (mongodb) aggregate mongodb orders group by customer`
  - `50 (mongodb) create index on mongodb users email field`
- **Usage Notes**:
  - The MongoDBModule manages connections and pooling automatically
  - First mongodb operation initializes the module from config
  - Module instance is reused across all mongodb operations
  - Use `mongo.insert_one()` / `insert_many()` for insertions
  - Use `mongo.find()` / `find_one()` for queries
  - Use `mongo.update_one()` / `update_many()` for updates
  - Use `mongo.delete_one()` / `delete_many()` for deletions
  - Use `mongo.aggregate()` for aggregation pipelines
  - Use `mongo.create_index()` for index management
  - Supports SSL/TLS with `TLS_ALLOW_INVALID_CERTIFICATES=true` for self-signed certs
  - ObjectId fields automatically converted to strings in results

#### `cassandra` - Apache Cassandra NoSQL Operations (with Module)
- **Description**: Distributed NoSQL database with high scalability and availability
- **Keywords**: cassandra, nosql, cql, distributed database, wide column, time series
- **Common Libraries**: cassandra-driver
- **Module**: `aibasic.modules.CassandraModule`
- **Configuration**: Requires `[cassandra]` section in `aibasic.conf`
- **Examples**:
  - `10 (cassandra) execute cql query on cassandra`
  - `20 (cassandra) insert data into cassandra table users`
  - `30 (cassandra) select from cassandra where key equals value`
  - `40 (cassandra) batch insert multiple rows to cassandra`
- **Usage Notes**:
  - The CassandraModule manages cluster connections automatically
  - Supports multiple contact points for high availability
  - Supports consistency levels: ONE, QUORUM, ALL, LOCAL_QUORUM, etc.
  - Use `cass.execute()` for CQL queries
  - Use `cass.execute_prepared()` for better performance with repeated queries
  - Use `cass.execute_batch()` for atomic multi-row operations
  - Use `cass.insert()` / `select()` / `update()` / `delete()` for CRUD
  - Supports SSL/TLS with `SSL_VERIFY=false` for self-signed certs
  - TTL supported for automatic data expiration

#### `clickhouse` - ClickHouse OLAP Database Operations (with Module)
- **Description**: High-performance column-oriented database for real-time analytics and OLAP
- **Keywords**: clickhouse, olap, analytics, column database, time series, data warehouse
- **Common Libraries**: requests (HTTP interface)
- **Module**: `aibasic.modules.ClickHouseModule`
- **Configuration**: Requires `[clickhouse]` section in `aibasic.conf`
- **Examples**:
  - `10 (clickhouse) query SELECT * FROM events WHERE event_date = today()`
  - `20 (clickhouse) insert into events values from dataframe`
  - `30 (clickhouse) create table analytics with MergeTree engine`
  - `40 (clickhouse) batch insert 100000 rows from dataframe`
  - `50 (clickhouse) create materialized view for aggregations`
  - `60 (clickhouse) optimize table events final`
- **Usage Notes**:
  - The ClickHouseModule uses HTTP interface (port 8123 by default)
  - Extremely fast for analytical queries on large datasets
  - Use `clickhouse.query()` for SELECT queries (returns list of dicts)
  - Use `clickhouse.query_df()` to get results as pandas DataFrame
  - Use `clickhouse.insert()` for single/small inserts
  - Use `clickhouse.batch_insert()` for high-performance bulk loading
  - Use `clickhouse.create_table()` with appropriate table engine
  - Supports compression: LZ4, ZSTD for network efficiency
  - Use partitioning for time-series data: `PARTITION BY toYYYYMM(date)`
  - Use `ORDER BY` to define primary key (required for MergeTree)
  - Materialized views for pre-aggregated data
  - Excellent for: web analytics, time-series data, log aggregation, data warehousing

#### `timescaledb` - TimescaleDB Time-Series Database Operations (with Module)
- **Description**: PostgreSQL extension optimized for time-series data with hypertables, continuous aggregates, and compression
- **Keywords**: timescaledb, time-series, hypertable, iot, sensor, metrics, monitoring, analytics
- **Common Libraries**: psycopg2-binary
- **Module**: `aibasic.modules.TimescaleDBModule`
- **Configuration**: Requires `[timescaledb]` section in `aibasic.conf`
- **Examples**:
  - `10 (timescaledb) create hypertable sensor_data with time column time`
  - `20 (timescaledb) insert sensor readings into timescaledb hypertable`
  - `30 (timescaledb) time bucket query with 15 minute intervals`
  - `40 (timescaledb) create continuous aggregate for hourly summaries`
  - `50 (timescaledb) add compression policy compress after 7 days`
  - `60 (timescaledb) add retention policy keep data for 30 days`
  - `70 (timescaledb) fill gaps in time-series using LOCF method`
  - `80 (timescaledb) query to dataframe with aggregations`
- **Usage Notes**:
  - The TimescaleDBModule uses PostgreSQL with TimescaleDB extension
  - Hypertables automatically partition time-series data into chunks
  - Use `tsdb.create_hypertable()` to convert regular PostgreSQL table
  - Use `tsdb.time_bucket_query()` for time-based aggregations (15min, 1hour, etc.)
  - Use `tsdb.create_continuous_aggregate()` for auto-updating materialized views
  - Use `tsdb.add_compression_policy()` for automatic compression (90%+ storage reduction)
  - Use `tsdb.add_retention_policy()` for automatic old data deletion
  - Use `tsdb.fill_gaps()` to fill missing data points (LOCF, linear interpolation, NULL)
  - Use `tsdb.query_to_dataframe()` to get results as pandas DataFrame
  - Supports space partitioning for multi-dimensional data (e.g., partition by sensor_id)
  - Chunk intervals: 1 hour (high-frequency), 1 day (medium), 1 week (low-frequency)
  - 100% PostgreSQL compatible - all PostgreSQL features work seamlessly
  - Compression is transparent - compressed data is still queryable
  - Continuous aggregates refresh automatically based on policies
  - Perfect for: IoT sensor data, application metrics, financial data, server monitoring, logs

#### `aws` - AWS Cloud Services Integration (with Module)
- **Description**: Comprehensive Amazon Web Services integration for cloud-native applications
- **Keywords**: aws, s3, dynamodb, sqs, sns, lambda, cloud, serverless, secrets manager, cloudwatch
- **Common Libraries**: boto3
- **Module**: `aibasic.modules.AWSModule`
- **Configuration**: Requires `[aws]` section in `aibasic.conf`
- **Examples**:
  - `10 (aws) upload file data.csv to S3 bucket my-bucket`
  - `20 (aws) download from S3 bucket my-bucket key data.csv`
  - `30 (aws) put item into DynamoDB table users with data`
  - `40 (aws) get item from DynamoDB table users with key`
  - `50 (aws) send message to SQS queue orders-queue`
  - `60 (aws) receive messages from SQS queue orders-queue`
  - `70 (aws) publish to SNS topic with message`
  - `80 (aws) invoke Lambda function my-function with payload`
  - `90 (aws) get secret from Secrets Manager db-credentials`
  - `100 (aws) put CloudWatch metric OrderCount value 150`
- **Usage Notes**:
  - The AWSModule provides unified access to 10+ AWS services
  - Supports production AWS and LocalStack for local development
  - Use `aws.s3_upload_file()` / `s3_download_file()` for S3 operations
  - Use `aws.dynamodb_put_item()` / `get_item()` / `query()` / `scan()` for DynamoDB
  - Use `aws.sqs_send_message()` / `receive_messages()` for SQS queuing
  - Use `aws.sns_publish()` for pub/sub notifications
  - Use `aws.lambda_invoke()` for serverless function execution
  - Use `aws.secrets_get_secret()` for secure credential retrieval
  - Use `aws.cloudwatch_put_metric()` for custom monitoring metrics
  - Automatic credential management: IAM roles, environment variables, or config file
  - Built-in retry logic and connection pooling
  - LocalStack endpoint: http://localhost:4566 (credentials: test/test)
  - S3: Upload, download, list, delete, presigned URLs, server-side encryption
  - DynamoDB: NoSQL database with primary keys, GSI, queries, scans
  - SQS: Message queuing with visibility timeout, long polling, dead-letter queues
  - SNS: Topic-based pub/sub with multiple subscribers
  - Lambda: Sync (RequestResponse) and async (Event) invocation
  - Perfect for: Cloud-native apps, serverless architectures, microservices, data pipelines, event-driven systems

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

#### `ssh` - SSH Remote Server Operations (with Module)
- **Description**: Secure Shell for remote server management, command execution, and file transfer
- **Keywords**: ssh, remote, server, sftp, command, execute, transfer, tunnel, shell
- **Common Libraries**: paramiko
- **Module**: `ssh_module.SSHModule`
- **Examples**:
  - `10 (ssh) execute command on remote server via ssh`
  - `20 (ssh) transfer file to remote server via sftp`
  - `30 (ssh) download file from remote server`
  - `40 (ssh) run shell script on remote host`
  - `50 (ssh) create ssh tunnel to server`
- **Module Features**:
  - Password and SSH key authentication
  - SFTP file upload/download
  - Interactive shell sessions
  - Batch command execution
  - Port forwarding and tunneling
  - Jump host/bastion support
  - Host key verification options

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

#### `teams` - Microsoft Teams Integration
- **Description**: Send messages, alerts, and adaptive cards to Microsoft Teams channels
- **Keywords**: teams, microsoft teams, teams message, teams alert, teams notification
- **Common Libraries**: requests (for webhooks), Microsoft Graph API
- **Examples**:
  - `10 (teams) send message to channel with title "Pipeline Complete"`
  - `20 (teams) send alert with severity "warning"`
  - `30 (teams) send status card with details`
  - `40 (teams) send notification with facts`

#### `slack` - Slack Integration
- **Description**: Send messages, alerts, blocks, and files to Slack channels
- **Keywords**: slack, slack message, slack alert, slack notification, slack blocks
- **Common Libraries**: requests (for webhooks), Slack API
- **Examples**:
  - `10 (slack) send message to channel "#general"`
  - `20 (slack) send alert with severity "error"`
  - `30 (slack) send status message with fields`
  - `40 (slack) upload file to channel`
  - `50 (slack) send block message with sections`

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

#### `elasticsearch` - Elasticsearch Search and Analytics Engine (with Module)
- **Description**: Elasticsearch distributed search and analytics engine for full-text search and real-time data
- **Keywords**: elasticsearch, search, index, query, aggregate, full-text, logs
- **Common Libraries**: elasticsearch
- **Module**: `aibasic.modules.ElasticsearchModule`
- **Configuration**: Requires `[elasticsearch]` section in `aibasic.conf`
- **Examples**:
  - `10 (elasticsearch) create elasticsearch index products with mappings`
  - `20 (elasticsearch) index document in elasticsearch index products`
  - `30 (elasticsearch) search elasticsearch for products matching "laptop"`
  - `40 (elasticsearch) search with query {"match": {"description": "wireless"}}`
  - `50 (elasticsearch) range query where price between 50 and 100`
  - `60 (elasticsearch) bool query with must and filter conditions`
  - `70 (elasticsearch) aggregate by category with average price`
  - `80 (elasticsearch) bulk index 10000 documents from dataframe`
  - `90 (elasticsearch) update elasticsearch document by id`
  - `100 (elasticsearch) delete elasticsearch documents matching query`
  - `110 (elasticsearch) search elasticsearch and return as dataframe`
- **Usage Notes**:
  - The ElasticsearchModule manages connection automatically
  - First elasticsearch operation initializes the module from config
  - Module instance is reused across all elasticsearch operations
  - Supports basic auth (username/password) and API key authentication
  - API keys recommended for production (more secure than passwords)
  - Set `VERIFY_CERTS=false` in config to skip SSL verification (dev/testing only)
  - Use `es.create_index()` to create index with mappings and settings
  - Use `es.index_document()` to index a single document
  - Use `es.bulk_index()` for batch indexing (high performance)
  - Use `es.search()` for full-text search with Query DSL
  - Use `es.search_df()` to get search results as pandas DataFrame
  - Use `es.get_document()` / `update_document()` / `delete_document()` for CRUD
  - Use `es.count()` to count documents matching query
  - Use `es.delete_by_query()` / `update_by_query()` for bulk operations
  - Query DSL: `{'match': {'field': 'value'}}` for text search (analyzed)
  - Query DSL: `{'term': {'field': 'exact'}}` for exact matches on keyword fields
  - Query DSL: `{'range': {'price': {'gte': 50, 'lte': 100}}}` for ranges
  - Query DSL: `{'bool': {'must': [...], 'filter': [...], 'should': [...]}}` for complex queries
  - Query DSL: `{'fuzzy': {'name': {'value': 'keybord', 'fuzziness': 'AUTO'}}}` for typo-tolerant search
  - Query DSL: `{'wildcard': {'name': {'value': '*mouse*'}}}` for wildcard patterns
  - Query DSL: `{'multi_match': {'query': 'wireless keyboard', 'fields': ['name', 'description']}}` for multi-field search
  - Aggregations: `{'categories': {'terms': {'field': 'category'}}}` for grouping
  - Aggregations: `{'avg_price': {'avg': {'field': 'price'}}}` for statistics
  - Aggregations: `{'price_histogram': {'histogram': {'field': 'price', 'interval': 50}}}` for distributions
  - Aggregations: `{'logs_over_time': {'date_histogram': {'field': 'timestamp', 'fixed_interval': '1h'}}}` for time-series
  - Perfect for: Application search, log analytics, e-commerce search, real-time analytics, business intelligence

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
