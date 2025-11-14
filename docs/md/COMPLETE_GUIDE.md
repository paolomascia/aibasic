# AIBasic v1.0 - Complete Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Language Syntax](#language-syntax)
4. [Task Types (36)](#task-types)
5. [Modules (14)](#modules)
6. [Control Flow](#control-flow)
7. [Examples](#examples)
8. [Compilation Process](#compilation-process)

---

## Introduction

**AIBasic** is a revolutionary natural-language programming language that compiles plain English instructions into optimized Python code using LLM technology.

### Key Features

- ✅ **Natural Language Syntax** - Write code in plain English
- ✅ **14 Integrated Modules** - Database, messaging, storage, networking
- ✅ **36 Task Types** - From data processing to automation
- ✅ **Advanced Control Flow** - Jumps, loops, error handling, subroutines
- ✅ **AI-Powered Compilation** - LLM translates intent to code
- ✅ **Production Ready** - Generates clean, optimized Python

### What's New in v1.0

1. **Subroutines (CALL/RETURN)** - Reusable code blocks
2. **Error Handling (ON ERROR GOTO)** - Robust exception management
3. **Function-Based Dispatch** - Each line = separate function
4. **3 New Modules** - MongoDB, S3, SSH
5. **36 Task Types** - Expanded capabilities

---

## Quick Start

### Installation

```bash
git clone https://github.com/your-org/aibasic.git
cd aibasic
pip install -r requirements.txt
```

### Your First Program

Create `hello.aib`:

```aibasic
10 print "Hello, AIBasic!"
20 set name to "World"
30 print "Hello," and name
```

Compile and run:

```bash
python src/aibasic/aibasicc.py -c aibasic.conf -i hello.aib -o hello.py
python hello.py
```

Output:
```
Hello, AIBasic!
Hello, World
```

---

## Language Syntax

### Program Structure

```
<line_number> <instruction in natural language>
```

- **Line numbers**: Positive integers (10, 20, 30...)
- **Instructions**: Plain English commands
- **Comments**: Lines starting with `#`

### Examples

```aibasic
10 set x to 5
20 multiply x by 2 and store in result
30 if result is greater than 5 print "Large"
40 read file "data.csv" into dataset
50 filter dataset where age > 18
```

### Task Type Hints (Optional)

```aibasic
10 (csv) read file "data.csv"
20 (postgres) query database "SELECT * FROM users"
30 (ssh) execute command "uptime" on remote server
```

---

## Task Types

AIBasic supports **36 task types** for different operations:

### Data Operations
- `csv` - CSV file operations
- `excel` - Excel spreadsheet operations
- `json` - JSON data handling
- `xml` - XML parsing and generation
- `df` - DataFrame operations (pandas)

### Databases
- `postgres` - PostgreSQL operations (module)
- `mysql` - MySQL/MariaDB operations (module)
- `mongodb` - MongoDB NoSQL operations (module)
- `cassandra` - Cassandra operations (module)
- `db` - Generic database operations

### Messaging & Streaming
- `rabbitmq` - RabbitMQ messaging (module)
- `kafka` - Apache Kafka (module)
- `stream` - Stream processing

### Caching & Search
- `redis` - Redis cache operations (module)
- `opensearch` - OpenSearch/Elasticsearch (module)

### Storage & Files
- `s3` - S3/MinIO object storage (module)
- `fs` - File system operations
- `compress` - File compression (module)
- `text` - Text file operations
- `pdf` - PDF generation/parsing

### Networking
- `api` - REST API calls (module)
- `web` - Web scraping
- `ssh` - SSH remote operations (module)
- `email` - Email sending (module)

### Security
- `vault` - HashiCorp Vault secrets (module)
- `crypto` - Cryptography operations

### Processing
- `math` - Mathematical operations
- `plot` - Data visualization
- `ml` - Machine learning
- `image` - Image processing

### Other
- `date` - Date/time operations
- `log` - Logging
- `config` - Configuration
- `rpa` - RPA/automation
- `shell` - Shell commands
- `other` - General operations

---

## Modules

AIBasic includes **14 production-ready modules**:

### 1. PostgreSQL Module

```aibasic
10 (postgres) connect to database "mydb"
20 (postgres) execute query "SELECT * FROM users WHERE age > 18"
30 (postgres) insert record into users table
40 (postgres) close connection
```

**Configuration** (`aibasic.conf`):
```ini
[postgres]
HOST = localhost
PORT = 5432
DATABASE = mydb
USERNAME = user
PASSWORD = pass
```

### 2. MySQL/MariaDB Module

```aibasic
10 (mysql) connect to database "customers"
20 (mysql) query "SELECT name, email FROM users"
30 (mysql) update users set status = 'active'
```

### 3. MongoDB Module

```aibasic
10 (mongodb) connect to collection "products"
20 (mongodb) find documents where price > 100
30 (mongodb) insert document with name "Product A"
40 (mongodb) aggregate pipeline for sales analysis
```

### 4. Cassandra Module

```aibasic
10 (cassandra) connect to keyspace "analytics"
20 (cassandra) query "SELECT * FROM events WHERE date > '2025-01-01'"
30 (cassandra) insert data into events table
```

### 5. Redis Module

```aibasic
10 (redis) set key "user:1000" to value "John Doe"
20 (redis) get value from key "user:1000"
30 (redis) set cache with expiration 3600 seconds
40 (redis) increment counter "visits"
```

### 6. RabbitMQ Module

```aibasic
10 (rabbitmq) publish message "Order #123" to queue "orders"
20 (rabbitmq) consume messages from queue "notifications"
30 (rabbitmq) declare exchange "events" type fanout
```

### 7. Apache Kafka Module

```aibasic
10 (kafka) produce message to topic "user-events"
20 (kafka) consume messages from topic "logs"
30 (kafka) commit offset for consumer group
```

### 8. OpenSearch Module

```aibasic
10 (opensearch) index document in "products" index
20 (opensearch) search for "laptop" in all fields
30 (opensearch) aggregate sales by category
```

### 9. Email Module

```aibasic
10 (email) send email to "user@example.com" with subject "Welcome"
20 (email) send email with attachment "report.pdf"
30 (email) send HTML email with template
```

### 10. S3/MinIO Module

```aibasic
10 (s3) upload file "data.csv" to bucket "my-bucket"
20 (s3) download object "report.pdf" from bucket
30 (s3) list objects in bucket with prefix "2025/"
40 (s3) generate presigned URL for object
```

### 11. SSH Module

```aibasic
10 (ssh) connect to server "192.168.1.100"
20 (ssh) execute command "uptime" on remote server
30 (ssh) transfer file "local.txt" to "/remote/path/file.txt"
40 (ssh) download file from remote "/var/log/app.log"
```

### 12. Vault Module

```aibasic
10 (vault) read secret from path "secret/api-keys"
20 (vault) write secret to path "secret/db-creds"
30 (vault) delete secret at path "secret/old-key"
```

### 13. Compression Module

```aibasic
10 (compress) compress folder "reports" into "archive.zip"
20 (compress) extract archive "data.tar.gz" to "output/"
30 (compress) create password-protected zip with password "secret"
```

### 14. REST API Module

```aibasic
10 (api) GET request to "https://api.example.com/users"
20 (api) POST data to endpoint with JSON payload
30 (api) authenticate with bearer token
40 (api) upload file to API endpoint
```

---

## Control Flow

### 1. Jumps (GOTO)

**Unconditional Jump:**
```aibasic
10 set x to 5
20 goto 50
30 print "This is skipped"
50 print "Jumped here!"
```

**Conditional Jump:**
```aibasic
10 set counter to 0
20 print counter
30 increment counter by 1
40 if counter is less than 5 jump to line 20
50 print "Done!"
```

### 2. Error Handling (ON ERROR GOTO)

```aibasic
10 set x to 10
20 set y to 0
30 on error goto 100
40 divide x by y and store in result
50 print "Result:" and result
60 goto 200

100 print "ERROR:" and _last_error
110 print "At line:" and _last_error_line
120 print "Recovering..."

200 print "Program complete"
```

**Error Variables:**
- `_last_error` - Exception object
- `_last_error_line` - Line number where error occurred
- `_error_handler` - Current error handler line

### 3. Subroutines (CALL/RETURN)

**Simple Subroutine:**
```aibasic
10 print "Main program"
20 set x to 5
30 call 1000
40 print "x after subroutine:" and x
50 goto 999

1000 print "In subroutine"
1010 multiply x by 2
1020 return

999 print "End"
```

**Nested Subroutines:**
```aibasic
10 call 100
20 print "Done"

100 print "Subroutine A"
110 call 200
120 return

200 print "Subroutine B"
210 return
```

**Subroutine Library Pattern:**
```aibasic
10 set a to 12
20 set b to 8
30 call 1000
40 print "GCD:" and gcd_result
50 goto 9999

# GCD Subroutine
1000 set x to a
1010 set y to b
1020 if y equals 0 jump to line 1060
1030 set temp to x modulo y
1040 set x to y
1050 set y to temp and goto 1020
1060 set gcd_result to x
1070 return

9999 print "End"
```

---

## Examples

### Example 1: Data Processing

```aibasic
10 (csv) read file "sales.csv" into data
20 (df) filter data where revenue > 1000
30 (df) group data by region and calculate sum of revenue
40 (df) sort by revenue descending
50 (excel) save result to "sales_report.xlsx"
60 print "Report generated!"
```

### Example 2: Database ETL

```aibasic
10 (postgres) connect to database "source_db"
20 (postgres) query "SELECT * FROM orders WHERE date > '2025-01-01'"
30 (df) transform data by calculating total_price
40 (mongodb) connect to collection "processed_orders"
50 (mongodb) insert documents from transformed data
60 print "ETL complete"
```

### Example 3: Web Scraping with Error Handling

```aibasic
10 on error goto 100
20 (web) navigate to "https://example.com/products"
30 (web) extract product names and prices
40 (csv) save scraped data to "products.csv"
50 print "Scraping successful"
60 goto 999

100 print "ERROR during scraping:" and _last_error
110 print "Saving partial results..."
120 (csv) save scraped data to "products_partial.csv"

999 print "Program end"
```

### Example 4: Server Automation

```aibasic
10 set servers to list "192.168.1.10" "192.168.1.11" "192.168.1.12"
20 set index to 0

30 if index >= length of servers jump to line 999
40 get server at index from servers
50 print "Connecting to" and server

60 on error goto 200
70 (ssh) connect to server
80 (ssh) execute command "df -h"
90 (ssh) execute command "uptime"
100 print "Server" and server and "OK"
110 goto 300

200 print "ERROR on server" and server
210 print _last_error

300 increment index by 1
310 goto 30

999 print "All servers checked"
```

### Example 5: Message Queue Processing

```aibasic
10 (rabbitmq) connect to queue "tasks"
20 set processed to 0

30 (rabbitmq) consume message from queue "tasks"
40 if no message available jump to line 999
50 print "Processing message:" and message

60 on error goto 200
70 (api) POST message to "https://api.example.com/process"
80 increment processed by 1
90 goto 30

200 print "Failed to process message"
210 (rabbitmq) publish message to queue "failed-tasks"
220 goto 30

999 print "Processed" and processed and "messages"
```

---

## Compilation Process

### How It Works

1. **Parse Instructions**: Each line parsed into components
2. **Detect Control Flow**: Identify jumps, calls, error handlers
3. **Generate Functions**: Each line becomes a Python function
4. **LLM Compilation**: Natural language → Python code via LLM
5. **Code Assembly**: Functions assembled with dispatch loop
6. **Output Generation**: Complete Python program

### Example Compilation

**Input (AIBasic):**
```aibasic
10 set counter to 0
20 print counter
30 increment counter by 1
40 if counter < 3 jump to line 20
50 print "Done!"
```

**Output (Python):**
```python
# === Generated by AIBasic Compiler ===

def _line_10():
    global _next_line, counter
    # 10 set counter to 0
    counter = 0
    if _next_line is None:
        _next_line = 20

def _line_20():
    global _next_line, counter
    # 20 print counter
    print(counter)
    if _next_line is None:
        _next_line = 30

def _line_30():
    global _next_line, counter
    # 30 increment counter by 1
    counter += 1
    if _next_line is None:
        _next_line = 40

def _line_40():
    global _next_line, counter
    # 40 if counter < 3 jump to line 20
    _aibasic_jump_condition = (counter < 3)
    if _aibasic_jump_condition:
        _next_line = 20
    if _next_line is None:
        _next_line = 50

def _line_50():
    global _next_line
    # 50 print "Done!"
    print("Done!")

def main():
    global _next_line, counter
    _current_line = 10
    _next_line = None

    _line_functions = {
        10: _line_10,
        20: _line_20,
        30: _line_30,
        40: _line_40,
        50: _line_50,
    }

    while _current_line is not None:
        _next_line = None
        line_func = _line_functions.get(_current_line)
        if line_func:
            line_func()
        _current_line = _next_line

if __name__ == '__main__':
    main()
```

### Compiler Features

- ✅ Function-based dispatch (O(1) lookup)
- ✅ Automatic variable management
- ✅ Try-except blocks for error handling
- ✅ Call stack for subroutines
- ✅ Type inference and validation
- ✅ Optimized code generation

---

## Configuration

Create `aibasic.conf` with module settings:

```ini
[llm]
API_URL = https://api.openai.com/v1/chat/completions
API_TOKEN = your-api-key-here
MODEL = gpt-4o-mini

[postgres]
HOST = localhost
PORT = 5432
DATABASE = mydb
USERNAME = user
PASSWORD = pass

[mongodb]
CONNECTION_STRING = mongodb://localhost:27017
DATABASE = mydb

[redis]
HOST = localhost
PORT = 6379

[s3]
AWS_ACCESS_KEY_ID = your-access-key
AWS_SECRET_ACCESS_KEY = your-secret-key
BUCKET_NAME = my-bucket

[ssh]
HOST = server.example.com
PORT = 22
USERNAME = admin
KEY_FILE = ~/.ssh/id_rsa
```

---

## Best Practices

### 1. Code Organization

```aibasic
# Main program: lines 10-990
10 print "Program start"
...
990 goto 9999

# Subroutine 1: lines 1000-1990
1000 # Calculate total
...
1990 return

# Subroutine 2: lines 2000-2990
2000 # Validate input
...
2990 return

# End: line 9999
9999 print "Program end"
```

### 2. Error Handling

```aibasic
10 on error goto 900
20 # ... risky operations ...
90 goto 999

900 print "ERROR:" and _last_error
910 # ... cleanup ...
920 goto 999

999 print "End"
```

### 3. Task Type Hints

```aibasic
# GOOD - explicit task types
10 (csv) read file "data.csv"
20 (df) filter where age > 18
30 (postgres) save to database

# OK - auto-detection
10 read file "data.csv"
20 filter where age > 18
30 save to database
```

---

## Troubleshooting

### Common Issues

**1. Module not found**
```bash
pip install psycopg2-binary  # for PostgreSQL
pip install pymongo           # for MongoDB
pip install paramiko          # for SSH
```

**2. API Key Error**
- Check `aibasic.conf` has valid `[llm]` section
- Verify API_TOKEN is correct

**3. Compilation Fails**
- Check line numbers are unique
- Verify jump targets exist
- Ensure RETURN is only in subroutines

---

## Resources

- **GitHub**: https://github.com/your-org/aibasic
- **Documentation**: `/docs/`
- **Examples**: `/examples/`
- **Module Guide**: `MODULES_GUIDE.md`
- **Task Types**: `TASK_TYPES.md`
- **Jumps Guide**: `JUMPS_GUIDE.md`

---

## License

AIBasic v1.0
© 2025 - All Rights Reserved
