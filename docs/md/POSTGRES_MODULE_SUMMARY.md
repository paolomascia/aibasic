# PostgreSQL Module - Complete Reference

## Overview

The **PostgreSQL module** provides comprehensive PostgreSQL database integration with connection pooling, transactions, and advanced SQL features.

**Module Type:** `(postgres)`
**Primary Use Cases:** Relational data storage, complex queries, ACID transactions, data integrity

---

## Key Features

- SQL query execution
- Parameterized queries (SQL injection protection)
- Transaction support (BEGIN, COMMIT, ROLLBACK)
- Connection pooling
- Batch operations
- JSON/JSONB support
- Full-text search
- Stored procedures

---

## Configuration

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

---

## Basic Operations

```basic
REM Execute query
10 (postgres) SELECT * FROM users WHERE age > 18

REM Insert data
20 (postgres) INSERT INTO users (name, email, age) VALUES ('John', 'john@example.com', 30)

REM Update data
30 (postgres) UPDATE users SET age = 31 WHERE name = 'John'

REM Delete data
40 (postgres) DELETE FROM users WHERE id = 123

REM Transaction
50 (postgres) BEGIN TRANSACTION
60 (postgres) INSERT INTO accounts (id, balance) VALUES (1, 1000)
70 (postgres) UPDATE accounts SET balance = balance - 100 WHERE id = 1
80 (postgres) COMMIT
```

---

## Module Information

- **Module Name**: PostgresModule
- **Task Type**: `(postgres)`
- **Dependencies**: `psycopg2-binary>=2.9.9`

---

*For more examples, see [example_postgres.aib](../../examples/example_postgres.aib)*
