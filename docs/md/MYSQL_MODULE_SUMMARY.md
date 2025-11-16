# MySQL Module - Complete Reference

## Overview

The **MySQL module** provides comprehensive MySQL/MariaDB database integration with connection pooling and transaction support.

**Module Type:** `(mysql)`
**Primary Use Cases:** Relational databases, web applications, data storage

---

## Configuration

```ini
[mysql]
HOST = localhost
PORT = 3306
DATABASE = mydb
USER = root
PASSWORD = secret
CHARSET = utf8mb4
```

---

## Basic Operations

```basic
10 (mysql) SELECT * FROM products WHERE price > 100
20 (mysql) INSERT INTO orders (customer_id, total) VALUES (123, 299.99)
30 (mysql) UPDATE inventory SET stock = stock - 1 WHERE product_id = 456
```

---

## Module Information

- **Module Name**: MySQLModule
- **Task Type**: `(mysql)`
- **Dependencies**: `mysql-connector-python>=8.0.33`
