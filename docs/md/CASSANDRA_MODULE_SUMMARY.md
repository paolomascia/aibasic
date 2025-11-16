# Cassandra Module - Complete Reference

## Overview

The **Cassandra module** provides comprehensive Apache Cassandra NoSQL database integration.

**Module Type**: `(cassandra)`
**Primary Use Cases**: Distributed NoSQL, high availability, time-series data, write-heavy applications

---

## Configuration

```ini
[cassandra]
HOSTS = localhost
PORT = 9042
KEYSPACE = analytics
```

---

## Basic Operations

```basic
10 (cassandra) execute query "CREATE TABLE users (id UUID PRIMARY KEY, name TEXT)"
20 (cassandra) insert into users values "uuid(), 'John Doe'"
30 (cassandra) SELECT * FROM users WHERE id = uuid
40 (cassandra) batch insert multiple records
```

---

## Module Information

- **Module Name**: CassandraModule
- **Task Type**: `(cassandra)`
- **Dependencies**: `cassandra-driver>=3.28.0`
