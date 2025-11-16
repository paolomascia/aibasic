# REST API Module - Complete Reference

## Overview

The **REST API module** provides comprehensive HTTP REST API client capabilities for API integration.

**Module Type**: `(restapi)` or `(api)`
**Primary Use Cases**: API integration, webhooks, microservices communication, third-party services

---

## Configuration

```ini
[restapi]
BASE_URL = https://api.example.com
AUTH_METHOD = bearer
BEARER_TOKEN = your_token
TIMEOUT = 30
```

---

## Basic Operations

```basic
REM GET request
10 (restapi) GET "https://api.example.com/users"

REM POST request
20 (restapi) POST "https://api.example.com/users" with data {"name": "John", "email": "john@example.com"}

REM PUT request
30 (restapi) PUT "https://api.example.com/users/123" with data {"name": "John Updated"}

REM DELETE request
40 (restapi) DELETE "https://api.example.com/users/123"

REM With headers
50 (restapi) GET "https://api.example.com/data" with headers {"Authorization": "Bearer token123", "Content-Type": "application/json"}
```

---

## Module Information

- **Module Name**: RestAPIModule
- **Task Type**: `(restapi)`, `(api)`
- **Dependencies**: `requests>=2.31.0`
