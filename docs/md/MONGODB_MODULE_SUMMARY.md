# MongoDB Module - Complete Reference

## Overview

The **MongoDB module** provides comprehensive MongoDB NoSQL database integration for document storage and querying.

**Module Type**: `(mongodb)`
**Primary Use Cases**: Document storage, flexible schemas, JSON data, real-time analytics

---

## Configuration

```ini
[mongodb]
CONNECTION_STRING = mongodb://localhost:27017
DATABASE = mydb
COLLECTION = documents
```

---

## Basic Operations

```basic
10 (mongodb) insert document {"name": "John", "age": 30} into "users"
20 (mongodb) find documents in "users" where {"age": {"$gt": 18}}
30 (mongodb) update documents in "users" set {"status": "active"} where {"name": "John"}
40 (mongodb) delete documents from "users" where {"age": {"$lt": 18}}
```

---

## Module Information

- **Module Name**: MongoDBModule
- **Task Type**: `(mongodb)`
- **Dependencies**: `pymongo>=4.0.0`
