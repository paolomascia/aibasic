# OpenSearch Module - Complete Reference

## Overview

The **OpenSearch module** provides comprehensive OpenSearch integration for full-text search and analytics.

**Module Type**: `(opensearch)`
**Primary Use Cases**: Full-text search, log analytics, application search, data exploration

---

## Configuration

```ini
[opensearch]
HOSTS = https://localhost:9200
USERNAME = admin
PASSWORD = admin
INDEX_NAME = documents
```

---

## Basic Operations

```basic
10 (opensearch) index document {"title": "Guide", "content": "..."} into "docs"
20 (opensearch) search in "docs" for "machine learning"
30 (opensearch) update document with id "123" set {"status": "published"}
40 (opensearch) delete document "123" from "docs"
```

---

## Module Information

- **Module Name**: OpenSearchModule
- **Task Type**: `(opensearch)`
- **Dependencies**: `opensearch-py>=2.0.0`, `boto3>=1.26.0`
