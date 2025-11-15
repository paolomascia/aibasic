# GCP Module - Complete Reference

## Overview

The GCP module enables comprehensive management of Google Cloud Platform resources through natural language instructions in AIbasic. It provides unified access to Compute Engine, Cloud Storage, Cloud SQL, BigQuery, Pub/Sub, Secret Manager, and more.

**Module Type:** Cloud Services
**Task Type:** `(gcp)`
**Python Implementation:** `src/aibasic/modules/gcp_module.py`
**Configuration Section:** `[gcp]` in `aibasic.conf`

## Key Features

- **Compute Engine** - VM instance lifecycle management (create, start, stop, delete)
- **Cloud Storage** - Bucket and blob operations
- **Cloud SQL** - Database instance management (MySQL, PostgreSQL, SQL Server)
- **BigQuery** - Dataset creation and SQL query execution for analytics
- **Cloud Functions** - Serverless function deployment
- **Cloud Run** - Container deployment and management
- **Pub/Sub** - Message publishing and subscription
- **Secret Manager** - Secure secrets storage and retrieval
- **Authentication** - Service Account and Application Default Credentials support
- **Multi-Region** - Deploy resources across multiple regions

## Architecture

The GCP module implements a **singleton pattern** with thread-safe initialization and lazy-loading of Google Cloud service clients using the official Google Cloud SDK for Python.

### Design Patterns

1. **Singleton Pattern** - Single instance with thread lock and initialization flag
2. **Lazy Loading** - Service clients initialized only when first accessed
3. **Configuration Management** - Reads from `aibasic.conf` with environment variable fallbacks
4. **Error Handling** - Comprehensive exception handling with descriptive messages

### Supported Google Cloud Services

- **Compute** - Compute Engine (google-cloud-compute)
- **Storage** - Cloud Storage (google-cloud-storage)
- **Database** - Cloud SQL (google-cloud-sql)
- **Analytics** - BigQuery (google-cloud-bigquery)
- **Serverless** - Cloud Functions, Cloud Run
- **Messaging** - Pub/Sub (google-cloud-pubsub)
- **Security** - Secret Manager (google-cloud-secret-manager)

## Configuration

### Required Settings

```ini
[gcp]
# Project ID (required)
PROJECT_ID = your-project-id

# Authentication
CREDENTIALS_PATH = /path/to/service-account-key.json

# Default Region and Zone
REGION = us-central1
ZONE = us-central1-a
```

### Optional Settings

```ini
[gcp]
# Compute Engine Settings
DEFAULT_MACHINE_TYPE = e2-medium
DEFAULT_DISK_SIZE = 10
DEFAULT_NETWORK = default

# Cloud Storage Settings
DEFAULT_STORAGE_CLASS = STANDARD

# Cloud SQL Settings
DEFAULT_DATABASE_VERSION = POSTGRES_14
DEFAULT_TIER = db-f1-micro

# BigQuery Settings
DEFAULT_DATASET_LOCATION = us-central1

# Resource Labeling
DEFAULT_LABELS = {"environment": "dev", "managed_by": "aibasic"}
```

### Authentication Methods

#### 1. Service Account (Recommended for Production)

Create a service account and download the JSON key:

```bash
gcloud iam service-accounts create aibasic-sa --display-name "AIBasic Service Account"
gcloud projects add-iam-policy-binding PROJECT_ID --member="serviceAccount:aibasic-sa@PROJECT_ID.iam.gserviceaccount.com" --role="roles/owner"
gcloud iam service-accounts keys create key.json --iam-account=aibasic-sa@PROJECT_ID.iam.gserviceaccount.com
```

Configure in `aibasic.conf`:

```ini
[gcp]
PROJECT_ID = your-project-id
CREDENTIALS_PATH = /path/to/key.json
```

#### 2. Application Default Credentials (For Local Development)

Use gcloud CLI authentication:

```bash
gcloud auth application-default login
```

Then configure only the project ID:

```ini
[gcp]
PROJECT_ID = your-project-id
```

## Core Operations

### Compute Engine

```aibasic
10 (gcp) create compute instance "web-server" in zone "us-central1-a" with machine_type "e2-medium"
20 (gcp) list compute instances in zone "us-central1-a"
30 (gcp) start compute instance "web-server" in zone "us-central1-a"
40 (gcp) stop compute instance "web-server" in zone "us-central1-a"
50 (gcp) delete compute instance "web-server" in zone "us-central1-a"
```

### Cloud Storage

```aibasic
10 (gcp) create storage bucket "my-bucket" in location "us-central1" with storage_class "STANDARD"
20 (gcp) list all storage buckets
30 (file) write "data.txt" with content "Hello GCP!"
40 (gcp) upload file "data.txt" to bucket "my-bucket" as "uploads/data.txt"
50 (gcp) list blobs in bucket "my-bucket"
60 (gcp) download file "uploads/data.txt" from bucket "my-bucket" to "downloaded.txt"
70 (gcp) delete storage bucket "my-bucket" with force True
```

### Cloud SQL

```aibasic
10 (gcp) create cloudsql instance "my-db" with database_version "POSTGRES_14" and tier "db-f1-micro" in region "us-central1"
20 (sleep) 120
30 (gcp) list cloudsql instances
40 (gcp) delete cloudsql instance "my-db"
```

### BigQuery

```aibasic
10 (gcp) create bigquery dataset "analytics" in location "us-central1"
20 (gcp) list bigquery datasets
30 (gcp) run bigquery query "SELECT 'Hello from BigQuery!' as message, CURRENT_TIMESTAMP() as timestamp"
```

### Pub/Sub

```aibasic
10 (gcp) create pubsub topic "events"
20 (gcp) list pubsub topics
30 (gcp) publish message "Event occurred" to topic "events" with user_id "12345"
40 (gcp) create pubsub subscription "events-sub" for topic "events"
```

### Secret Manager

```aibasic
10 (gcp) create secret "api-key" with value "secret-value-123"
20 (gcp) list secrets
30 (gcp) get secret "api-key"
```

## Complete Examples

### Example 1: Multi-Tier Web Application

```aibasic
REM Deploy complete web application infrastructure
10 (print) "Deploying multi-tier application..."

REM Create storage for application data
20 (gcp) create storage bucket "webapp-assets" in location "us-central1"
30 (gcp) create storage bucket "webapp-backups" in location "us-central1" with storage_class "NEARLINE"

REM Create Cloud SQL database
40 (gcp) create cloudsql instance "webapp-db" with database_version "POSTGRES_14" and tier "db-g1-small"

REM Create Compute Engine instances
50 (sleep) 60
60 (gcp) create compute instance "webapp-frontend" in zone "us-central1-a" with machine_type "e2-small" and labels {"tier": "web"}
70 (gcp) create compute instance "webapp-backend" in zone "us-central1-a" with machine_type "e2-medium" and labels {"tier": "app"}

REM Store secrets
80 (gcp) create secret "db-connection" with value "postgresql://user:pass@webapp-db/webapp"

90 (print) "Application deployed successfully!"
```

### Example 2: Data Pipeline

```aibasic
REM Build data processing pipeline
10 (print) "Deploying data pipeline..."

REM Create storage buckets
20 (gcp) create storage bucket "data-raw" in location "us-central1"
30 (gcp) create storage bucket "data-processed" in location "us-central1"

REM Create BigQuery datasets
40 (gcp) create bigquery dataset "raw_data" in location "us-central1"
50 (gcp) create bigquery dataset "analytics" in location "us-central1"

REM Create Pub/Sub for pipeline events
60 (gcp) create pubsub topic "pipeline-events"
70 (gcp) create pubsub subscription "pipeline-processor" for topic "pipeline-events"

REM Upload sample data
80 (file) write "sample.csv" with content "id,name,value\n1,Test,100"
90 (gcp) upload file "sample.csv" to bucket "data-raw" as "data/2025/01/sample.csv"

100 (print) "Data pipeline deployed!"
```

### Example 3: IoT Platform

```aibasic
REM Deploy IoT data collection platform
10 (print) "Deploying IoT platform..."

REM Create Pub/Sub for device telemetry
20 (gcp) create pubsub topic "device-telemetry"
30 (gcp) create pubsub subscription "telemetry-processor" for topic "device-telemetry"

REM Create storage for device data
40 (gcp) create storage bucket "iot-device-data" in location "us-central1"

REM Create BigQuery for analytics
50 (gcp) create bigquery dataset "iot_telemetry" in location "us-central1"

REM Simulate device message
60 (gcp) publish message '{"device_id": "sensor-001", "temperature": 22.5}' to topic "device-telemetry" with device_id "sensor-001"

70 (print) "IoT platform deployed!"
```

## Best Practices

### Security

1. **Use Service Accounts** for production deployments with minimal permissions
2. **Store secrets in Secret Manager** - Never hardcode credentials
3. **Enable Cloud Monitoring** and Cloud Logging
4. **Implement VPC Service Controls** for enterprise security
5. **Use IAM policies** following principle of least privilege
6. **Enable Cloud Armor** for DDoS protection
7. **Use Cloud KMS** for encryption key management

### Resource Management

1. **Use labels** for resource organization and cost tracking
2. **Implement resource quotas** to prevent overspending
3. **Monitor costs** with Budgets & Alerts
4. **Clean up unused resources** regularly
5. **Use consistent naming conventions**

### High Availability

1. **Deploy across multiple zones** for fault tolerance
2. **Use Cloud Load Balancing** for traffic distribution
3. **Configure auto-scaling** for Compute Engine
4. **Implement health checks** and monitoring
5. **Use Cloud CDN** for content delivery

### Performance

1. **Choose appropriate machine types** based on workload
2. **Use SSD persistent disks** for I/O intensive workloads
3. **Leverage Cloud CDN** for static content
4. **Use BigQuery** for large-scale analytics
5. **Implement caching** strategies

### Cost Optimization

1. **Start with smaller instance types** and scale as needed
2. **Use committed use discounts** for predictable workloads
3. **Implement auto-shutdown** for dev/test instances
4. **Use preemptible VMs** for batch processing
5. **Monitor and optimize** with Cloud Cost Management

## Error Handling

The GCP module raises `RuntimeError` exceptions with descriptive messages:

```aibasic
10 ON ERROR GOTO 100
20 (gcp) create compute instance "test-vm" in zone "invalid-zone"
30 (print) "VM created"
40 GOTO 999

100 REM Error handler
110 (print) "Error occurred during GCP operation"
120 (log) "Check zone name and permissions"

999 (print) "Script completed"
```

## Troubleshooting

### Authentication Issues

**Problem:** `DefaultAzureCredential failed to retrieve token`

**Solution:**
1. Run `gcloud auth application-default login`
2. Or configure Service Account in `aibasic.conf`
3. Verify PROJECT_ID is correct

### Permission Denied

**Problem:** `Permission denied` errors

**Solution:**
1. Verify Service Account has required IAM roles
2. Check project-level permissions
3. Enable required APIs in Cloud Console

### Resource Already Exists

**Problem:** `Resource already exists` error

**Solution:**
1. Use unique names for resources
2. Delete existing resource first
3. Add timestamps or random suffixes to names

## Integration with Other Modules

### GCP + Terraform

```aibasic
10 (terraform) apply terraform configuration
20 (sleep) 60
30 (gcp) list compute instances in zone "us-central1-a"
```

### GCP + BigQuery + CSV

```aibasic
10 (csv) read file "sales-data.csv" into data
20 (gcp) create bigquery dataset "sales" in location "us-central1"
30 (gcp) load data into bigquery table "sales.transactions"
```

### GCP + Pub/Sub + Email

```aibasic
10 (gcp) create pubsub subscription "alerts-sub" for topic "system-alerts"
20 (gcp) pull messages from subscription "alerts-sub"
30 (email) send alert email with message content
```

## Module API Reference

### Class: GCPModule

**Location:** `src/aibasic/modules/gcp_module.py`

#### Properties

- `credentials` - GCP authentication credentials (lazy-loaded)
- `compute_client` - Compute Engine client
- `storage_client` - Cloud Storage client
- `sql_admin_client` - Cloud SQL client
- `bigquery_client` - BigQuery client
- `functions_client` - Cloud Functions client
- `run_client` - Cloud Run client
- `pubsub_publisher` - Pub/Sub publisher client
- `pubsub_subscriber` - Pub/Sub subscriber client
- `secretmanager_client` - Secret Manager client

#### Methods

##### Compute Engine

- `compute_instance_create(name, zone, machine_type, ...)` - Create VM instance
- `compute_instance_list(zone)` - List instances
- `compute_instance_start(name, zone)` - Start instance
- `compute_instance_stop(name, zone)` - Stop instance
- `compute_instance_delete(name, zone)` - Delete instance

##### Cloud Storage

- `storage_bucket_create(name, location, storage_class)` - Create bucket
- `storage_bucket_list()` - List buckets
- `storage_bucket_delete(name, force)` - Delete bucket
- `storage_upload_file(bucket, source, destination)` - Upload file
- `storage_download_file(bucket, source, destination)` - Download file
- `storage_list_blobs(bucket, prefix)` - List blobs

##### Cloud SQL

- `cloudsql_instance_create(name, database_version, tier, region)` - Create instance
- `cloudsql_instance_list()` - List instances
- `cloudsql_instance_delete(name)` - Delete instance

##### BigQuery

- `bigquery_dataset_create(dataset_id, location)` - Create dataset
- `bigquery_dataset_list()` - List datasets
- `bigquery_query(query)` - Execute SQL query

##### Pub/Sub

- `pubsub_topic_create(topic_id)` - Create topic
- `pubsub_topic_list()` - List topics
- `pubsub_publish(topic_id, message, **attributes)` - Publish message
- `pubsub_subscription_create(subscription_id, topic_id)` - Create subscription

##### Secret Manager

- `secret_create(secret_id, value)` - Create secret
- `secret_get(secret_id, version)` - Get secret value
- `secret_list()` - List secrets

##### Utility

- `get_project_info()` - Get project information

## Dependencies

```
google-cloud-compute>=1.14.0
google-cloud-storage>=2.10.0
google-cloud-sql>=1.6.0
google-cloud-bigquery>=3.11.0
google-cloud-functions>=1.13.0
google-cloud-run>=0.9.0
google-cloud-pubsub>=2.18.0
google-cloud-secret-manager>=2.16.0
google-auth>=2.23.0
```

## Additional Resources

- **Google Cloud Python SDK:** https://cloud.google.com/python/docs/reference
- **Google Cloud Console:** https://console.cloud.google.com
- **gcloud CLI:** https://cloud.google.com/sdk/gcloud
- **Google Cloud Architecture:** https://cloud.google.com/architecture
- **Pricing Calculator:** https://cloud.google.com/products/calculator
- **Example File:** `examples/example_gcp.aib` (22 complete examples)

## Version History

- **v1.0** (2025-01-15) - Initial release
  - Compute Engine management
  - Cloud Storage operations
  - Cloud SQL management
  - BigQuery dataset and query operations
  - Pub/Sub messaging
  - Secret Manager integration
  - Service Account and ADC authentication
  - Multi-region support

---

**Module:** GCP (Module #26)
**Task Types:** 47 total (gcp is task type #47)
**Total Modules:** 26
