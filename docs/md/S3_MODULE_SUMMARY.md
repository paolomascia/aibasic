# S3/MinIO Module - Complete Reference

## Overview

The **S3 module** provides comprehensive S3-compatible object storage integration (AWS S3, MinIO, DigitalOcean Spaces).

**Module Type**: `(s3)`
**Primary Use Cases**: File storage, backups, media hosting, data lakes, static websites

---

## Configuration

```ini
[s3]
AWS_ACCESS_KEY_ID = your_key
AWS_SECRET_ACCESS_KEY = your_secret
BUCKET_NAME = my-bucket
REGION = us-east-1
ENDPOINT_URL = http://minio:9000  # For MinIO
```

---

## Basic Operations

```basic
10 (s3) upload file "report.pdf" to "documents/report.pdf"
20 (s3) download "documents/report.pdf" to "local_report.pdf"
30 (s3) list objects in bucket with prefix "documents/"
40 (s3) delete object "documents/old_file.pdf"
50 (s3) create bucket "new-bucket"
```

---

## Module Information

- **Module Name**: S3Module
- **Task Type**: `(s3)`
- **Dependencies**: `boto3>=1.26.0`
