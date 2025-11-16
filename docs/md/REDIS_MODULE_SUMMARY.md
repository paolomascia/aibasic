# Redis Module - Complete Reference

## Overview

The **Redis module** provides comprehensive Redis in-memory data store integration for caching, sessions, and real-time data.

**Module Type**: `(redis)`
**Primary Use Cases**: Caching, session storage, pub/sub, rate limiting, real-time analytics

---

## Configuration

```ini
[redis]
HOST = localhost
PORT = 6379
DB = 0
PASSWORD = secret
```

---

## Basic Operations

```basic
REM Key-Value operations
10 (redis) SET "user:123:name" "John Doe"
20 (redis) GET "user:123:name"
30 (redis) DEL "user:123:name"

REM Expiration
40 (redis) SETEX "session:abc" 3600 "user_data"

REM Lists
50 (redis) LPUSH "queue:tasks" "task1"
60 (redis) RPOP "queue:tasks"

REM Hashes
70 (redis) HSET "user:123" "name" "John" "email" "john@example.com"
80 (redis) HGET "user:123" "name"
```

---

## Module Information

- **Module Name**: RedisModule
- **Task Type**: `(redis)`
- **Dependencies**: `redis>=5.0.0`
